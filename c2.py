import sys
import argparse
import arrow
import msvcrt   # only ok on Windows !

from observable.binancedatasource import BinanceDatasource
from observable.archiveddatasource import ArchivedDatasource
from observer.archiver import Archiver
from observer.secondarydataaggregator import SecondaryDataAggregator
from utility.patternmatcher import PatternMatcher
from utility.threadedtimecounter import ThreadedTimeCounter

VERSION_NUMBER = "0.5"
LOCAL_TIME_ZONE = 'Europe/Zurich'

class Controller:
    '''
    This class is the entry point of the C2 application.

    :seqdiag_note Entry point of the C2 application. When started at the commandline, accepts parameters like RT or simulation mode.
    '''
    DATE_TIME_FORMAT_ARROW = 'YYYY-MM-DD-HH-mm-ss'
    DEFAULT_PRIMARY_FILENAME = 'primary'
    DEFAULT_SECONDARY_FILENAME = 'secondary'

    def __init__(self):
        '''
        Initiate a Controller for the passed trading pair.

        :param tradingPair: example: 'BTCUSDT'
        '''
        self.datasource = None
        self.primaryDataFileName = None
        self.secondaryDataFileName = None
        self.stopped = False


    def getCommandLineArgs(self, argList):
        '''
        Uses argparse to acquire the user optional command line arguments.

        :param argList: were acquired from sys.argv or set by test code

        :return: execution mode, primary data file name, secondary data file name
        '''
        parser = argparse.ArgumentParser(
            description="Version {}. Executes C2 either in real time or simulation mode. " \
                        "In both mode, the secondary data are sent to the Criterion for " \
                        "computing if an alarm is to be raised. " \
                        "In this version, the trading pair is forced to BTCUSDT and real time " \
                        "data come from the Binance exchange. "
                        "In real time mode, both primary and secondary data files are generated. " \
                        "In simulation mode, the primary data are read from the specified primary " \
                        "data file. The secondary data file is recreated at each simulation run. " \
                        "In both modes, the user can specify the output data file names. The final names are " \
                        "suffixed with the execution local date and time. " \
                        "In case no file names are provided, defaults are used, for example " \
                        "primary-YYYY.MM.DD-HH:MM:SS and secondary-YYYY.MM.DD-HH:SS. In any mode, " \
                        "the YYYY-MM-DD-HH:MM:SS secondary data file suffix is equal to the corresponding " \
                        "primary data file date suffix.".format(VERSION_NUMBER)
        )
        parser.add_argument("-m", choices=['r', 's'], required=True,
                            help="specifies the mode, r for real time, s for simulation")
        parser.add_argument("-d", "--duration", nargs="?",
                            help="specifies the duration of the real time data reception in seconds")
        parser.add_argument("-p", "--primary", nargs="?", default=self.DEFAULT_PRIMARY_FILENAME,
                            help="specifies a primary data file name. In real time mode, optional, " \
                                 "in simulation mode, mandatory. A YYYY-MM-DD-HH-MM-SS suffix will be added to the file " \
                                 "name. Extension will be .csv")
        parser.add_argument("-s", "--secondary", nargs="?", default=self.DEFAULT_SECONDARY_FILENAME,
                            help="specifies an optional secondary data file name. The YYYY-MM-DD-HH-MM-SS suffix of the " \
                                 "source primary data file name will be added to the secondary file name. " \
                                 "Extension will be .csv")
        parser.add_argument("-v", action='store_true',
                            help="verbose flag. If -v is specified, C2 outputs in the console each received/handled data " \
                                 "element ")
        args = parser.parse_args(argList)

        return args.m, args.duration, args.primary, args.secondary, args.v

    def start(self, commandLineArgs=None):
        '''
        Start the data stream.

        :param commandLineArgs: used only for unit testing only
        :return: error message if relevant
        '''
        isUnitTestMode = False

        if commandLineArgs == None:
            #here, we are not in unit test mode and we collect the parms entered
            #by the user on the command line
            commandLineArgs = sys.argv[1:]
        else:
            isUnitTestMode = True

        executionMode, durationStr, primaryFileName, secondaryFileName, isVerbose = self.getCommandLineArgs(commandLineArgs)
        localNow = arrow.now(LOCAL_TIME_ZONE)

        if executionMode.upper() == 'R':
            #C2 executing in real time mode ...
            tradingPair = 'BTCUSDT'
            print('Starting the Binance aggregate trade stream for pair {}. Type any key to stop the stream ...'.format(
                tradingPair))
            self.datasource = BinanceDatasource(tradingPair)
            dateTimeStr = localNow.format(self.DATE_TIME_FORMAT_ARROW)

            #adding an Archiver to store on disk the primary data
            self.primaryDataFileName = self.buildPrimaryFileName(primaryFileName, dateTimeStr)
            self.datasource.addObserver(Archiver(self.primaryDataFileName, Archiver.PRIMARY_DATA_CSV_ROW_HEADER, isVerbose))

            #adding a Notifyer to compute the secondary data, store them on disk and send
            #them to the Criterion
            csvSecondaryDataFileName = "{}-{}.csv".format(secondaryFileName, dateTimeStr)
            #forcing isVerbose to False to avoid interfering with Archiver verbosity !
            self.datasource.addObserver(SecondaryDataAggregator(csvSecondaryDataFileName, isVerbose=False))

            self.datasource.startDataReception()
            counter = None

            if durationStr:
                counter = ThreadedTimeCounter(ThreadedTimeCounter.MODE_COUNT_DOWN, \
                                              intervalSecond=1, \
                                              durationSecond=self.getDurationSeconds(durationStr), \
                                              client=self)

            if not isUnitTestMode or durationStr != None:
                #here, we are not in unit test mode and we have to wait for the user to
                #stop receiving the real time data

                if counter:
                    counter.start()

                while not self.stopped:
                    if msvcrt.kbhit():
                        if counter:
                            counter.stop()
                            print('\nStopping the stream ...')
                        else:
                            print('Stopping the stream ...')
                        c2.stop()

                sys.exit(0)  # required for the program to exit !
        else:
            #C2 executing in simulation mode ...
            if primaryFileName == self.DEFAULT_PRIMARY_FILENAME:
                errorMsg = "ERROR - in simulation mode, a primary file name must be provided !"
                print(errorMsg)

                return errorMsg

            csvSecondaryDataFileName = self.buildSecondaryFileNameFromPrimaryFileName(primaryFileName,
                                                                                      secondaryFileName)
            try:
                self.datasource = ArchivedDatasource(primaryFileName)
            except FileNotFoundError as e:
                errorMsg = "ERROR - specified file {} not found !".format(e.filename)
                print(errorMsg)
                return errorMsg

            self.datasource.addObserver(SecondaryDataAggregator(csvSecondaryDataFileName, isVerbose))
            self.datasource.processArchivedData()

    def getDurationSeconds(self, durationStr):
        return int(durationStr)

    def buildSecondaryFileNameFromPrimaryFileName(self, primaryFileName, secondaryFileName):
        dateTimeStr = PatternMatcher.extractDateTimeStrFrom(primaryFileName)
        if dateTimeStr:
            csvSecondaryDataFileName = "{}-{}.csv".format(secondaryFileName, dateTimeStr)
        else:
            csvSecondaryDataFileName = "{}.csv".format(secondaryFileName)

        return csvSecondaryDataFileName


    def buildPrimaryFileName(self, primaryFileName, dateSuffix):
        return "{}-{}.csv".format(primaryFileName, dateSuffix)


    def stop(self):
        '''
        Stop the data stream.
        :return: created primary csv file name if started in real time mode
        '''
        self.datasource.stopObservable()
        self.stopped = True

        return self.primaryDataFileName


    def wasStopped(self):
        return self.stopped


if __name__ == '__main__':
    tradingPair = 'BTCUSDT'
    c2 = Controller()
    c2.start()

