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
    TYPE_WORKER  = 2
    TYPE_SHIFT   = 1
    FIRST_SHIFT  = '10:00'

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
        if len(schedules) > 99 or type_id > 9:
            raise ValueError

        schedule_id = 0
        shifts = []

        for this_schedule in schedules:
            slots = self.flatten_time_ranges(this_schedule)
            prefix = type_id * self.TYPE_OFFSET + schedule_id * self.ID_OFFSET
            shifts += [prefix + shift for shift in slots]
            schedule_id += 1

        return shifts

    # Take set of time ranges in human readable format
    # and return list of ranges in integer format
    # Used both to create shifts and worker availability
    #
    # Creating UID which expresses info like weekday + time
    def flatten_time_ranges(self, work_hours):
        DOW = 'MTWRFSU'
        day_id = 0
        flat = []

        for day in DOW:
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


    def combine_adjacent_slots(self):
        pass

    def text_to_minutes(self, time):
        t = self.timecheck(time)
        hr = int(t.split(':')[0])
        m = int(t.split(':')[1])
        return (60 * hr + m)

    def minutes_to_text(self, num):
        hr = num // 60
        m = num % 60
        return("%s:%s" % (hr, m))

    def round_off(self, num, interval):
        return ((num // interval) * interval)

    # Expecting:
    #   hh
    #   hh pm/am
    #   hhpm/am
    #   hh:mm
    #   hh:mm pm/am
    #   hh:mmpm/am
    #
    # Returning hh:mm
    def timecheck(self, time):
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
        return range(start_in_minutes, end_in_minutes, interval)


