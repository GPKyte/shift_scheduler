from scheduler import *
# Test file for validating conversions between I/O

def main():
    tester = TestMachine()
    #tester.test_generate_shifts()
    #tester.test_convert_std_time()
    tester.test_week_hours_to_slots()

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

    def test_generate_shifts(self):
        M = [10000600, 10000615, 10000630, 10000645, 10000660, 10000675, 10000690, 10000705, 10000780, 10000795, 10000810, 10000825, 10000840, 10000855, 10000870, 10000885, 10000900, 10000915, 10000930, 10000945, 10000960, 10000975, 10000990, 10001005]
        T = [10010600, 10010615, 10010630, 10010645, 10010660, 10010675, 10010690, 10010705, 10010720, 10010735, 10010750, 10010765, 10010780, 10010795, 10010810, 10010825, 10010840, 10010855, 10010870, 10010885, 10010900, 10010915, 10010930, 10010945, 10010960, 10010975, 10010990, 10011005, 10011020, 10011035, 10011050]
        W = [10021000, 10021015, 10021030, 10021045, 10021100, 10021115, 10021130, 10021145, 10021200, 10021215, 10021230, 10021245, 10021300, 10021315, 10021330, 10021345, 10021400, 10021415, 10021430, 10021445, 10021500, 10021515, 10021530, 10021545, 10021600, 10021615, 10021630, 10021645, 10021700, 10021715, 10021730]
        R = [10030600, 10030615, 10030630, 10030645, 10030660, 10030675, 10030690, 10030705, 10030720, 10030735, 10030750, 10030765]
        F = [10040600, 10040615, 10040630, 10040645, 10040660, 10040675, 10040690, 10040705]
        # The UID format is 'T##DMMMM':
        #   T = Type of time slot (shift versus worker)
        #   # = ID of time slot (first worker's id is 00)
        #   D = Day of the week
        #   M = Minutes from 0-1439 (24 * 60 - 1) of given day
        shifts_short = self.scheduler.generate_shifts(self.short_avail, type_id=2)
        goal_short = [20000600, 20000615, 20000630, 20000645, 20000660, 20000675, 20000690, 20000705, 20000720, 20000735, 20000750, 20000765]
        goal_ben = M+T+W+R+F
        shifts_ben = self.scheduler.generate_shifts(self.ben_avail, type_id=1)
        try:
            assert(shifts_ben == goal_ben)
            assert(shifts_short == goal_short)
        except AssertionError:
            self.compare_inequal_collections(shifts_short, goal_short)
            self.compare_inequal_collections(shifts_ben, goal_ben)

    # For one employee availability
    def test_week_hours_to_slots(self):
        flat_short = self.scheduler.flatten_time_ranges(self.short_avail)
        # DMMMM where day is Day of week, from 0-6 (would 107 be better? For padding, yes)
        goal_short = [10*60, 10*60 + 15, 10*60 + 30, 10*60 + 45,
                        11*60, 11*60 + 15, 11*60 + 30, 11*60 + 45,
                        12*60, 12*60 + 15, 12*60 + 30, 12*60 + 45]

        # goal_ben may be incorrect
        goal_ben = [600, 615, 630, 645, 660, 675, 690, 705, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 945, 960, 975, 990, 1005, 10600, 10615, 10630, 10645, 10660, 10675, 10690, 10705, 10720, 10735, 10750, 10765, 10780, 10795, 10810, 10825, 10840, 10855, 10870, 10885, 10900, 10915, 10930, 10945, 10960, 10975, 10990, 11005, 11020, 11035, 11050, 21000, 21015, 21030, 21045, 21100, 21115, 21130, 21145, 21200, 21215, 21230, 21245, 21300, 21315, 21330, 21345, 21400, 21415, 21430, 21445, 21500, 21515, 21530, 21545, 21600, 21615, 21630, 21645, 21700, 21715, 21730, 30600, 30615, 30630, 30645, 30660, 30675, 30690, 30705, 30720, 30735, 30750, 30765, 40600, 40615, 40630, 40645, 40660, 40675, 40690, 40705]
        flat_ben = self.scheduler.flatten_time_ranges(self.ben_avail)

        try:
            assert(flat_short == goal_short)
            assert(flat_ben == goal_ben)
        except AssertionError:
            self.compare_inequal_collections(flat_short, goal_short)
            self.compare_inequal_collections(flat_ben, goal_ben)

    def compare_inequal_collections(self, apples, oranges):
        if apples != oranges:
            print("%s \n%s\n" % (apples, len(apples)))
            print("%s \n%s\n" % (oranges, len(oranges)))
            print([a for a in oranges if a not in apples])
            print([b for b in apples if b not in oranges])

    def test_convert_std_time(self):
        # From 10 am to 12 pm
        result = self.scheduler.create_time_range('10:00', '24:00')
        goal = [600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 945, 960, 975, 990, 1005, 1020, 1035, 1050, 1065, 1080, 1095, 1110, 1125, 1140, 1155, 1170, 1185, 1200, 1215, 1230, 1245, 1260, 1275, 1290, 1305, 1320, 1335, 1350, 1365, 1380, 1395, 1410, 1425]
        try:
            assert(result == goal)
        except AssertionError:
            print(result)


if __name__ == '__main__':
    main()
