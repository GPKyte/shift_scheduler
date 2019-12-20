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


# Using ROW-MAJOR table!!!!
# That means TABLE[ROW][COLUMN] = cell
def as_CSV(table):
    str_table = []

    for each_row in table:
        table_cells_as_strings = list(map(str, each_row))
        lines.append(",".join(table_cells_as_strings))

    return ("\n".join(lines))


# Take two sets of all unique slots that can be matched
# By an equality of Time of Day stored in the UID of each slot
# The method reduces the problem to Job Matching in Graph Theory
# by treating each set of slots as partitions in a bipartite graph
# RETURNS a set of 2-tuples that represent the assignment of an
#   employee to a INTERVAL-sized shift, aka slot.
def assign_shifts(w_slots, s_slots):
    slots = sorted(w_slots + s_slots)
    vertices = range(len(slots))
    edges = select_matching_pairs(w_slots, s_slots) # Edges describe bipartite graph

    vertex_2_slot = dict(vertices, slots)
    slot_2_vertex = dict(slots, vertices)

    edges = [(slot_2_vertex.get(w), slot_2_vertex.get(s))
                for w, s in edges]

    # Solve Job Matching problem
    def decide_matching(edges, vertices):
        save_data_for_solver(edges, len(vertices), )
        solver_args = ['./match_bipartite_graph', '-f', , '--max']
        solver_output = check_output(solver_args).split('\n')
        edge_set = parse_graph_solution(solver_output)

    edges = decide_matching(edges, vertices)
    assigned_shifts = [(vertex_2_slot.get(w), vertex_2_slot.get(s))
                for w, s in edges]

    return(assigned_shifts)


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


# Given two collections and a lambda to retrieve key
# Make pairs of all matches using psuedo hash-join on equality
# Returns list of pairs (tuples)
def match_equal_key_pairs(left_list, right_list, get_key):
    left_list.sort(key=get_key)
    right_list.sort(key=get_key)

    longer_list = left_list if len(left_list) >= len(right_list)

    # Now mimc merge sort and pair off the lists
    caravan = 0

    while caravan < len(longer_list):
        scout_left = caravan
        scout_right = caravan

        L = left_list[scout_left]
        R = right_list[scout_right]

        if L == R:
            matched_pairs += (L, R)
        elif L < R:
            scout_left += 1
        elif L > R:
            scout_right += 1
        else:
            raise Exception("Unknown state, logically impossible comparison")

    return matched_pairs


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


# Functional method to reverse direction of dictionary
# Probably not efficient, oh well. Not intended for large maps
def reverse_keys_and_values(mapping):
    new_map = {}

    for key in mapping.keys():
        value = mapping[key]
        new_map[value] = key

    return new_map


# Pretty cut and dry method here to save file in format solver expects
# value_map: converts UIDs to indexed sequential vertices in graph
# TODO: Change weight (third number currently 0) of edges to favor long shifts
def save_data_for_solver(edges, num_vertices, output_file_name):
    # First two lines will be #Vertices and #Edges
    # Followed by lines looking like x y 0
    # And edge is referenced by a pair of vertices and given some weight
    output_data = [str(num_vertices), str(len(edges))]
    output_data += ["%s %s 0" % (value_map[e[0]], value_map[e[1]])
        for e in edges]

    output_file = open(output_file_name, 'w')
    output_file.write('\n'.join(output_data))
    output_file.close()


# High-level readable function to join two sets of UIDs
# RETURN matched UIDs as 2-tuples
def select_matching_pairs(worker_slots, shift_slots):
    def get_key_from_a_slot(slot):
        return int(slot)

    return match_equal_key_pairs(worker_slots, shift_slots, get_key_from_a_slot)


if __name__ == '__main__':
    # TODO: (Feature) Calendar integration with results
    make_matching('docs/xuMakerSpringAvailability.txt')

