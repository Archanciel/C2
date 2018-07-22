import unittest
import os,sys,inspect
import csv
import time

DUMMY_HEADER = ["DUMMY HEADER 1", "DUMMY HEADER 2"]

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from c2 import Controller
from documentation.seqdiagbuilder import SeqDiagBuilder

class TestController(unittest.TestCase):

    def setUp(self):
        self.projectPath = 'D:\\Development\\Python\\C2'

    @unittest.skip
    def testStartModeRealtime(self):
        '''
        this causes testStartModeRealtimeWithDurationInSeconds to fail !!!
        :return:
        '''
        controller = Controller()
        print("running c2 in real time mode for 10 seconds")

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-mr'])
        time.sleep(2)
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


    def testStartModeRealtimeWithDurationInSeconds(self):
        controller = Controller()
        duration = 3
        print("running c2 in real time mode for {} seconds".format(duration))

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        try:
            controller.start(['-mr', '-d{}'.format(duration)])
        except SystemExit:
            pass

        csvPrimaryDataFileName = controller.primaryDataFileName
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


    @unittest.skip
    def testStartModeRealtimeWithDurationInSecondsBuildSeqDiag(self):
        controller = Controller()
        duration = 2
        print("running c2 in real time mode for {} seconds".format(duration))

        SeqDiagBuilder.activate(self.projectPath, 'Controller', 'start')  # activate sequence diagram building

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        try:
            controller.start(['-mr', '-d{}'.format(duration)])
            time.sleep(duration)
        except SystemExit:
            pass

        csvPrimaryDataFileName = controller.primaryDataFileName
        csvSecondaryDataFileName = controller.buildSecondaryFileNameFromPrimaryFileName(csvPrimaryDataFileName, "secondary")

        os.remove(csvPrimaryDataFileName)
        os.remove(csvSecondaryDataFileName)

        commands = SeqDiagBuilder.createSeqDiaqCommands('USER')

        with open("c:\\temp\\ess.txt", "w") as f:
            f.write(commands)

        SeqDiagBuilder.deactivate()  # deactivate sequence diagram building


    def testStartModeSimulation(self):
        csvPrimaryDataFileName = "primary-2018-06-28-22-41-05.csv"
        csvSecondaryDataFileName = "secondary-2018-06-28-22-41-05.csv"
        controller = Controller()

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

        os.remove(csvSecondaryDataFileName)


    def testStartModeSimulationBuildSeqDiag(self):
        csvPrimaryDataFileName = "primary-one.csv"
        csvSecondaryDataFileName = "secondary.csv"
        controller = Controller()
        classCtorArgsDic = {'ArchivedDatasource': ['primary-one.csv'], 'SecondaryDataAggregator': ['secondary.csv', False], 'Archiver': ['secondary.csv', False]}

        SeqDiagBuilder.activate(self.projectPath, 'Controller', 'start', classCtorArgsDic)  # activate sequence diagram building

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])
        controller.stop()

        os.remove(csvSecondaryDataFileName)

        commands = SeqDiagBuilder.createSeqDiaqCommands('USER', maxSigArgNum=None, maxSigCharLen=30)

        with open("c:\\temp\\C2 Simulation mode sequence diagram.txt", "w") as f:
            f.write(commands)

        SeqDiagBuilder.deactivate()  # deactivate sequence diagram building

        self.assertEqual(
'''@startuml

actor USER
participant Controller
	note over of Controller
		Entry point of the C2 application. When
		started at the commandline, accepts
		parameters like RT or simulation mode.
	end note
participant ArchivedDatasource
	note over of ArchivedDatasource
		Reads data from a primary data file in
		simulation mode.
	end note
participant Observable
	note over of Observable
		Pivot class in the Observable design pattern.
	end note
participant SecondaryDataAggregator
	note over of SecondaryDataAggregator
		Implements the Observer part in the
		Observable design pattern. Calculates the
		secondary data and sends them one by one to
		the Criterion.
	end note
participant Archiver
	note over of Archiver
		Implements the Observer part in the
		Observable design pattern. Writes either
		primary or secondary data on disk.
	end note
participant PriceVolumeCriterion
	note over of PriceVolumeCriterion
		Responsible of computing if an alarm must be
		raised.
	end note
USER -> Controller: start(commandLineArgs=None)
	activate Controller
	Controller -> ArchivedDatasource: processArchivedData()
		activate ArchivedDatasource
		ArchivedDatasource -> Observable: notifyObservers(data)
			activate Observable
			Observable -> SecondaryDataAggregator: update(data)
				activate SecondaryDataAggregator
				SecondaryDataAggregator -> SecondaryDataAggregator: aggregateSecondaryData(timestampMilliSec, ...)
					activate SecondaryDataAggregator
					note right
						method to be implemented by Philippe
					end note
					SecondaryDataAggregator <-- SecondaryDataAggregator: 
					deactivate SecondaryDataAggregator
				SecondaryDataAggregator -> Archiver: update(data)
					activate Archiver
					SecondaryDataAggregator <-- Archiver: 
					deactivate Archiver
				SecondaryDataAggregator -> PriceVolumeCriterion: check(data)
					activate PriceVolumeCriterion
					note right
						method to be implemented by Philippe
					end note
					SecondaryDataAggregator <-- PriceVolumeCriterion: 
					deactivate PriceVolumeCriterion
				Observable <-- SecondaryDataAggregator: 
				deactivate SecondaryDataAggregator
			ArchivedDatasource <-- Observable: 
			deactivate Observable
		Controller <-- ArchivedDatasource: 
		deactivate ArchivedDatasource
	USER <-- Controller: 
	deactivate Controller
@enduml''', commands)


    def testStartModeSimulationNoPrimaryFileSpecification(self):
        csvPrimaryDataFileName = "primary.csv"
        csvSecondaryDataFileName = "secondary-2018-06-28-22-41-05.csv"
        controller = Controller()

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        errorMsg = controller.start(['-ms', '-s{}'.format(csvSecondaryDataFileName)])

        self.assertEqual(errorMsg, "ERROR - in simulation mode, a primary file name must be provided !")


    def testStartModeSimulationPrimaryFileWithNoDateSpecification(self):
        csvPrimaryDataFileName = "../primary.csv"
        csvSecondaryDataFileName = "secondary.csv"
        controller = Controller()

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

        os.remove(csvSecondaryDataFileName)


    def testStartModeSimulationPrimaryFileNotExist(self):
        csvPrimaryDataFileName = "../primary.cs"
        csvSecondaryDataFileName = "secondary.csv"
        controller = Controller()

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        errorMsg = controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])

        self.assertTrue("ERROR - specified file ../primary.cs not found !", errorMsg)


    def testBuildPrimaryFileName(self):
        dateTimeStr = "2018-06-28 22-41-05"
        controller = Controller()
        primaryFileNameRoot = "primary"
        csvPrimaryDataFileName = "primary-2018-06-28 22-41-05.csv"

        self.assertEqual(csvPrimaryDataFileName, controller.buildPrimaryFileName(primaryFileNameRoot, dateTimeStr))


if __name__ == '__main__':
    unittest.main()