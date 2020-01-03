# File used to separate data from test file
# Reason for move was arbitrary, i.e. mostly for appearance and possibility of other shared, global vars

all_day = '10:00-17:00'
open_position_for_makerspace = {
    0: all_day,
    1: all_day,
    2: all_day,
    3: all_day,
    4: all_day,
    5: all_day,
    6: all_day
}
avail_M = {
    'Name': 'A_M',
    'Hours': '1',
    'M': all_day,
}
avail_T = {
    'Name': 'B_T',
    'Hours': '2',
    'T': all_day,
}
avail_WTF = {
    'Name': 'C_WTF',
    'Hours': '1',
    'W': all_day,
    'T': all_day,
    'F': all_day
}
avail_USR = {
    'Name': 'D_USR',
    'Hours': '1',
    'S': all_day,
    'U': all_day,
    'R': all_day
}
ben_avail = {
    # Object has 100 slots: 4slots/hr * (3 + 4 + 7 + 2 + 4 + 3 + 2)hr
    'Name': 'Ben S',
    'Hours': '8',
    'M': '10:00-13:00, 13:00-17:00',
    'T': all_day,
    'W': '10:00-12:00, 13:00-17:00',
    'R': '10:00-13:00',
    'F': '10:00-12:00'
}
short_avail = {
    'Name': 'Shortie',
    'Hours': '1',
    'M': '10:00-13:00'
}
dirty_avail_1 = {
    'NAME': 'dirty one',
    "Hours I want to work": 5,
    'ID': 626,
    'typE': 'test',
    "0": all_day,
    "2": "13:00-17:00",
    "8": "9:00-23:00",
    "F": all_day
}
clean_avail_1 = {
    'name': 'dirty one',
    'hours': 5,
    'id': 626,
    'type': 'test',
    "0": all_day,
    "2": "13:00-17:00",
    "8": "9:00-23:00",
    "4": all_day
}

WORKER = 1
POSITION = 2
par_baked_slots = [
    # (day_in_cycle, identifier, nice_name, time_of_day, timeslot_class, weight=0),
    (0, 0, "Slot 0", 1000, WORKER, 0),
    (2, 0, "Slot 0", 1000, WORKER, 0),
    (7, 0, "Slot 0", 1000, WORKER, 0),
    (0, 1, "Slot 1", 1000, POSITION, 0),
    (2, 1, "Slot 1", 1000, POSITION, 0),
    (7, 1, "Slot 1", 1000, POSITION, 0),
    (0, 2, "Slot 2", 1000, WORKER, 5),
    (2, 2, "Slot 2", 1000, WORKER, 5),
    (7, 2, "Slot 2", 1000, WORKER, 5)
]

clean_solver_output = [
"Optimal matching cost: 14",
"Edges in the matching:",
"0 1",
"2 3",
"4 7",
"5 6",
"8 9"
]
