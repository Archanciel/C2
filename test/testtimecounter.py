import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from utility.timecounter import TimeCounter

class TestTimeCounter(unittest.TestCase):
    def testSplitDurationSecondZeroSS(self):
        duration = 0
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 0)
        self.assertEqual(hh, 0)
        self.assertEqual(mm, 0)
        self.assertEqual(ss, 0)


    def testSplitDurationSecondSomeSS(self):
        duration = 40
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 0)
        self.assertEqual(hh, 0)
        self.assertEqual(mm, 0)
        self.assertEqual(ss, 40)


    def testSplitDurationSecondMMZeroSS(self):
        duration = 60
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 0)
        self.assertEqual(hh, 0)
        self.assertEqual(mm, 1)
        self.assertEqual(ss, 0)


    def testSplitDurationSecondMMSS(self):
        duration = 100
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 0)
        self.assertEqual(hh, 0)
        self.assertEqual(mm, 1)
        self.assertEqual(ss, 40)


    def testSplitDurationSecondHHZeroMMZeroSS(self):
        duration = 3600
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 0)
        self.assertEqual(hh, 1)
        self.assertEqual(mm, 0)
        self.assertEqual(ss, 0)


    def testSplitDurationSecondHHMMSS(self):
        duration = 3700
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 0)
        self.assertEqual(hh, 1)
        self.assertEqual(mm, 1)
        self.assertEqual(ss, 40)


    def testSplitDurationSecondDDZeroHHZeroMMZeroSS(self):
        duration = 86400
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 1)
        self.assertEqual(hh, 0)
        self.assertEqual(mm, 0)
        self.assertEqual(ss, 0)


    def testSplitDurationSecondDDZeroHHZeroMMSS(self):
        duration = 86404
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 1)
        self.assertEqual(hh, 0)
        self.assertEqual(mm, 0)
        self.assertEqual(ss, 4)


    def testSplitDurationSecondDDZeroHHMMSS(self):
        duration = 86504
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 1)
        self.assertEqual(hh, 0)
        self.assertEqual(mm, 1)
        self.assertEqual(ss, 44)


    def testSplitDurationSecondDDHMMSS(self):
        duration = 90104
        counter = TimeCounter(durationSecond=duration)

        dd, hh, mm, ss = counter.splitDurationSecond(duration)

        self.assertEqual(dd, 1)
        self.assertEqual(hh, 1)
        self.assertEqual(mm, 1)
        self.assertEqual(ss, 44)


if __name__ == '__main__':
    unittest.main()