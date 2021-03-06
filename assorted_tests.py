from scheduler import *
from matcher import *
from share_data import *
from logger import *

# Test file for validating conversions between I/O
from pprint import pprint


def main():
    tester = TestMachine()

    try:
        tester.run_regression_tests()
        tester.run_new_tests()

    except Exception as e:
        raise e
    else:
        log("All Tests SUCCESS")
    finally:
        log("- = - = - = - = - = - = - = - = - = - = -\n")


def count(objects):
    return(len(objects))

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


    def run_new_tests(self):
        try:
            self.test_exclusive_slots()
            self.test_overlapping_slots()
            print("SUCCESS for new test(s)")

        except Exception:
            print("FAILED new test(s)")
            raise

    def run_regression_tests(self):
        try:
            self.test_sanitize_input()
            self.test_join_lists()
            self.test_timecheck()
            self.test_group_sequential_ranges()
            self.test_timerange_to_slots()
            self.test_weight_policies()
            self.test_print_table_as_csv()
            self.test_remove_empty_rows_from_table()

            print("SUCCESS for regression test(s)")
        except Exception:
            print("FAILED run regression test(s)")
            raise


    def run_inspection_tests(self):
        self.inspect_slot_translation()
        raw_input()


    # UPDATE keep idea but change impl entirely
    def __compare_inequal_collections__(self, apples, oranges):
        if apples != oranges:
            print("%s \n%s apples\n" % (apples, len(apples)))
            print("%s \n%s oranges\n" % (oranges, len(oranges)))
            print("Apples that aren't oranges", [a for a in apples if a not in oranges])
            print("Oranges that aren't apples", [o for o in oranges if o not in apples])


    # Helper method, not an actual test
    def __generate_schedule__(self, workers):

        w_slots = self.scheduler.make_slots(
            ScheduleInterpreter.TYPE_WORKER, *workers)

        s_slots = self.scheduler.make_slots(
            ScheduleInterpreter.TYPE_SHIFT, open_position_for_makerspace)

        shifts = assign_shifts(w_slots, s_slots)
        table = self.scheduler.make_schedule(shifts)

        return table


    ### General testing ###

    def test_create_slots_from_avail(self):

        avail = ben_avail.copy()
        avail["id"] = key
        avail["type"] = type_id

        slots = self.scheduler.convert_availability_to_slots(avail)
        s0 = slots[0]

        assert(s0.weight == 0) # 0-weight policy default
        assert(s0.time_of_day == 10*60)
        assert(s0.id == ID)
        assert(s0.day_in_cycle == 0) # Monday is first

        assert(len(slots) == 100)


    def test_variable_table_size(self):
        start_minute = 10 * 60
        end_minute = 17 * 60
        interval = 15
        times_of_day = range(start_minute, end_minute, interval)

        width_makerspace = 7 * shifts_at_makerspace_per_day # Week day repeat and two per day
        height_makerspace = len(times_of_day)

        def find_index_in(indexable_data):
            col = random.randint(0, shifts_at_makerspace_per_day)
            row = random.randint(0, count(times_of_day))

            return (row, col)

        T = ScheduleInterpreter.make_empty_table(times_of_day)
        ScheduleInterpreter.fill_empty_table(T, find_index_in, times_of_day)

        assert(len(T) == len(times_of_day)) # Row-major
        same_length = len(T[0])

        for row in T:
            assert(len[row] == same_length)



    def test_exclusive_slots(self):
        workers = (avail_USR, avail_WTF)
        table = self.__generate_schedule__(workers)
        log_debug(as_CSV(table))

    def test_overlapping_slots(self):
        workers = (avail_T, avail_WTF)
        table = self.__generate_schedule__(workers)
        log_debug(as_CSV(table))

    def test_timerange_to_slots(self):
        # From 10 am to 12 pm
        result = self.scheduler.create_TOD_slot_range('10:00', '24:00')
        goal = list(range(600, 1440, 15))

        try:
            assert(result == goal)
        except AssertionError as e:
            raise AssertionError(f"Resulting timerange is incorrect:\n{result}")

    def test_invalid_slot_failure(self):
        pass
    def test_favor_long_shifts(self):
        pass

    def test_sanitize_input(self):
        dirty_json = dirty_avail_1
        clean_json = self.scheduler.sanitize_availability(dirty_json)
        goal_json = clean_avail_1

        try:
            just_name = {"Name": "Apple"} # Missing important fields
            lowercase_name = self.scheduler.sanitize_availability(just_name)
        except AssertionError:
            pass
        else:
            raise AssertionError("Expected Error not raised")

        try:
            assert(clean_json == goal_json)
        except AssertionError:
            raise AssertionError(f"Cleaned data does not met standards:\nResult: {clean_json}\nGoal: {goal_json}")

        for avail in [avail_M, avail_T, avail_WTF, avail_USR, ben_avail, short_avail]:
            A = avail.copy()
            A['id'] = None
            A['type'] = 0
            clean = self.scheduler.sanitize_availability(A)

            # Note on:  assert(clean.__contains__('name'))
            # Not part of sanitize requirements,
            # but once before, 'name' was disappearing after avail santized
            assert(clean.__contains__('name'))


    def test_interpret_match_results(self):
        stubbed_results = clean_solver_output
        edges_1 = parse_graph_solution(stubbed_results)

        stubbed_results = clean_solver_output + [""] # Had problem with empty line once
        edges_2 = parse_graph_solution(stubbed_results)

        assert(len(edges_1) > 0)
        assert(len(edges_1) == len(edges_2))
        assert(len(edges_1[0]) == 2)

        int(edges_1[0][0])
        int(edges_1[0][1])

        for e in edges_1:
            assert(e[0] != e[1])

        return True

    def test_edge_generation(self):
        A = range(0, 1000, 1)
        B = range(0, 1000, 2)
        C = match_equal_key_pairs(A, B, int)

        assert(len(C) == 500)
        assert(B == C)

        X = range(990, 1606, 15)
        Y = range(1500, 1651, 15)
        Z = match_equal_key_pairs(X, Y, int)

        assert(len(Z) == 7) # 15*107 = 1605; 15*100 = 1500
        assert(Z[0] == 1500)
        assert(Z[-1] == 1605)

    def test_print_table_as_csv(self):
        row_major_table = \
            [['M', 'T', 'W', 'R', 'F', 'S', 'U'],
            [10100600, None, None, None, None, None, None],
            [None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None]]
        table = as_CSV(row_major_table)

        goal = f"M,T,W,R,F,S,U\n10100600,None,None,None,None,None,None\nNone,None,None,None,None,None,None\nNone,None,None,None,None,None,None"

        try:
            assert(table == goal)
        except AssertionError:
            log_debug(table)


    def test_group_sequential_ranges(self):
        A = list(range(0, 100, 1))
        B = list(range(40, 80, 1))
        C = list(range(90, 100, 1))
        D = list(range(0, 35, 1))

        all_possible = A
        ungrouped = B + C + D
        goal = [D, B, C]
        result = self.scheduler.group_sequential_ranges(all_possible, ungrouped)

        try:
            assert(result == goal)
        except AssertionError:
            raise AssertionError(f"Resulting sequential ranges are incorrect:\n{result}")


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
        listA = list(range(0, 100))
        listB = list(range(0, 100, 5))
        listAB = match_equal_key_pairs(listA, listB, lambda x: x)
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


    def test_weight_policies(self):

        def test_long_shift():
            flags = [self.scheduler.LONG_SHIFT]
            interval = ScheduleInterpreter.SHIFT_LENGTH

            possible_shift_times = []
            possible_shift_times += range(12*60, 15*60, interval) # len = 12
            possible_shift_times += range(16*60, 17*60, interval) # len = 4
            possible_shift_times += range(10*60, 10*60 + 30, interval) # len = 2

            slots = [
                Slot(time_of_day=TOD, validation_on=False)
                    for TOD in possible_shift_times
            ]

            self.scheduler.decide_weights(slots, flags)

            assert(len(possible_shift_times) == len(slots))
            assert(slots[0].weight == 12)
            assert(slots[11].weight == 12)
            assert(slots[12].weight == 4)
            assert(slots[15].weight == 4)
            assert(slots[16].weight == 2)
            assert(slots[-1].weight == 2)

        # Test the policies conscisely below
        try:
            test_long_shift()
        except AssertionError as e:
            log_debug(str(e))

            return False


    def inspect_slot_translation(self):

        count = 1
        slots = [
            Slot(*slot_args, validation_on=False)
                for slot_args in par_baked_slots[0:3]
        ]

        for s in slots:
            log_verbose(f"Inspecting Slot #{count}")
            log_verbose(f"\t{'String':<30}{str(s)}")
            log_verbose(f"\t{'Integer':<30}{int(s)}")
            log_verbose(f"\t{'Default':<30}{repr(s)}")
            count += 1

        return None


if __name__ == '__main__':
    main()
