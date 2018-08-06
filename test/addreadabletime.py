import csv
import os
from datetime import datetime

SECONDARY_DATA_CSV_ROW_HEADER = ["IDX", "TIMESTAMP (MS)", "READABLE TIME", "VOLUME     ", "PRICE"]

class AddReadableTime():
    '''
    This class reads a primary data csv file line 
    by line and writes the data to a csv file adding
    a readable time string after the millisec timestamp
    '''
    def __init__(self, filename):
        '''
        Constructor.
        :param filename: name of the file to read data from
        '''
        curDir = os.path.dirname(os.path.realpath(__file__)) + '/'

        self.inputFile = open(curDir + filename, 'r')
        self.reader = csv.reader(self.inputFile, delimiter='\t')
        next(self.reader) #read the header line

        self.outputFile = open(curDir + filename + '_r.csv', 'w', newline = '')
        self.writer = csv.writer(self.outputFile, delimiter = '\t')
        self.writer.writerow(SECONDARY_DATA_CSV_ROW_HEADER)
        self.recordIndex = 0

    def convert(self):
        '''
        Addsthe a readable time string
        after the millisec timestamp
        '''
        for row in self.reader:
            self.recordIndex += 1
            recordIndex = row[0]
            timestampMilliSec = row[1]
            volumeFloat = float(row[2])
            priceFloat = float(row[3])
            readableTime = datetime.fromtimestamp(int(timestampMilliSec) / 1000).strftime("%H:%M:%S.%f")
            self.writer.writerow([self.recordIndex, timestampMilliSec, readableTime, "{:.6f}".format(volumeFloat), "{:.2f}".format(priceFloat)])

        self.inputFile.close()
        self.outputFile.close()

if __name__ == '__main__':
    art = AddReadableTime(input('Enter source csv file name: '))
    art.convert()
