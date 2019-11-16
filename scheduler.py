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


    def append_indices_to_values(self, num_subcolumns, *value_location_pairs):
        """
        WARNING: BUG-PRONE
        Generate index for each UID and Slot pair
        Location in final table is dependent upon:
            1) Time of day,   2) Day of week,    3) Concurrent employee #, and
            4) Offset in minutes from the start of the workday

        Return (x_index, y_index, UID) tuples
        """
        SHIFT_UID = self.TYPE_SHIFT - 1 # 0-index
        WORKER_UID = self.TYPE_WORKER - 1 # 0-index
        y_offset = self.text_to_minutes(self.FIRST_SHIFT)
        indices = []

        # TODO: simplify table by oversizing and parsing later, i.e. remove (4)
        # TODO: Make this whole method easier to read and find bugs?

        for pair in value_location_pairs:
            slot_UID = pair[SHIFT_UID]
            x = self.get_DOW(slot_UID) * num_subcolumns + self.get_ID(slot_UID)
            y = (self.get_TOD(slot_UID) - y_offset) // self.SHIFT_LENGTH

            indices.append( (x, y, pair[WORKER_UID]) )

        return indices


    @staticmethod
    def assign_id(schedules):
        # Attempt to control ID for UIDs
        # TODO: Refactor ID scheme
        return ScheduleInterpreter.index_elements(*schedules)

    # TODO: combine_adjacent_slots() for Calendar feature and/or weighted edges
    def combine_adjacent_slots(self):
        pass


    def create_time_slots(self, start_inclusive, end_exclusive, military_time=False):
        """ Given 13:00 and 16:50, return 13*60, 13*60 +15, ..., 16:30 """
        # TODO: Debate "duplication of code" versus readability

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



    def create_master_schedule(self, assigned_shifts, worker_names={}, num_concurrent_shifts=2):
        """
        Master Schedule is a fancy name for a regular table
        This will show for each day of the week
        Who is assigned to each slot of the day
        But there's a catch, some or all days have n >= 2 shifts
        i.e. multiple employees are scheduled to cover each day
        and this needs clear representation in the table

        Given list of UID pairs, create table
        Where workers' UID are in each cell and indexed by matching shift UID
        Pairs are necessary only because of concurrent employees
        """
        WORKER_UID = self.TYPE_WORKER - 1 # 0-index
        SHIFT_UID = self.TYPE_SHIFT - 1 # 0-index
        hours_in_day = 24
        headers = []

        for day in self.DOW:
            for x in range(1, num_concurrent_shifts + 1):
                suffix = str(x) if x > 1 else ''
                headers.append(day + suffix)


        # Note: intentionally make and prune excess of rows to simplify code
        daily_shifts_as_rows = range(0, hours_in_day * 60, self.SHIFT_LENGTH)
        columns_in_schedule = range(len(self.DOW) * num_concurrent_shifts)

        # To export nicely as CSV file, make a ROW-MAJOR table
        # Note: since table is small, performance gains from locality negligible
        table = [[None for col in columns_in_schedule]
                    for row in daily_shifts_as_rows]

        row_col_UID_tuples = self.append_indices_to_values(num_concurrent_shifts, *assigned_shifts)
        tuples_with_nice_names = lambda (row, col, UID): \
            (row, col, worker_names.get(self.get_ID(UID), UID))

        positions_for_names = map(tuples_with_nice_names, row_col_UID_tuples)

        self.fill_table(table, positions_for_names)
        self.prune_empty_lists_from(table) # Remove empty rows

        master = [headers] + table # headers must be list to append row to top

        return master

    # Takes a sufficiently sized table
    #   then plots values by their provided indices
    #   while converting values based on given mapping if such mapping exists
    # Returns same table address; this is a mutator function
    def fill_table(self, table, index_value_tuples):
        for assignment in index_value_tuples:
            column, row, cell_value = assignment
            print(assignment)

            try:
                # Note the ordering of row and column!!!
                table[row][column] = cell_value

            except IndexError as ie:
                print("Cell at Row: %s, Column: %s is not in range:") % (row, column)
                print("Value %s, Table:\n %s") % (cell_value, table)
                raise ie

        return table


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


    @staticmethod
    def get_DOW(slot_UID):
        # Get Day of Week (DOW)
        # '101A1015' -> A
        return (slot_UID % ScheduleInterpreter.ID_OFFSET // ScheduleInterpreter.DOW_OFFSET)

    @staticmethod
    def get_ID(slot_UID):
        # ID refers to which of a type is described, e.g. ID 2 may be the third worker
        # '1AB31015' -> AB
        return (slot_UID % ScheduleInterpreter.TYPE_OFFSET // ScheduleInterpreter.ID_OFFSET)

    @staticmethod
    def get_TOD(slot_UID):
        # Get Time of Day (TOD)
        # '2005ABCD' -> ABCD
        return (slot_UID % ScheduleInterpreter.DOW_OFFSET)

    @staticmethod
    def get_type(slot_UID):
        # 'A0911015' -> A
        return (slot_UID // ScheduleInterpreter.TYPE_OFFSET)


    # Avoiding loop of fxn calls with use of *args
    @staticmethod
    def index_elements(*args):
        keys = range(len(args))
        return dict(zip(keys, args))


    @staticmethod
    def minutes_to_text(num):
        hr = num // 60
        m = num % 60
        return("%s:%s" % (hr, m))


    @staticmethod
    def prune_empty_lists_from(table):
        """
        Method results from a simplification on indexing
        Some rows should never be used and will thus be empty, remove them
        Note, this will work with either ROW/COL-MAJOR tables
            but is originally intended for row-removal
        """
        empty = [None for x in range(len(table[0]))]
        z = 0

        while z < len(table):
            if table[z] == empty:
                table.pop(z)

            else:
                z += 1

        return None

    @staticmethod
    def round_off(num, interval):
        return ((num // interval) * interval)


    # Given std format of "hh:mm" return the int mmmm
    @staticmethod
    def text_to_minutes(time):
        t = ScheduleInterpreter.timecheck(time)
        hr = int(t.split(':')[0])
        m = int(t.split(':')[1])
        return (60 * hr + m)

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
