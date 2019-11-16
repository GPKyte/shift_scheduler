# Some m work shifts need fulfilled by some n employees
# Available shifts may overlap, i.e. two employees during same time
# This problem is reduced by simplifying the available time
# into unique slots for both workers and shifts
#
# Next, we relate worker's availability blocks to the shifts as pairs
# This results in a well-known graph theory problem of Matching
# with a bi-partite graph where shifts are vertices and ability
# to fulfill them is shown in pairs.
#
# We then use an implementation of a Matching solver to
# make our life easy, so we export a file of pairs and meta data,
# execute the matcher and collect the results which can be
# collected and reinterpretted as human readable shifts assigned
# the original n workers. Ideally all shifts will be matched
# and each worker has a reasonable shift

class ScheduleInterpreter():
    SHIFT_LENGTH = 15
    TYPE_WORKER  = 1
    TYPE_SHIFT   = 2
    FIRST_SHIFT  = '10:00'
    LAST_SHIFT   = '17:00'
    DOW          = 'MTWRFSU'

    TYPE_OFFSET  = 10000000
    ID_OFFSET    =   100000
    DOW_OFFSET   =    10000

    # Creates UID for every possible time slot in week_availability
    # The UID format is 'T##DMMMM':
    #   T = Type of time slot (shift versus worker)
    #   # = ID of time slot (first worker's id is 00)
    #   D = Day of the week
    #   M = Minutes from 0-1439 (24 * 60 - 1) of given day
    def generate_shifts(self, type_id, *schedules):
        # Enforce Data integrity of UID with simple check
        if len(schedules) > 99 or type_id > 9:
            raise ValueError

        shifts = []
        # TODO: Finish designating responsibility of ID tracking
        named_schedules = self.assign_id(schedules)

        for schedule_id in named_schedules.keys():
            this_schedule = named_schedules[schedule_id]
            slots = self.flatten_time_ranges(this_schedule)

            prefix = type_id * self.TYPE_OFFSET + schedule_id * self.ID_OFFSET
            shifts += [prefix + shift for shift in slots]

        return shifts

    # Attempt to control ID for UIDs
    @staticmethod
    def assign_id(schedules):
        return ScheduleInterpreter.index_elements(*schedules)

    # Avoiding loop of fxn calls with use of *args
    @staticmethod
    def index_elements(*args):
        keys = range(len(args))
        return dict(zip(keys, args))

    # Take set of time ranges in human readable format
    # and return list of ranges in integer format
    # Used both to create shifts and worker availability
    #
    # Creating UID which expresses info like weekday + time
    def flatten_time_ranges(self, work_hours):
        day_id = 0
        flat = []

        # TODO: decrease indentation, yikes.
        # TODO: Replace UID with OOP solution
        # TODO: Add weight to edges by storing length of consecutive shift availability
        #       This will prioritize longer shifts in a max weight graph
        for day in self.DOW:
            ranges = []
            todays_slots = []

            if work_hours.get(day):
                ranges += work_hours.get(day).split(', ')

            for time_range in ranges:
                try:
                    start, end = time_range.split('-')
                except ValueError:
                    print("Could not parse this time range: ", time_range)
                    raw_input()
                    continue

                todays_slots += self.create_time_slots(start, end)

            prefix = day_id * self.DOW_OFFSET
            day_id += 1
            flat += [prefix + slot for slot in todays_slots]

        return flat

    # Master Schedule is a fancy name for a regular table
    # This will show for each day of the week
    # Who is assigned to each slot of the day
    # But there's a catch, some or all days have n >= 2 shifts
    # i.e. multiple employees are scheduled to cover each day
    # and this needs clear representation in the table
    #
    # Given list of UID pairs, create table
    # Where workers' UID are in each cell and indexed by matching shift UID
    # Pairs are necessary only because of concurrent employees
    def create_master_schedule(self, assigned_shifts, worker_names={}):
        WORKER_UID = 0
        SHIFT_UID = 1
        # This will become easiest if will assume there is room for n shifts
        # in every possible time slot. Once we find n, we simply create a
        # 2d table with appropriate headers and lack of matched shifts
        # will take care of any discrepancies from this assumption

        # Find n # of shifts by relying on information in UID
        # Because ID is one order higher than time and DOW,
        # Max UID will give the number of shifts concurrently scheduled
        last_shift = int(max([s[SHIFT_UID] for s in assigned_shifts]))
        num_concurrent_shifts = self.get_ID(last_shift) + 1 # 0-indexed ID

        # Create headers
        headers = []
        for day in self.DOW:
            for x in range(1, num_concurrent_shifts + 1):
                suffix = str(x) if x > 1 else ''
                headers.append(day + suffix)

        # TODO: Make a build table method?
        # TODO: Clean these rambling comments
        # What's the table size?
        # Well, as for columns we have N * DOW
        # and for shifts we have 24 hr * 60 min/hr / 15 min/interval
        # But more precisely, we have as many DOW as needed (<=7)
        # And we only have time slots between the first and last shift
        max_daily_shifts = range(len(
            self.create_time_slots(self.FIRST_SHIFT, self.LAST_SHIFT)))
        total_weekly_coverage = range(len(self.DOW) * num_concurrent_shifts)

        # Because we will join as CSV most-likely
        # create a column by row table (choose row then column)!!!!!!!!!!!!!!
        # Note: BC table is small, performance gains from locality negligible
        table = [[None for col in total_weekly_coverage] for row in max_daily_shifts]

        # TODO: Better yet, make one function call and return the indices appended to data
        indices = self.append_indices_to_values(num_concurrent_shifts, *assigned_shifts)
        table = self.fill_table(table, indices, worker_names)
        master = [headers] + table # headers must be list to append row to top

        return master

    # Takes a sufficiently sized table
    #   then plots values by their provided indices
    #   while converting values based on given mapping if such mapping exists
    # Returns same table address; this is a mutator function
    def fill_table(self, table, index_value_tuples, value_mapping={}):
        for assignment in index_value_tuples:
            column, row, default_value = assignment
            key = self.get_ID(default_value)
            cell_value = value_mapping.get(key, default_value)

            try:
                # Note the ordering of row and column!!!
                table[row][column] = cell_value

            except IndexError as ie:
                print("Cell at Row: %s, Column: %s is not in range:") % (row, column)
                print("Value %s, Table:\n %s") % (cell_value, table)
                raise ie

        return table

    # Generate index for each UID and Slot pair
    # Location in final table is dependent upon:
    # 1) Time of day,   2) Day of week,    3) Concurrent employee #, and
    #       4) Offset in minutes from the start of the workday
    # TODO: simplify table by oversizing and parsing later, i.e. remove (4)
    # Return (x_index, y_index, UID) tuples
    def append_indices_to_values(self, num_subcolumns, *value_location_pairs):
        SHIFT_UID = self.TYPE_SHIFT - 1
        WORKER_UID = self.TYPE_WORKER - 1
        y_offset = self.text_to_minutes(self.FIRST_SHIFT)
        indices = []

        # TODO: Make this whole method easier to read and find bugs?

        for pair in value_location_pairs:
            slot_UID = pair[SHIFT_UID]
            x = self.get_DOW(slot_UID) * num_subcolumns + self.get_ID(slot_UID)
            y = (self.get_TOD(slot_UID) - y_offset) // self.SHIFT_LENGTH
            indices.append( (x, y, pair[WORKER_UID]) )

        return indices

    # TODO: Make these methods static (class methods instead of instance methods)
    # Series of UID-specific helper functions to avoid duplication and error
    # UID format: T##DMMMM, note that int is required input
    # Get Time of Day (TOD)
    @staticmethod
    def get_TOD(slot_UID):
        # '2005ABCD' -> ABCD
        return (slot_UID % ScheduleInterpreter.DOW_OFFSET)

    # Get Day of Week (DOW)
    @staticmethod
    def get_DOW(slot_UID):
        # '101A1015' -> A
        return (slot_UID % ScheduleInterpreter.ID_OFFSET // ScheduleInterpreter.DOW_OFFSET)

    @staticmethod
    def get_ID(slot_UID):
        # '1AB31015' -> AB
        return (slot_UID % ScheduleInterpreter.TYPE_OFFSET // ScheduleInterpreter.ID_OFFSET)

    @staticmethod
    def get_type(slot_UID):
        # 'A0911015' -> A
        return (slot_UID // ScheduleInterpreter.TYPE_OFFSET)
    # End series of GET UID-info helpers

    # TODO: combine_adjacent_slots() for Calendar feature and/or weighted edges
    def combine_adjacent_slots(self):
        pass

    # Given std format of "hh:mm" return the int mmmm
    @staticmethod
    def text_to_minutes(time):
        t = ScheduleInterpreter.timecheck(time)
        hr = int(t.split(':')[0])
        m = int(t.split(':')[1])
        return (60 * hr + m)

    @staticmethod
    def minutes_to_text(num):
        hr = num // 60
        m = num % 60
        return("%s:%s" % (hr, m))

    @staticmethod
    def round_off(num, interval):
        return ((num // interval) * interval)

    # TODO: Completely rework this timecheck(time) mehtod from scratch
    # Expecting any of the following formats:
    #   hh
    #   hh pm/am
    #   hhpm/am
    #   hh:mm
    #   hh:mm pm/am
    #   hh:mmpm/am
    #
    # Returning hh:mm
    @staticmethod
    def timecheck(time):
        tmp = None
        is_past_noon = False
        # Do not change order of operations carelessly
        # 1
        if ' ' in time: # Remove spaces to simplify cases
            time = ''.join(time.split(' '))

        # 2
        if 'pm' in time:
            tmp = time[:time.find('pm')] # Remove suffix
            is_past_noon = True
        elif 'am' in time:
            tmp = time[:time.find('am')]
        else:
            tmp = time

        # 3
        if ':' in tmp:
            result = tmp
        else:
            result = tmp + ':00'

        # 4
        if is_past_noon:
            hr, m = result.split(':')
            hr_proper = int(hr) % 12 + 12
            result = "%s:%s" % (hr_proper, m)

        return result


    # TODO: Debate "duplication of code" versus readability
    # Given 13:00 and 16:50, return 13*60, 13*60 +15, ..., 16:30
    def create_time_slots(self, start_inclusive, end_exclusive):
        interval = self.SHIFT_LENGTH
        starting_minute = self.text_to_minutes(start_inclusive)
        ending_minute = self.text_to_minutes(end_exclusive)

        if ending_minute <= starting_minute:
            # Timecheck can't handle assumptions made in
            # human-readable time ranges without more context
            # this is a workaround to insure 24-hour upheld
            ending_minute += (12 * 60)
        if starting_minute < self.text_to_minutes(self.FIRST_SHIFT):
            # Must be PM work if earlier than first shift
            starting_minute += (12 * 60)

        start_in_minutes = self.round_off(starting_minute, interval)
        end_in_minutes = self.round_off(ending_minute, interval)

        return(range(start_in_minutes, end_in_minutes, interval))

