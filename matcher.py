# This file will take in schedule information
# then match open shifts to available work hours
from scheduler import ScheduleInterpreter
import json

# Given two collections and a comparison lambda
# Make pairs of all matches
# Returns list of pairs (tuples)
def make_pairs(left, right, get_key):
    left_keys = map(get_key, left)
    right_keys = map(get_key, right)

    list_of_lists = [[] for w in range(len(left_keys))]
    join_zone = dict(zip(left_keys, list_of_lists))
    pairs = []

    for w in range(len(left)):
        join_zone[left_keys[w]].append(left[w])

    for w in range(len(right)):
        for each_item in join_zone.get(right_keys[w],[]):
            pairs.append( (each_item, right[w]) )

    return pairs


def match_workers_to_shifts(worker_slots, shift_slots):
    pairs = make_pairs(worker_slots, shift_slots,
        lambda slot: slot % ScheduleInterpreter.ID_OFFSET)

    return pairs


def main():
    file = open('docs/xuMakerSpringAvailability.txt','r')
    print(file)
    schedules = json.loads(file.read())
    all_day_every_day = {
        'M': '10:00-17:00',
        'T': '10:00-17:00',
        'W': '10:00-17:00',
        'R': '10:00-17:00',
        'F': '10:00-17:00',
        'S': '10:00-17:00',
        'U': '10:00-17:00'
    }

    scheduler = ScheduleInterpreter()
    w_slots = scheduler.generate_shifts(ScheduleInterpreter.TYPE_WORKER, *schedules)
    s_slots = scheduler.generate_shifts(ScheduleInterpreter.TYPE_SHIFT, \
        all_day_every_day, all_day_every_day)

    pairs = match_workers_to_shifts(w_slots, s_slots)

    # Because our bipartite matcher requires sequential vertices
    # We sort all slots and index them to map their values to their indices
    all_slots = sorted(s_slots + w_slots)
    value_map = dict(zip(all_slots, range(len(all_slots))))

    print(len(all_slots))
    print(len(pairs))
    for p in pairs:
        print("%s %s 0" % (value_map[p[0]], value_map[p[1]]))


if __name__ == '__main__':
    main()
