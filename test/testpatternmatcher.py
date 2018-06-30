import unittest
import os,sys,inspect
import csv

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from utility.patternmatcher import PatternMatcher

class TestPatternMatcher(unittest.TestCase):
    def testGetDurationSS(self):
        durationStr = '22'
        durationTuple = PatternMatcher.getDurationStrTuple(durationStr)
        self.assertEqual(1, len(durationTuple))
        self.assertEqual(('22',), durationTuple)

    def testGetDurationMMSS(self):
        durationStr = '17-22'
        durationTuple = PatternMatcher.getDurationStrTuple(durationStr)
        self.assertEqual(2, len(durationTuple))
        self.assertEqual(('17','22'), durationTuple)

    def testGetDurationHHMMSS(self):
        durationStr = '2-7-02'
        durationTuple = PatternMatcher.getDurationStrTuple(durationStr)
        self.assertEqual(3, len(durationTuple))
        self.assertEqual(('2','7','02'), durationTuple)

    def testGetDurationDDHHMMSS(self):
        durationStr = '7-22-0-0'
        durationTuple = PatternMatcher.getDurationStrTuple(durationStr)
        self.assertEqual(4, len(durationTuple))
        self.assertEqual(('7','22','0','0'), durationTuple)

if __name__ == '__main__':
    unittest.main()