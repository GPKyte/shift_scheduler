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


    def convert_availability_to_slots(self, avail, weight_policy=None):
        slots = []

        def convert_old_DOW_format(avail):
            formatted_avail = {}
            """
            Note to maintainers:
            incoming data may have old DOW format
            Use the following to change to day_in_cycle standard """
            for key in avail.keys():
                try:
                    new_key = self.DOW.index(key)
                    formatted_avail[new_key] = avail[key]
                except ValueError:
                    # Key not found, but this is fine
                    formatted_avail[key] = avail[key]

            return formatted_avail

        def get_times_of_day_for_whole_cycle(avail):
            times_grouped_by_day = {}

            for key in avail.keys():
                some_times_of_day = []

                # Convert timeranges into one list of time_of_day values
                try:
                    day_in_cycle = int(key)
                except ValueError:
                    break # key was not an int and thus not relevant

                # Format looks like "10am-11:30am, 1:00pm-5:00pm"
                for timerange in avail[day_in_cycle].split(', '):
                    start, end = timerange.split("-")
                    military_time_on = True

                    some_times_of_day += \
                        create_time_slots(start, end, military_time_on)

                times_grouped_by_day[key] = some_times_of_day

            return times_grouped_by_day

        weight = 0
        nice_name = avail["Name"]
        identifier = avail["id"]
        timeslot_class = avail["type"]
        avail = convert_old_DOW_format(avail)
        times_grouped_by_day = get_times_of_day_for_whole_cycle(avail)

        for key in times_grouped_by_day.keys():
            # Make real slots from present data
            day_in_cycle = int(key)

            for TOD in times_grouped_by_day[key]:
                slots += Slot(
                    day_in_cycle,
                    identifier,
                    nice_name,
                    TOD,
                    timeslot_class,
                    weight
                )

        return slots


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


    def create_master_schedule(self, assigned_shifts):
        w_slot = 0
        slots = [pair[w_slot] for pair in assigned_shifts]

        return self.make_table(slots)

    # Headers in top row,
    def make_table(self, slots):
        def slot_to_col(slot):
            return ({"day": slot.day_in_cycle, "id": slot.ID})

        # Note: intentionally make and prune excess of rows to simplify code
        rows = range(0, hours_in_day * 60, self.SHIFT_LENGTH)
        columns = sorted(set(map(slot_to_col(), slots)))
        headers = ["Time of Day"] + [c["day"] for c in columns]

        # To export nicely as CSV file, make a ROW-MAJOR table
        # Note: since table is small, performance gains from locality negligible
        table = [[minutes_to_text(row)] + [None for col in columns]
                    for row in rows]

        for slot in slots:
            row_index = slot.time_of_day // self.SHIFT_LENGTH
            col_index = columns.find(slot_to_col(slot))
            table[row_index][col_index] = str(slot)

        self.prune_empty_lists_from(table) # Remove empty rows

        return headers + table


    # Make slots from provided availability schedules
    def make_slots(self, type_id, *schedules):
        shifts = []
        schedules = self.assign_id(schedules)

        for key in schedules.keys():
            availability = schedules[key]
            availability["id"] = key
            availability["type"] = type_id

            shifts += self.convert_availability_to_slots(availability)

        return shifts


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
            but is originally intended for row-removal """
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
    The UID used in previous versions of the project
    redesigned in OOP fashion for cleaner function and referencing """

    def __init__(
            self,
            day_in_cycle,
            identifier,
            nice_name,
            time_of_day,
            timeslot_class,
            weight=0
        ):

        # WARNING: Direct access to attributes restricts one to these names when dependents use code?
        self.day_in_cycle = day_in_cycle
        self.ID = identifier
        self.match_ID = -1 # Delete if possible
        # TODO: self.index = 0 # Idea to fill in later
        self.name = nice_name
        self.time_of_day = time_of_day
        self.type = timeslot_class
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














