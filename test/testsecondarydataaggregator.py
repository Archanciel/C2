import unittest
import os,sys,inspect
import csv
from io import StringIO

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from observer.secondarydataaggregator import SecondaryDataAggregator
from c2 import Controller

class TestSecondaryDataAggregator(unittest.TestCase):
    def testCalculateStartTimestamp(self):
        csvSecondaryDataFileName = "secondary-2018-07-31-20-56-05.csv"
        aggregator = SecondaryDataAggregator(csvSecondaryDataFileName)

        testTsMilliSec = 1533063366209

        self.assertEqual(1533063367000, aggregator.calculateStartTimestamp(testTsMilliSec))
        aggregator.close()

    def testSecDataGenerationInSimulationModeA(self):
        csvPrimaryDataFileName = "primary-a.csv"
        csvSecondaryDataFileName = "secondary.csv"
        csvExpectedSecondaryDataFileName = "expected-secondary-a.csv"
        controller = Controller()

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])
        controller.stop()

        self.assertTrue(os.path.isfile(csvSecondaryDataFileName))
        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            with open(csvExpectedSecondaryDataFileName, 'r') as csvExpectedSecondaryFile:
                for secondaryFileLine in csvSecondaryFile:
                    expectedSecondaryFileLine = csvExpectedSecondaryFile.readline()
                    self.assertEqual(secondaryFileLine, expectedSecondaryFileLine)

        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            with open(csvExpectedSecondaryDataFileName, 'r') as csvExpectedSecondaryFile:
                secondaryRecordsNumber, expectedSecondaryRecordsNumber = 0, 0
                for secondaryRecordsNumber, _ in enumerate(csvSecondaryFile):
                    pass
                for expectedSecondaryRecordsNumber, _ in enumerate(csvExpectedSecondaryFile):
                    pass
                self.assertEqual(secondaryRecordsNumber, expectedSecondaryRecordsNumber)

        os.remove(csvSecondaryDataFileName)

    def testSecDataGenerationInSimulationModeB(self):
        csvPrimaryDataFileName = "primary-b.csv"
        csvSecondaryDataFileName = "secondary.csv"
        csvExpectedSecondaryDataFileName = "expected-secondary-b.csv"
        controller = Controller()

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])
        controller.stop()

        self.assertTrue(os.path.isfile(csvSecondaryDataFileName))
        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            with open(csvExpectedSecondaryDataFileName, 'r') as csvExpectedSecondaryFile:
                for secondaryFileLine in csvSecondaryFile:
                    expectedSecondaryFileLine = csvExpectedSecondaryFile.readline()
                    self.assertEqual(secondaryFileLine, expectedSecondaryFileLine)

        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            with open(csvExpectedSecondaryDataFileName, 'r') as csvExpectedSecondaryFile:
                secondaryRecordsNumber, expectedSecondaryRecordsNumber = 0, 0
                for secondaryRecordsNumber, _ in enumerate(csvSecondaryFile):
                    pass
                for expectedSecondaryRecordsNumber, _ in enumerate(csvExpectedSecondaryFile):
                    pass
                self.assertEqual(secondaryRecordsNumber, expectedSecondaryRecordsNumber)

        os.remove(csvSecondaryDataFileName)

    def testSecDataGenerationInSimulationModeAB(self):
        csvPrimaryDataFileName = "primary-ab.csv"
        csvSecondaryDataFileName = "secondary.csv"
        csvExpectedSecondaryDataFileName = "expected-secondary-ab.csv"
        controller = Controller()

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])
        controller.stop()

        self.assertTrue(os.path.isfile(csvSecondaryDataFileName))
        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            with open(csvExpectedSecondaryDataFileName, 'r') as csvExpectedSecondaryFile:
                for secondaryFileLine in csvSecondaryFile:
                    expectedSecondaryFileLine = csvExpectedSecondaryFile.readline()
                    self.assertEqual(secondaryFileLine, expectedSecondaryFileLine)

        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            with open(csvExpectedSecondaryDataFileName, 'r') as csvExpectedSecondaryFile:
                secondaryRecordsNumber, expectedSecondaryRecordsNumber = 0, 0
                for secondaryRecordsNumber, _ in enumerate(csvSecondaryFile):
                    pass
                for expectedSecondaryRecordsNumber, _ in enumerate(csvExpectedSecondaryFile):
                    pass
                self.assertEqual(secondaryRecordsNumber, expectedSecondaryRecordsNumber)

        os.remove(csvSecondaryDataFileName)

if __name__ == '__main__':
    unittest.main()