import unittest
import os,sys,inspect
import csv

DUMMY_HEADER = ["DUMMY HEADER 1", "DUMMY HEADER 2"]

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from observable.archiveddatasource import ArchivedDatasource
from observer.secondarydataaggregator import SecondaryDataAggregator
from observer.observer import Observer

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


    def testProcessArchivedDataValues(self):
        csvPrimaryDataFileName = "../primary.csv"
        archivedDatasource = ArchivedDatasource(csvPrimaryDataFileName)

        class TestObserver(Observer):
            def __init__(self):
                self.receivedDataList = []
            def update(self, arg):
                self.receivedDataList.append(arg)
            def close(self):
                pass

        tstObserver = TestObserver()
        archivedDatasource.addObserver(tstObserver)
        archivedDatasource.processArchivedData()

        self.assertEqual(tstObserver.receivedDataList[0], ('1','1530201849627', '6103.0', '0.100402'))
        self.assertEqual(tstObserver.receivedDataList[1], ('2','1530201851230', '6103.99', '0.03'))

if __name__ == '__main__':
    unittest.main()