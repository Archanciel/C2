import unittest
import os,sys,inspect
import csv
import time

DUMMY_HEADER = ["DUMMY HEADER 1", "DUMMY HEADER 2"]

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from c2 import Controller

class TestController(unittest.TestCase):

    def testStartModeRealtime(self):
        controller = Controller()
        print("running c2 in real time mode for 10 seconds")

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-mr'])
        time.sleep(10)
        csvPrimaryDataFileName = controller.stop()
        csvSecondaryDataFileName = controller.buildSecondaryFileNameFromPrimaryFileName(csvPrimaryDataFileName, "secondary")

        with open(csvPrimaryDataFileName, 'r') as csvPrimaryFile:
            with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
                i, j = 0, 0
                for i, _ in enumerate(csvPrimaryFile):
                    pass
                for j, _ in enumerate(csvSecondaryFile):
                    pass
                self.assertEqual(i, j)

        self.assertTrue(os.path.isfile(csvPrimaryDataFileName))

        os.remove(csvPrimaryDataFileName)
        os.remove(csvSecondaryDataFileName)


    def testStartModeSimulation(self):
        csvPrimaryDataFileName = "primary-2018-06-28-22-41-05.csv"
        csvSecondaryDataFileName = "secondary-2018-06-28-22-41-05.csv"
        controller = Controller()
        print("running c2 in simulation mode")

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])
        controller.stop()

        self.assertTrue(os.path.isfile(csvSecondaryDataFileName))
        with open(csvPrimaryDataFileName, 'r') as csvPrimaryFile:
            with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
                i, j = 0, 0
                for i, _ in enumerate(csvPrimaryFile):
                    pass
                for j, _ in enumerate(csvSecondaryFile):
                    pass
                self.assertEqual(i, j)


    def testBuildPrimaryFileName(self):
        dateTimeStr = "2018-06-28 22-41-05"
        controller = Controller()
        primaryFileNameRoot = "primary"
        csvPrimaryDataFileName = "primary-2018-06-28 22-41-05.csv"

        self.assertEqual(csvPrimaryDataFileName, controller.buildPrimaryFileName(primaryFileNameRoot, dateTimeStr))


if __name__ == '__main__':
    unittest.main()