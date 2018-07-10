import unittest
import os,sys,inspect
import csv

DUMMY_HEADER = ["DUMMY HEADER 1", "DUMMY HEADER 2"]

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from observer.archiver import Archiver

class TestArchiver(unittest.TestCase):

    def testInitCloseCycle(self):
        csvFileName = "test.csv"
        archiver = Archiver(csvFileName, isVerbose=False)
        archiver.close()

        with open(csvFileName, 'r') as csvFile:
            csvReader = csv.reader(csvFile)
            self.assertEqual(Archiver.CSV_ROW_HEADER, next(csvReader))

        os.remove(csvFileName)


    def testInitCloseCycleOverwritingExistingFile(self):
        #creating a csv file which will be overwritten
        csvFileName = "test.csv"

        with open(csvFileName, 'w') as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow(DUMMY_HEADER)

        with open(csvFileName, 'r') as csvFile:
            csvReader = csv.reader(csvFile)
            self.assertEqual(DUMMY_HEADER, next(csvReader))

        #now, instanciating the Archiver and checking the csv file was overwritten
        archiver = Archiver(csvFileName, isVerbose=False)
        archiver.close()

        with open(csvFileName, 'r') as csvFile:
            csvReader = csv.reader(csvFile)
            self.assertEqual(Archiver.CSV_ROW_HEADER, next(csvReader))

        os.remove(csvFileName)


    def testUpdate(self):
        csvFileName = "test.csv"
        archiver = Archiver(csvFileName, isVerbose=False)
        archiver.update((1530201849627,6103.0,0.100402))
        archiver.update((1530201851230,6103.99,0.03))
        archiver.close()

        with open(csvFileName, 'r') as csvFile:
            csvReader = csv.reader(csvFile)
            self.assertEqual(Archiver.CSV_ROW_HEADER, next(csvReader))
            self.assertEqual(['1','1530201849627','6103.0','0.100402'], next(csvReader))
            self.assertEqual(['2','1530201851230','6103.99','0.03'], next(csvReader))

        os.remove(csvFileName)


if __name__ == '__main__':
    unittest.main()