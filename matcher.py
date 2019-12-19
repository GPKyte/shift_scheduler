# MATCHER.PY
#
# This package works as a unit to interpret employee schedules
# Towards the end of assigning them shifts that provide maximum
# coverage of all work hours
#
# This problem is reduced to Bipartite Graphs & Job Matching,
# This is done at a "slot" based level. Look into SCHEDULER.PY
# for more information on time range interpretation of availabilities
from scheduler import ScheduleInterpreter
from subprocess import check_output
import json

# Given two collections and a lambda to retrieve key
# Make pairs of all matches using psuedo hash-join on equality
# Returns list of pairs (tuples)
def match_pairs(left, right, get_key):
    left_keys = list(map(get_key, left))
    right_keys = list(map(get_key, right))

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
# RETURN matched UIDs as 2-tuples
def match_workers_to_shifts(worker_slots, shift_slots):
    def get_key_from_a_slot(slot):
        return int(slot)

    return match_pairs(worker_slots, shift_slots, get_key_from_a_slot)


# Functional method to reverse direction of dictionary
# Probably not efficient, oh well. Not intended for large maps
def reverse_keys_and_values(mapping):
    new_map = {}

    for key in mapping.keys():
        value = mapping[key]
        new_map[value] = key

    return new_map


# Using ROW-MAJOR table!!!!
# That means TABLE[ROW][COLUMN] = cell
def as_CSV(table):
    str_table = []

    for each_row in table:
        table_cells_as_strings = list(map(str, each_row))
        lines.append(",".join(table_cells_as_strings))

    return ("\n".join(lines))


# Pretty cut and dry method here to save file in format solver expects
# value_map: converts UIDs to indexed sequential vertices in graph
# TODO: Change weight (third number currently 0) of edges to favor long shifts
def save_data_for_solver(edges, num_vertices, value_map, output_file_name):
    # First two lines will be #Vertices and #Edges
    # Followed by lines looking like x y 0
    # And edge is referenced by a pair of vertices and given some weight
    output_data = [str(num_vertices), str(len(edges))]
    output_data += ["%s %s 0" % (value_map[e[0]], value_map[e[1]])
        for e in edges]

    output_file = open(output_file_name, 'w')
    output_file.write('\n'.join(output_data))
    output_file.close()


# Designed specifically parsing the output of an Bipartite Graph match solver
# Solver output is a collection of lines
# RETURN set of edges remaining in subgraph as list of 2-tuples
def parse_graph_solution(solver_output):
        just_some_index = solver_output[0].find(':')
        num_edges_in_result = int( solver_output[0][just_some_index + len(" "):])
        start = 2 # Known from looking at output, completely a magic number

        # This is a list of string lines with 2 numbers separated by a space
        pairs = solver_output[start:start + num_edges_in_result]
        str_matched_edges = [pair.split(' ') for pair in pairs]
        matched_edges = map( # to integers for table
            lambda pair: (int(pair[0]), int(pair[1])),
            str_matched_edges)

        return(matched_edges)


# The I/O high-level director of this program sourcing data and writing it back
def make_matching(availability_file):
    file = open(availability_file, 'r')
    worker_availability = json.loads(file.read())
    file.close()

    position1_shifts = position2_shifts = {
        # Each time I see this I think about a quick concise generator,
        # but what if the content changes for only some days? So keep it simple
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
    shifts  = ScheduleInterpreter.TYPE_SHIFT
    w_slots = scheduler.make_slots(workers, *worker_availability)
    s_slots = scheduler.make_slots(shifts, position1_shifts, position2_shifts)

    # Map ids in UIDs to worker names
    ID_2_slotname = {slot.id: str(slot) for slot in w_slots}

    # TODO: Find the bug that causes an empty line to be in output
    assignments = assign_shifts(w_slots, s_slots)
    table = scheduler.create_master_schedule(assignments, ID_2_slotname)

    output_file = open('new_schedule.csv', 'w')
    output_file.write(as_CSV(table))
    output_file.close()

    return(table)


# Take two sets of all unique slots that can be matched
# By an equality of Time of Day stored in the UID of each slot
# The method reduces the problem to Job Matching in Graph Theory
# by treating each set of slots as partitions in a bipartite graph
# RETURNS a set of 2-tuples that represent the assignment of an
#   employee to a INTERVAL-sized shift, aka slot.
def assign_shifts(w_slots, s_slots):
    # Because our bipartite matcher requires sequential vertices
    # We sort and index all slots to map them to vertices and recover them
    all_slots = sorted(w_slots + s_slots)
    value_map = dict(zip(all_slots, range(len(all_slots))))

    # Generate "edges" in a description of a bipartite graph
    matchings = match_workers_to_shifts(w_slots, s_slots)
    save_data_for_solver(matchings, len(all_slots), value_map, './docs/graph')
    # Don't worry about leaving file behind (don't waste energy by deleting it)

    # Solve Job Matching problem
    solver_args = ['./match_bipartite_graph', '-f', './docs/graph', '--max']
    solver_output = check_output(solver_args).split('\n')
    edge_set = parse_graph_solution(solver_output)

    try: # Revert graph vertices to slots as UIDs
        recover = reverse_keys_and_values(value_map)
        assignments = [(recover[e[0]], recover[e[1]]) for e in edge_set]

    except KeyError as ke:
        print("The value, %s, does not map to a UID" % (se))
        raise ke

    return(assignments)

# TODO: (Feature) Calendar integration with results
# TODO: Polymorphism of UIDs
def main():
    make_matching('docs/xuMakerSpringAvailability.txt')


if __name__ == '__main__':
    main()
