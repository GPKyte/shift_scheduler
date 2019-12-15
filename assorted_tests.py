from scheduler import *
from matcher import *
# Test file for validating conversions between I/O
from pprint import pprint


def main():
    tester = TestMachine()

    tester.test_assign_id_and_index()
    tester.test_convert_std_time()
    tester.test_exclusive_days()
    tester.test_flatten_time_range()
    tester.test_generate_shifts()
    tester.test_generate_master_schedule()
    tester.test_print_table_as_csv()
    tester.test_join_lists()
    tester.test_remove_empty_rows_from_table()
    tester.test_timecheck()
    tester.test_week_hours_to_slots()


class TestMachine():
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

    def __init__(self):
        self.scheduler = ScheduleInterpreter()

    def test_join_lists(self):
        listA = range(0, 100)
        listB = range(0, 100, 5)
        listAB = match_pairs(listA, listB, lambda x: x)
        goal_pairs = [(a, a) for a in range(0, 100, 5)]

        try:
            assert(listAB == goal_pairs)
    
        except AssertionError:
            pass
            print("Results: ", listAB)
            print("Goal: ", goal_pairs)

    def test_assign_id_and_index(self):
        need_id = [{'name' : 'a_1'}, {'name' : 'b_2'}, {'name' : 'c_3'}]
        with_id = self.scheduler.assign_id(need_id)

        print(with_id)
        pprint(self.scheduler.flatten_time_ranges(with_id.get(0)))

    def test_flatten_time_range(self):
        flat = self.scheduler.flatten_time_ranges(self.avail_M)
        print(flat)

    def test_timecheck(self):
        # hh, hh pm/am, hhpm/am, hh:mm, hh:mm pm/am, hh:mmpm/am
        test_cases = {
            "10":       "10:00",
            "10 pm":    "22:00",
            "10am":     "10:00",
            "11:15":    "11:15",
            "18:45":    "18:45",
            "18:45 pm": "18:45",
            "6:45pm":   "18:45"
        }
        for test in test_cases.keys():
            try:
                checked = self.scheduler.timecheck(test)
                assert(test_cases[test] == checked)
            except AssertionError:
                print("%s -> %s != %s" % (test, test_cases[test], checked))

    def __generate_schedule__(self, workers):
        s_slots = self.scheduler.create_time_slots('10:00', '24:00')
        w_slots = self.scheduler.generate_shifts(
            ScheduleInterpreter.TYPE_WORKER, *workers
        )
        ID_schedules = self.scheduler.assign_id(workers)
        ID_mapping = dict(
            [(w, ID_schedules[w]['Name']) for w in ID_schedules.keys()]
        )

        shifts = assign_shifts(w_slots, s_slots)
        table = self.scheduler.create_master_schedule(shifts, ID_mapping)

        return table

    def test_exclusive_days(self):
        workers = (self.avail_USR, self.avail_WTF)
        table = self.__generate_schedule__(workers)
        print(as_CSV(table))

    def test_shared_days(self):
        workers = (self.avail_T, self.avail_WTF)
        table = self.__generate_schedule__(workers)
        print(as_CSV(table))

    def test_generate_master_schedule(self):
        worker_UID = 10100600 # Worker 2 at 10:00 Monday
        shift_UID = 20000600 # Shift 1 at 10:00 Monday
        shifts = [(10060990, 20060990),(10061005, 20061005)]

        for slot in range(0,75,15):
            shifts.append( (worker_UID + slot, shift_UID + slot) )

        master = self.scheduler.create_master_schedule(shifts)
        table = \
            [['M', 'T', 'W', 'R', 'F', 'S', 'U'],
            [10100600, None, None, None, None, None, None],
            [10100615, None, None, None, None, None, None],
            [10100630, None, None, None, None, None, None],
            [10100645, None, None, None, None, None, None],
            [10100660, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, 10060990],
            [None, None, None, None, None, None, 10061005]] # 7 by 28

        try:
            assert(master == table)
        except AssertionError:
            print("FAILED: test_generate_master_schedule() mismatch expectations of table output")
            pprint(master)
            print("Rows expected %s vs. received %s" % (len(table), len(master)))
            print("Columns expected %s vs. received %s" % (len(table[0]), len(master[0])))
            print(table[1][0], master[1][0], "First values")

    def test_print_table_as_csv(self):
        row_major_table = \
            [['M', 'T', 'W', 'R', 'F', 'S', 'U'],
            [10100600, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None]]
        table = as_CSV(row_major_table)

        goal = """M,T,W,R,F,S,U
10100600,None,None,None,None,None,None
None,None,None,None,None,None,None
None,None,None,None,None,None,None"""

        try:
            assert(table == goal)
        except AssertionError:
            print(table)


    def test_generate_shifts(self):
        M = [10000600, 10000615, 10000630, 10000645, 10000660, 10000675, 10000690, 10000705, 10000720, 10000735, 10000750, 10000765, 10000780, 10000795, 10000810, 10000825, 10000840, 10000855, 10000870, 10000885, 10000900, 10000915, 10000930, 10000945, 10000960, 10000975, 10000990, 10001005]
        T = [10010600, 10010615, 10010630, 10010645, 10010660, 10010675, 10010690, 10010705, 10010720, 10010735, 10010750, 10010765, 10010780, 10010795, 10010810, 10010825, 10010840, 10010855, 10010870, 10010885, 10010900, 10010915, 10010930, 10010945, 10010960, 10010975, 10010990, 10011005]
        W = [10020600, 10020615, 10020630, 10020645, 10020660, 10020675, 10020690, 10020705, 10020780, 10020795, 10020810, 10020825, 10020840, 10020855, 10020870, 10020885, 10020900, 10020915, 10020930, 10020945, 10020960, 10020975, 10020990, 10021005]
        R = [10030600, 10030615, 10030630, 10030645, 10030660, 10030675, 10030690, 10030705, 10030720, 10030735, 10030750, 10030765]
        F = [10040600, 10040615, 10040630, 10040645, 10040660, 10040675, 10040690, 10040705]

        # The UID format is 'T##DMMMM':
        #   T = Type of time slot (shift versus worker)
        #   # = ID of time slot (first worker's id is 00)
        #   D = Day of the week
        #   M = Minutes from 0-1439 (24 * 60 - 1) of given day
        shifts_short = self.scheduler.generate_shifts(ScheduleInterpreter.TYPE_WORKER, self.short_avail)
        goal_short = [10000600, 10000615, 10000630, 10000645, 10000660, 10000675, 10000690, 10000705, 10000720, 10000735, 10000750, 10000765]
        goal_ben = M+T+W+R+F
        shifts_ben = self.scheduler.generate_shifts(ScheduleInterpreter.TYPE_WORKER, self.ben_avail)

        goal_combined = goal_ben + [ScheduleInterpreter.ID_OFFSET * 1 + x for x in goal_short]
        shifts_combined = self.scheduler.generate_shifts( \
            ScheduleInterpreter.TYPE_WORKER, self.ben_avail, self.short_avail)

        testing_pairs = [
            (shifts_ben, goal_ben),
            (shifts_short, goal_short),
            (shifts_combined, goal_combined)
        ]

        for each in testing_pairs:
            try:
                assert(each[0] == each[1])
            except AssertionError:
                self.compare_inequal_collections(each[0], each[1])
                print()

    # For one employee availability
    # DMMMM where day is Day of week, from 0-6 (would 107 be better? For padding, yes)
    def test_week_hours_to_slots(self):
        flat_short = self.scheduler.flatten_time_ranges(self.short_avail)
        goal_short = [10*60, 10*60 + 15, 10*60 + 30, 10*60 + 45,
                        11*60, 11*60 + 15, 11*60 + 30, 11*60 + 45,
                        12*60, 12*60 + 15, 12*60 + 30, 12*60 + 45]

        flat_ben = self.scheduler.flatten_time_ranges(self.ben_avail)
        goal_ben = [600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 945, 960, 975, 990, 1005, 10600, 10615, 10630, 10645, 10660, 10675, 10690, 10705, 10720, 10735, 10750, 10765, 10780, 10795, 10810, 10825, 10840, 10855, 10870, 10885, 10900, 10915, 10930, 10945, 10960, 10975, 10990, 11005, 20600, 20615, 20630, 20645, 20660, 20675, 20690, 20705, 20780, 20795, 20810, 20825, 20840, 20855, 20870, 20885, 20900, 20915, 20930, 20945, 20960, 20975, 20990, 21005, 30600, 30615, 30630, 30645, 30660, 30675, 30690, 30705, 30720, 30735, 30750, 30765, 40600, 40615, 40630, 40645, 40660, 40675, 40690, 40705]

        try:
            assert(flat_short == goal_short)
            assert(flat_ben == goal_ben)
        except AssertionError:
            self.compare_inequal_collections(flat_short, goal_short)
            self.compare_inequal_collections(flat_ben, goal_ben)

    def compare_inequal_collections(self, apples, oranges):
        if apples != oranges:
            print("%s \n%s apples\n" % (apples, len(apples)))
            print("%s \n%s oranges\n" % (oranges, len(oranges)))
            print("Apples that aren't oranges", [a for a in apples if a not in oranges])
            print("Oranges that aren't apples", [o for o in oranges if o not in apples])

    def test_convert_std_time(self):
        # From 10 am to 12 pm
        result = self.scheduler.create_time_slots('10:00', '24:00')
        goal = [600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 945, 960, 975, 990, 1005, 1020, 1035, 1050, 1065, 1080, 1095, 1110, 1125, 1140, 1155, 1170, 1185, 1200, 1215, 1230, 1245, 1260, 1275, 1290, 1305, 1320, 1335, 1350, 1365, 1380, 1395, 1410, 1425]
        try:
            assert(result == goal)
        except AssertionError:
            print(result)

    def test_remove_empty_rows_from_table(self):
        raw_table = end_table = [
            [None],
            [1],
            [None],
            [None],
            [2],
            [3],
            [None]
        ]
        goal_pruned = [[1], [2], [3]]
        self.scheduler.prune_empty_lists_from(raw_table)

        try:
            assert(end_table == goal_pruned)
        except AssertionError:
            print("FAILED to remove correct rows")

if __name__ == '__main__':
    main()
