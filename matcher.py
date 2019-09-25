# This file will take in schedule information
# then match open shifts to available work hours
from scheduler import ScheduleInterpreter
from subprocess import check_output
import json

# Given two collections and a lambda to retrieve key
# Make pairs of all matches using psuedo hash-join on equality
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


# High-level readable function to join two sets of UIDs
def match_workers_to_shifts(worker_slots, shift_slots):
    # Join by portion of UID (number) representing a time of day
    pairs = make_pairs(worker_slots, shift_slots,
        lambda slot: slot % ScheduleInterpreter.ID_OFFSET)

    return pairs

def save_matchings_to_file(matchings, all_combined, value_map, output_file_name):
    output_file = open(output_file_name, 'w')
    # Start file formatting for graph solver
    # First two lines will be #Vertices and #Edges
    output_data = [str(len(all_combined)), str(len(matchings))]
    # Followed by lines of x y 0, i.e. the vertices of edge and its weight
    output_data += ["%s %s 0" % (value_map[m[0]], value_map[m[1]])
            for m in matchings]
    output_file.write('\n'.join(output_data))
    # End file formatting
    output_file.close()

def main():
    file = open('docs/xuMakerSpringAvailability.txt','r')
    worker_availability = json.loads(file.read())
    worker1_shifts = worker2_shifts = {
        'M': '10:00-17:00',
        'T': '10:00-17:00',
        'W': '10:00-17:00',
        'R': '10:00-17:00',
        'F': '10:00-17:00',
        'S': '10:00-17:00',
        'U': '10:00-17:00'
    }

    # Convert given schedules into UIDs to be matched by shared time
    scheduler = ScheduleInterpreter()
    workers = ScheduleInterpreter.TYPE_WORKER
    shifts = ScheduleInterpreter.TYPE_SHIFT
    w_slots = scheduler.generate_shifts(workers, *worker_availability)
    s_slots = scheduler.generate_shifts(shifts, worker1_shifts, worker2_shifts)
    # Because our bipartite matcher requires sequential vertices
    # We sort all slots and index them to map their values to their indices
    all_slots = sorted(all_left + all_right)
    value_map = dict(zip(all_slots, range(len(all_slots))))

    # Generate "edges" in a description of a bipartite graph
    pairs = match_workers_to_shifts(w_slots, s_slots)
    save_matchings_to_file(pairs, all_slots, value_map './docs/graph')

    # Use graph theory to find best shift coverage with "Job Matching" problem
    solver_args = ['-f', './docs/graph', '--max']
    solver_output = check_output(['./match_bipartite_graph'] + solver_args).split('\n')

    # Convert "solved" graph's matchings (chosen edges) into
    # Readable shifts for (TODO:calendar_feature and) a table for managers
    tmp_index = solver_output[0].find(':')
    num_edges = int( solver_output[0][tmp_index + len(" "):])
    starting_line = 2
    matched_edges = solver_output[starting_line:starting_line + num_edges]

    # Revert graph vertices to slots as UIDs
    reverse_map = dict(zip(value_map.values(), value_map.keys()))
    matched_shifts = [(reverse_map[me[0]], reverse_map[me[1]]) \
            for me in matched_edges]

    # TODO: Find the bug that causes an empty line to be in output
    table = scheduler.create_master_schedule(matched_shifts)


if __name__ == '__main__':
    main()
