from scheduler import *
from matcher import *
from share_data import *
# Test file for validating conversions between I/O
from pprint import pprint


def main():
    tester = TestMachine()



class TestMachine():
    """
    Functional class that may maintain it's own data and methods
    Should provide testing methods and consistent clear results
    """
    ALL = 0
    NEW = 1
    WIP = 2

    def __init__(self):
        test_types = [self.ALL, self.NEW, self.WIP]
        self.tests = [{} for each in test_types]
        self.scheduler = ScheduleInterpreter()


    def new_test(self, pretty_name=None):
        def decorator(base_fxn):
            if pretty_name is None:
                pretty_name = f"Test {len(self.regression_tests[self.NEW])}"

            def test_fxn():
                try:
                    base_fxn()
                    test_results = f"{pretty_name:<50}: PASS"

                except e:
                    test_results = f"{pretty_name:<50}: FAIL"

                return test_results

            self.regression_tests[self.NEW][pretty_name] = test_fxn

            return base_fxn


    # DELETE test_assign_id_and_index because it did not assert anything and this functionality will be rewritten
    # DELETED test_flatten_availability because of DRY
    # DELETED test_generate_shifts verbose with data, will break with OOP change, was not helpful in past
    # DELETE test_generate_master_schedule bc it was too tightly coupled, will break with generalization -> parameterize?
    
    @new_test
    def new_unnamed_test(self):
        pass

    # Helper method, not an actual test
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


    def test_flatten_time_range(self):
        flat = self.scheduler.flatten_time_ranges(avail_M)
        print(flat)


    def test_exclusive_days(self):
        workers = (avail_USR, avail_WTF)
        table = self.__generate_schedule__(workers)
        print(as_CSV(table))


    def test_shared_days(self):
        workers = (avail_T, avail_WTF)
        table = self.__generate_schedule__(workers)
        print(as_CSV(table))


    # RENAMED
    @new_test
    def test_timerange_to_slots(self):
        # From 10 am to 12 pm
        result = self.scheduler.create_time_slots('10:00', '24:00')
        goal = [600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 945, 960, 975, 990, 1005, 1020, 1035, 1050, 1065, 1080, 1095, 1110, 1125, 1140, 1155, 1170, 1185, 1200, 1215, 1230, 1245, 1260, 1275, 1290, 1305, 1320, 1335, 1350, 1365, 1380, 1395, 1410, 1425]
        try:
            assert(result == goal)
        except AssertionError:
            print(result)

    ### General testing ###


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


    # UPDATE keep idea but change impl entirely
    def compare_inequal_collections(self, apples, oranges):
        if apples != oranges:
            print("%s \n%s apples\n" % (apples, len(apples)))
            print("%s \n%s oranges\n" % (oranges, len(oranges)))
            print("Apples that aren't oranges", [a for a in apples if a not in oranges])
            print("Oranges that aren't apples", [o for o in oranges if o not in apples])


    # Test basic utility's correctness
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


if __name__ == '__main__':
    main()
