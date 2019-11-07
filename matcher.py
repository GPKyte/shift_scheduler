# BREAK DOWN MAIN METHOD FOR TESTING

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


def reverse_keys_and_values(mapping):
    new_map = {}

    for key in mapping.keys():
        value = mapping[key]
        new_map[value] = key

    return new_map


# Assume ROW-MAJOR table!
def as_CSV(table):
    string_table = []
    for each_row in table:
        string_table.append(
            map(lambda entry: str(entry), each_row))

    rows = [','.join(row) for row in string_table]
    return ('\n'.join(rows))


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


def parse_graph_solution(solver_output):
        # Convert solved graph's matchings (chosen edges) into
        # Readable shifts for (TODO:calendar_feature and) a table for managers
        tmp_index = solver_output[0].find(':')
        num_edges = int( solver_output[0][tmp_index + len(" "):])
        starting_line = 2

        # This is a list of string lines with 2 numbers separated by a space
        pairs = solver_output[starting_line:starting_line + num_edges]
        str_matched_edges = [pair.split(' ') for pair in pairs]
        matched_edges = map( # need integers in table
            lambda pair: (int(pair[0]), int(pair[1])),
            str_matched_edges)

        return matched_edges


def make_matching(availability_file):
    file = open(availability_file,'r')
    worker_availability = json.loads(file.read())
    # Each time I see this I think about a quick concise generator,
    # but what if the content changes for only some days? So keep it simple
    worker1_shifts = worker2_shifts = {
        'M': '10:00-17:00',
        'T': '10:00-17:00',
        'W': '10:00-17:00',
        'R': '10:00-17:00',
        'F': '10:00-17:00',
        'S': '10:00-17:00',
        'U': '10:00-17:00'
    }

    ### CREATE SHIFTS ###
    # Convert given schedules into UIDs to be matched by shared time
    scheduler = ScheduleInterpreter()
    workers = ScheduleInterpreter.TYPE_WORKER
    shifts = ScheduleInterpreter.TYPE_SHIFT
    w_slots = scheduler.generate_shifts(workers, *worker_availability)
    s_slots = scheduler.generate_shifts(shifts, worker1_shifts, worker2_shifts)

    assignments = assign_shifts(w_slots, s_slots)

    # Map ids in UIDs to worker names
    ID_schedules = scheduler.assign_id(worker_availability)
    name_id_pairs = [(w, ID_schedules[w]['Name']) for w in ID_schedules.keys()]
    ID_names = dict(name_id_pairs)

    # TODO: Find the bug that causes an empty line to be in output
    table = scheduler.create_master_schedule(assignments, ID_names)

    output_file = open('new_schedule.csv', 'w')
    output_file.write(as_CSV(table))
    output_file.close()

    return(table)
 

# Using a graph theory solution to job matching, assign shifts by
# treating each matched shift (a shift that a worker can fulfill)
# as an edge between worker and shift. This creates a bipartite graph
def assign_shifts(w_slots, s_slots):
    # Because our bipartite matcher requires sequential vertices
    # We sort all slots and index them to map their values to their indices
    all_slots = sorted(w_slots + s_slots)
    value_map = dict(zip(all_slots, range(len(all_slots))))

    # Generate "edges" in a description of a bipartite graph
    matchings = match_workers_to_shifts(w_slots, s_slots)
    save_matchings_to_file(matchings, all_slots, value_map, './docs/graph')

    # Use graph theory to find best shift coverage with "Job Matching" problem
    solver_args = ['-f', './docs/graph', '--max']
    solver_output = check_output(['./match_bipartite_graph'] + solver_args).split('\n')
    selected_edges = parse_graph_solution(solver_output)

    # Revert graph vertices to slots as UIDs
    reverse_map = reverse_keys_and_values(value_map)
    try:
        assigned_shifts = [(reverse_map[se[0]], reverse_map[se[1]]) \
            for se in selected_edges]
    except KeyError as ke:
        print("The value, %s, does not map to a UID" % (se))
        raise ke

    return(assigned_shifts)


def main():
    make_matching('docs/xuMakerSpringAvailability.txt')


if __name__ == '__main__':
    main()
