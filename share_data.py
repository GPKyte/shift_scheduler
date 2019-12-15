# File used to separate data from test file
# Reason for move was arbitrary, i.e. mostly for appearance and possibility of other shared, global vars

all_day = '10:00-17:00'
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