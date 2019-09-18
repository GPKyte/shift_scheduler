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
#
# The UID format is 'T##DMMMM':
#   T = Type of time slot (shift versus worker)
#   # = ID of time slot (first worker's id is 00)
#   D = Day of the week
#   M = Minutes from 0-1439 (24 * 60 - 1) of given day

def generate_shifts(workers, shifts):
    interpreter = ScheduleInterpreter()
    type_id = 1 # For shifts
    shift_id = 0
    open_shifts = []
    
    for this_shift in shifts:
        slots = interpreter.flatten_time_ranges(this_shift)
        open_shifts += [type_id * TYPE_OFFSET + shift_id * ID_OFFSET \
                        + shift for shift in slots]
        shift_id += 1

    type_id = 2 # For workers
    worker_id = shift_id + 1
    worker_shifts = []

    for this_worker in workers:
        slots = interpreter.flatten_time_ranges(this_worker)
        worker_shifts += [type_id * TYPE_OFFSET + worker_id * ID_OFFSET \
                            + shift for shift in slots]
        worker_id += 1

class ScheduleInterpreter(self):
    DOW_OFFSET = 10**3
    SHIFT_LENGTH = 15

    # Take set of time ranges in human readable format
    # and return list of ranges in integer format
    # Used both to create shifts and worker availability
    def flatten_time_ranges(self, work_hours):
        DOW = 'MTWRFSU'
        just_times = [work_hours.get(day) for day in DOW]

        flat = []
        for i in range(len(just_times)):
            left, right = just_times[i].split('-')
            # Creating UID which expresses info like weekday + time
            flat += [i * self.DOW_OFFSET + timeblock \
                        for timeblock in create_time_range(left, right)]

        return flat


    def timecheck(t):
        # Several conditions exist for now return input
        # pm/am
        # No :mm
        # no pm, but past noon (Need context)
        return t


    # Given 13:00, 16:50. return 1300, 1315, 1330, 1345, 1400, 1415, ..., 1645
    def create_time_range(self, start_inclusive, end_exclusive):
        interval = self.SHIFT_LENGTH
        start_inclusive = timecheck(start_inclusive)
        end_exclusive = timecheck(end_inclusive)

        hr_1 = int(start_inclusive.split(':')[0])
        m_1 = int(start_inclusive.split(':')[1])
        hr_2 = int(end_exclusive.split(':')[0])
        m_2 = int(end_exclusive.split(':')[1])

        # Round off by interval
        start_in_minutes = ((hr_1 * 60 + m_1) / interval) * interval
        end_in_minutes = ((hr_2 * 60 + m_2) / interval) * interval
        
        # Converting to min for simplicity, exclude last
        return range(start_in_minutes, end_in_minutes, interval)


