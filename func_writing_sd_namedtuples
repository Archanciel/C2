import csv
import os
import collections

#SHOWING USAGE OF PYTHON COLLECTIONS.NAMEDTUPLES
SdLine = collections.namedtuple('SdLine',['index','timestamp','volume','price','critData1','critData2'])
sdLineList = [SdLine(1,1533063366209,0.008764,7735.00,0,0),
              SdLine(2,1533063367343,0.000017,7734.99,0,0)]

print("idx\tvolume\t\tprice\tcritData1")
for namedTuple in sdLineList:
    print("{0}\t{1:.7f}\t{2:.2f}\t{3}".format(namedTuple.index, namedTuple.volume, namedTuple.price, namedTuple.critData1))
    
#USING NAMED TUPPLE AS ARGUMENT FOR FUNCTION
#WRITESDTOCSV() DEFINED BELOW

def writeSdToCsv(csvWriter, sdNamedTuple):
    '''
    This function writes the secondary
    data passed to it as a named tuple
    to the passed csv writer
    '''
    csvWriter.writerow([sdNamedTuple.index,sdNamedTuple.trades,sdNamedTuple.timestamp,sdNamedTuple.volume,sdNamedTuple.price,sdNamedTuple.critData1,sdNamedTuple.critData2])

#opening pd_reader on file primary.csv
#located in same dir as the current 
#python file
dir_path = os.path.dirname(os.path.realpath(__file__))
primaryFileName = "primary.csv"
pd_file = open(dir_path + "/" + primaryFileName, 'r')
pd_reader = csv.reader(pd_file, delimiter='\t')

#creating sd_writer on file secondary.csv
#located in same dir as the current 
#python file

secondaryFileName = "secondary.csv"
sd_file = open(dir_path + "/" + secondaryFileName, 'w')
sd_writer = csv.writer(sd_file, delimiter='\t')

#read the pd csv header line
next(pd_reader)

#define the sd named tuple
SdLine = collections.namedtuple('SdLine',['index','trades','timestamp','volume','price','critData1','critData2'])

#create the sd csv file header
#and writing it to the csv file
sdCsvFileHeader = ["IDX", "TRD", "TIMESTAMP (MS)", "VOLUME", "PRICE","CRITDATA1","CRITDATA2"]
sd_writer.writerow(sdCsvFileHeader)

#now, iterating on primary.csv data

idx = 0

for pd in pd_reader:
    idx += 1
    #here, you would calculate your
    #sd data values. For demonstration,
    #I simply state that a sd is
    #a pd plus criterion data, which 
    #is perfectly nonsensical !
    
    #creating a named tuple which is
    #then passed as arg of the function
    sd = SdLine(idx,pd[0],pd[1],pd[2],pd[3],0,0)
    writeSdToCsv(sd_writer, sd)
    
print('\nfinished writing sd in file ' + dir_path + "/" + secondaryFileName)
