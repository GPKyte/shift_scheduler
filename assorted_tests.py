from scheduler import *
# Test file for validating conversions between I/O

def main():
    tester = TestMachine()
    tester.test_generate_shifts()
    tester.test_convert_std_time()
    tester.test_week_hours_to_slots()
    tester.test_timecheck()

class TestMachine():
    ben_avail = {
        'name': 'Ben S',
        'hours': '8',
        'M': '10:00-13:00, 13:00-17:00',
        'T': '10:00-17:00',
        'W': '10:00-12:00, 13:00-17:00',
        'R': '10:00-13:00',
        'F': '10:00-12:00'
    }
    short_avail = {
        'name': 'Shortie',
        'hours': '1',
        'M': '10:00-13:00'
    }
    def __init__(self):
        self.scheduler = ScheduleInterpreter()

    def test_timecheck(self):
        # hh, hh pm/am, hhpm/am, hh:mm, hh:mm pm/am, hh:mmpm/am
        test_cases = {
            "10": "10:00",
            "10 pm": "22:00",
            "10am": "10:00",
            "11:15": "11:15",
            "18:45": "18:45",
            "18:45 pm": "18:45",
            "6:45pm": "18:45"
        }
        for test in test_cases.keys():
            try:
                checked = self.scheduler.timecheck(test)
                assert(test_cases[test] == checked)
            except AssertionError:
                print("%s -> %s != %s" % (test, test_cases[test], checked))


    def test_generate_shifts(self):
        M = [20000600, 20000615, 20000630, 20000645, 20000660, 20000675, 20000690, 20000705, 20000720, 20000735, 20000750, 20000765, 20000780, 20000795, 20000810, 20000825, 20000840, 20000855, 20000870, 20000885, 20000900, 20000915, 20000930, 20000945, 20000960, 20000975, 20000990, 20001005]
        T = [20010600, 20010615, 20010630, 20010645, 20010660, 20010675, 20010690, 20010705, 20010720, 20010735, 20010750, 20010765, 20010780, 20010795, 20010810, 20010825, 20010840, 20010855, 20010870, 20010885, 20010900, 20010915, 20010930, 20010945, 20010960, 20010975, 20010990, 20011005]
        W = [20020600, 20020615, 20020630, 20020645, 20020660, 20020675, 20020690, 20020705, 20020780, 20020795, 20020810, 20020825, 20020840, 20020855, 20020870, 20020885, 20020900, 20020915, 20020930, 20020945, 20020960, 20020975, 20020990, 20021005]
        R = [20030600, 20030615, 20030630, 20030645, 20030660, 20030675, 20030690, 20030705, 20030720, 20030735, 20030750, 20030765]
        F = [20040600, 20040615, 20040630, 20040645, 20040660, 20040675, 20040690, 20040705]
        # The UID format is 'T##DMMMM':
        #   T = Type of time slot (shift versus worker)
        #   # = ID of time slot (first worker's id is 00)
        #   D = Day of the week
        #   M = Minutes from 0-1439 (24 * 60 - 1) of given day
        shifts_short = self.scheduler.generate_shifts(ScheduleInterpreter.TYPE_WORKER, self.short_avail)
        goal_short = [20000600, 20000615, 20000630, 20000645, 20000660, 20000675, 20000690, 20000705, 20000720, 20000735, 20000750, 20000765]
        goal_ben = M+T+W+R+F
        shifts_ben = self.scheduler.generate_shifts(ScheduleInterpreter.TYPE_WORKER, self.ben_avail)

        goal_combined = goal_ben + [ScheduleInterpreter.ID_OFFSET * 1 + x for x in goal_short]
        shifts_combined = self.scheduler.generate_shifts( \
            ScheduleInterpreter.TYPE_WORKER, self.ben_avail, self.short_avail)
        try:
            assert(shifts_ben == goal_ben)
            assert(shifts_short == goal_short)
            assert(shifts_combined == goal_combined)
        except AssertionError:
            self.compare_inequal_collections(shifts_short, goal_short)
            self.compare_inequal_collections(shifts_ben, goal_ben)
            self.compare_inequal_collections(shifts_combined, goal_combined)

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


if __name__ == '__main__':
    main()
