import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import time
from utility.threadedtimecounter import ThreadedTimeCounter

class TestThreadedTimeCounter(unittest.TestCase):
    def testSplitDurationSecondZeroSS(self):
        duration = 0
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 0)
        self.assertEqual(counter.hour, 0)
        self.assertEqual(counter.minute, 0)
        self.assertEqual(counter.second, 0)


    def testSplitDurationSecondSomeSS(self):
        duration = 40
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 0)
        self.assertEqual(counter.hour, 0)
        self.assertEqual(counter.minute, 0)
        self.assertEqual(counter.second, 40)


    def testSplitDurationSecondMMZeroSS(self):
        duration = 60
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 0)
        self.assertEqual(counter.hour, 0)
        self.assertEqual(counter.minute, 1)
        self.assertEqual(counter.second, 0)


    def testSplitDurationSecondMMSS(self):
        duration = 100
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 0)
        self.assertEqual(counter.hour, 0)
        self.assertEqual(counter.minute, 1)
        self.assertEqual(counter.second, 40)


    def testSplitDurationSecondHHZeroMMZeroSS(self):
        duration = 3600
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 0)
        self.assertEqual(counter.hour, 1)
        self.assertEqual(counter.minute, 0)
        self.assertEqual(counter.second, 0)


    def testSplitDurationSecondHHMMSS(self):
        duration = 3700
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 0)
        self.assertEqual(counter.hour, 1)
        self.assertEqual(counter.minute, 1)
        self.assertEqual(counter.second, 40)


    def testSplitDurationSecondDDZeroHHZeroMMZeroSS(self):
        duration = 86400
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 1)
        self.assertEqual(counter.hour, 0)
        self.assertEqual(counter.minute, 0)
        self.assertEqual(counter.second, 0)


    def testSplitDurationSecondDDZeroHHZeroMMSS(self):
        duration = 86404
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 1)
        self.assertEqual(counter.hour, 0)
        self.assertEqual(counter.minute, 0)
        self.assertEqual(counter.second, 4)


    def testSplitDurationSecondDDZeroHHMMSS(self):
        duration = 86504
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 1)
        self.assertEqual(counter.hour, 0)
        self.assertEqual(counter.minute, 1)
        self.assertEqual(counter.second, 44)


    def testSplitDurationSecondDDHMMSS(self):
        duration = 90104
        counter = ThreadedTimeCounter(durationSecond=duration)

        counter.splitDurationSecond(duration)

        self.assertEqual(counter.day, 1)
        self.assertEqual(counter.hour, 1)
        self.assertEqual(counter.minute, 1)
        self.assertEqual(counter.second, 44)


    def testCountUpUnthreadedMode(self):
        counter = ThreadedTimeCounter(mode=ThreadedTimeCounter.MODE_COUNT_UP, intervalSecond=1, durationSecond=2)
        active = True

        while active:
            active = counter.count()


    def testCountDownUnthreadedMode(self):
        counter = ThreadedTimeCounter(mode=ThreadedTimeCounter.MODE_COUNT_DOWN, intervalSecond=1, durationSecond=2)
        active = True

        while active:
            active = counter.count()


    def testCountUpThreadedMode(self):
        counter = ThreadedTimeCounter(mode=ThreadedTimeCounter.MODE_COUNT_UP, intervalSecond=1, durationSecond=2)
        counter.start()


    def testCountDownThreadedMode(self):
        counter = ThreadedTimeCounter(mode=ThreadedTimeCounter.MODE_COUNT_DOWN, intervalSecond=1, durationSecond=2)
        counter.start()


if __name__ == '__main__':
    unittest.main()