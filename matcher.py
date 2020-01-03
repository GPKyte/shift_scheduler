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
from logger import *

import json


# Using ROW-MAJOR table!!!!
# That means TABLE[ROW][COLUMN] = cell
def as_CSV(table):
    lines = []

    log_pretty_data(table)

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

    vertex_2_slot = dict(zip(vertices, slots))
    slot_2_vertex = dict(zip(slots, vertices))

    edges = [(slot_2_vertex.get(w), slot_2_vertex.get(s), w.weight)
                for w, s in edges]

    # Solve Job Matching problem
    def decide_matching(edges, vertices):
        path2file = "./docs/xuMakerSpringAvailability"

        save_data_for_solver(edges, len(vertices), path2file)
        solver_args = ['./match_bipartite_graph', '-f', path2file, '--max']
        solver_output = check_output(solver_args).decode("utf-8").split('\n')
        edge_set = parse_graph_solution(solver_output)

        return edge_set

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
    table = scheduler.make_schedule(assignments, ID_2_slotname)

    output_file = open('new_schedule.csv', 'w')
    output_file.write(as_CSV(table))
    output_file.close()

    return(table)


# Given two collections and a proceedure to retrieve key
# Make pairs of all matches using psuedo hash-join on equality
# Returns list of 2-tuples
def match_equal_key_pairs(left, right, get_key):
    left_keys = list(map(get_key, left))
    right_keys = list(map(get_key, right))

    list_of_lists = [[] for W in range(len(left_keys))]
    join_zone = dict(zip(left_keys, list_of_lists))
    matched_pairs = list()

    # Create buckets indexed by left list keys
    for W in range(len(left)):
        join_zone[left_keys[W]].append(left[W])

    for W in range(len(right)):
        right_key = right_keys[W]

        # Match all right list items with all previously bucketed items
        for each_item in join_zone.get(right_key, list()):
            matched_pairs.append( (each_item, right[W]) )

    return matched_pairs


# Designed specifically parsing the output of an Bipartite Graph match solver
# Solver output is a collection of lines
# RETURN set of edges remaining in subgraph as list of 2-tuples
def parse_graph_solution(solver_output):
    just_some_index = solver_output[0].find(':')
    num_edges_in_result = int( solver_output[0][just_some_index + len(" "):])
    start = 2 # Known from looking at output, completely a magic number

    # TODO: does name imply mutator method even when it's for a filter?
    # goal is to return bool for every element in list individually
    def clean(a_line_to_the_solution):
        empty = None

        if a_line_to_the_solution is empty:
            return False
        if len(a_line_to_the_solution) in [0, 1]:
            return False
        if " " not in a_line_to_the_solution:
            return False

        pairs = a_line_to_the_solution.split(" ")

        if len(pairs) != 2:
            return False

        try:
            int(pairs[0])
            int(pairs[1])
        except Exception as e:
            return False

        return True

    # This is a list of string lines with 2 numbers separated by a space
    pairs = solver_output[start:start + num_edges_in_result]
    sanitized_data = filter(clean, pairs)
    str_matched_edges = [pair.split(' ') for pair in sanitized_data]

    matched_edges = map( # to integers for table
        lambda pair: (int(pair[0]), int(pair[1])),
        str_matched_edges)

    track_var("solver_output", solver_output)
    track_var("sanitized_data", sanitized_data)

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
# First two lines will be #Vertices and #Edges
# Followed by lines looking like x y z
# And edge is referenced by a pair of vertices and given some weight
def save_data_for_solver(edges, num_vertices, output_file_name):
    x = 0
    y = 1
    weight = 2
    output_data = [str(num_vertices), str(len(edges))]
    output_data += [f"{E[x]} {E[y]} {E[weight]}" for E in edges]

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

