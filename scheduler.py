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
TESTING = True


class ScheduleInterpreter():
    SHIFT_LENGTH = 15
    TYPE_WORKER  = 1
    TYPE_SHIFT   = 2
    FIRST_SHIFT  = '10:00'
    LAST_SHIFT   = '17:00'
    DOW          = 'MTWRFSU'

    def __init__(self, start=FIRST_SHIFT, end=LAST_SHIFT, shift_len=SHIFT_LENGTH):
        """ Keeping some design choices constant for compatibility, i.e. minimal breaking changes """
        self.FIRST_SHIFT = start
        self.LAST_SHIFT = end
        self.SHIFT_LENGTH = shift_len


    @staticmethod
    def assign_id(schedules):
        # Attempt to control ID for UIDs
        # TODO: Refactor ID scheme
        return ScheduleInterpreter.index_elements(*schedules)


    # TODO: simplify by forcing military time
    def create_time_slots(self, start_inclusive, end_exclusive, military_time=False):
        """ Given 13:00 and 16:50, return 13*60, 13*60 +15, ..., 16:30 """
        # TODO: Debate "duplication of code" versus readability

        interval = self.SHIFT_LENGTH
        starting_minute = self.text_to_minutes(start_inclusive)
        ending_minute = self.text_to_minutes(end_exclusive)

        if not military_time \
            and (starting_minute < self.text_to_minutes(self.FIRST_SHIFT)):
            # Must be PM work if earlier than first shift
            starting_minute += (12 * 60)

        if ending_minute <= starting_minute:
            # Timecheck can't handle assumptions made in
            # human-readable time ranges without more context
            # this is a workaround to insure 24-hour upheld
            ending_minute += (12 * 60)

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
        # TODO: Rewrite as a map.reduce function using slot meta-data
        columns_in_schedule = range(len(self.DOW) * num_concurrent_shifts)

        # To export nicely as CSV file, make a ROW-MAJOR table
        # Note: since table is small, performance gains from locality negligible
        table = [[None for col in columns_in_schedule]
                    for row in daily_shifts_as_rows]


        # At this point assigned_shifts = [(w_UID, s_UID), ...]
        # TODO: retwrite relevant pieces to use slot meta-data
        row_col_UID_tuples = self.append_indices_to_values(*assigned_shifts)
        tuples_with_nice_names = lambda row, col, UID: \
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
    def fill_table(self, table, time_slots):
        


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



    # Make slots from provided availability schedules
    def generate_shifts(self, type_id, *schedules):
        


    @staticmethod
    def get_DOW(slot_UID):
        # Get Day of Week (DOW)
        # '101A1015' -> A
        return (slot_UID.day_in_cycle)

    @staticmethod
    def get_ID(slot_UID):
        # ID refers to which of a type is described, e.g. ID 2 may be the third worker
        # '1AB31015' -> AB
        return (slot_UID.ID)

    @staticmethod
    def get_TOD(slot_UID):
        # Get Time of Day (TOD)
        # '2005ABCD' -> ABCD
        return (slot_UID.time_of_day)

    @staticmethod
    def get_type(slot_UID):
        # 'A0911015' -> A
        return (slot_UID.type)


    ### Utility methods for public ###

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

    # TODO: Completely rework this timecheck(time) method from scratch
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


class Slot():
    """
    The UID used in previous versions of the project redesigned in OOP fashion for cleaner function and reference
    """

    def __init__(
            self,
            day_in_cycle,
            identifier,
            nice_name,
            time_of_day,
            timeslot_class,
            cycle_size=7,
            weight=0
        ):

        # WARNING: Direct access to attributes restricts one to these names when dependents use code?
        self.day_in_cycle = day_in_cycle
        self.ID = identifier
        self.match_ID = -1
        # TODO: self.index = 0 # Idea to fill in later
        self.name = nice_name
        self.time_of_day = time_of_day
        self.type = timeslot_class
        self.cycle_size = cycle_size
        self.weight = weight

        self.ordered_repr = [
            self.name,
            self.weight,
            self.type,
            self.ID,
            self.day_in_cycle,
            self.time_of_day
        ]

        if TESTING:
            assert(self.validation_check_passes())


    def __repr__(self):
        raw_repr = self.ordered_repr
        clear_repr = map(str(), raw_repr)
        full_repr = f"{super().__repr__()}: {' '.join(clear_repr)}"

        return(full_repr)

    def __str__(self):
        return(str(self.name))

    def __int__(self):
        repr_for_comparisons = f"{self.day_in_cycle}{self.time_of_day}"
        just_time_and_day = int(repr_for_comparisons)

        return just_time_and_day

    def __eq__(self, other):
        return(int(self) == int(other))


    def __ne__(self, other):
        return(int(self) != int(other))

    def __gt__(self, other):
        return(int(self) > int(other))

    def __lt__(self):
        return(int(self) < int(other))

    def validation_check_passes():
        return False

    def make_many_slots(tuples_of_init_args):
        # Opportunity for Vectorization
        return []














