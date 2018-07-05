import unittest
import os,sys,inspect
import csv

DUMMY_HEADER = ["DUMMY HEADER 1", "DUMMY HEADER 2"]

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from observable.archiveddatasource import ArchivedDatasource
from observer.secondarydataaggregator import SecondaryDataAggregator

class TestArchivedDatasource(unittest.TestCase):

    def testProcessArchivedData(self):
        csvPrimaryDataFileName = "../primary.csv"
        csvSecondaryDataFileName = "secondary.csv"
        archivedDatasource = ArchivedDatasource(csvPrimaryDataFileName)
        archivedDatasource.addObserver(SecondaryDataAggregator(csvSecondaryDataFileName, isVerbose=False))
        archivedDatasource.processArchivedData()

        with open(csvPrimaryDataFileName, 'r') as csvPrimaryFile:
            with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
                i, j = 0, 0
                for i, _ in enumerate(csvPrimaryFile):
                    pass
                for j, _ in enumerate(csvSecondaryFile):
                    pass
                self.assertEqual(i, j)

        os.remove(csvSecondaryDataFileName)

if __name__ == '__main__':
    unittest.main()