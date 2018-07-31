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
                primaryRecordsNumber, secondaryRecordsNumber = 0, 0
                for primaryRecordsNumber, _ in enumerate(csvPrimaryFile):
                    pass
                for secondaryRecordsNumber, _ in enumerate(csvSecondaryFile):
                    pass
                self.assertEqual(primaryRecordsNumber, 25)
                self.assertEqual(secondaryRecordsNumber, 12)

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

        self.assertEqual(tstObserver.receivedDataList[0], ('1', '1533063366209', '0.008764', '7735.00'))
        self.assertEqual(tstObserver.receivedDataList[1], ('2', '1533063367343', '0.000017', '7734.99'))

if __name__ == '__main__':
    unittest.main()