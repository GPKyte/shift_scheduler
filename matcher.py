# This file will take in schedule information
# then match open shifts to available work hours
from threading import Thread

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
        raw_input()

    for w in range(len(right)):
        for each_item in join_zone[right_keys[w]]:
            pairs.append( (each_item, right[w]) )

    return pairs
