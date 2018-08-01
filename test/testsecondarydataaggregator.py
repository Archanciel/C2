import unittest
import os,sys,inspect
import csv
from io import StringIO

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from observer.secondarydataaggregator import SecondaryDataAggregator

class TestSecondaryDataAggregator(unittest.TestCase):
    def testCalculateStartTimestamp(self):
        csvSecondaryDataFileName = "secondary-2018-07-31-20-56-05.csv"
        aggregator = SecondaryDataAggregator(csvSecondaryDataFileName)

        testTsMilliSec = 1533063366209

        self.assertEqual(1533063367000, aggregator.calculateStartTimestamp(testTsMilliSec))
        aggregator.close()

if __name__ == '__main__':
    unittest.main()