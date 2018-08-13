import unittest
import os,sys,inspect
import csv
import time
from io import StringIO

DUMMY_HEADER = ["DUMMY HEADER 1", "DUMMY HEADER 2"]

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from c2 import Controller
from documentation.seqdiagbuilder import SeqDiagBuilder

class TestController(unittest.TestCase):

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
            header = csvPrimaryFile.readline()
            self.assertEqual(header, 'IDX	TIMESTAMP (MS)	VOLUME\tPRICE\n')
        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            header = csvSecondaryFile.readline()
            self.assertEqual(header, 'IDX	TRD\tTIMESTAMP (MS)	VOLUME\tPRICE\n')

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
            header = csvPrimaryFile.readline()
            self.assertEqual(header, 'IDX	TIMESTAMP (MS)	VOLUME\tPRICE\n')
        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            header = csvSecondaryFile.readline()
            self.assertEqual(header, 'IDX	TRD\tTIMESTAMP (MS)	VOLUME\tPRICE\n')

        self.assertTrue(os.path.isfile(csvPrimaryDataFileName))

        os.remove(csvPrimaryDataFileName)
        os.remove(csvSecondaryDataFileName)


    def testStartModeRTFolowedBySimulation(self):
        '''
        Start C2 in RT for 3 seconds. Then launch C2 in simulation mode on the generated primary
        file and ensure the secondary data generated at the RT and simulation steps are identical.
        :return:
        '''
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

        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            sdFromRT = csvSecondaryFile.readlines()

        self.assertTrue(os.path.isfile(csvPrimaryDataFileName))

        controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])
        controller.stop()

        with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
            sdFromSimulation = csvSecondaryFile.readlines()

        self.assertEqual(sdFromRT, sdFromSimulation)

        os.remove(csvPrimaryDataFileName)
        os.remove(csvSecondaryDataFileName)


    @unittest.skip
    def testStartModeRealtimeWithDurationInSecondsBuildSeqDiag(self):
        controller = Controller()
        duration = 2
        print("running c2 in real time mode for {} seconds".format(duration))

        SeqDiagBuilder.activate(parentdir, 'Controller', 'start')  # activate sequence diagram building

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
        csvPrimaryDataFileName = "primary-2018-07-31-20-56-05.csv"
        csvSecondaryDataFileName = "secondary-2018-07-31-20-56-05.csv"
        controller = Controller()

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])
        controller.stop()

        self.assertTrue(os.path.isfile(csvSecondaryDataFileName))
        with open(csvPrimaryDataFileName, 'r') as csvPrimaryFile:
            with open(csvSecondaryDataFileName, 'r') as csvSecondaryFile:
                primaryRecordsNumber, secondaryRecordsNumber = 0, 0
                for primaryRecordsNumber, _ in enumerate(csvPrimaryFile):
                    pass
                for secondaryRecordsNumber, _ in enumerate(csvSecondaryFile):
                    pass
                self.assertEqual(primaryRecordsNumber, 25)
                self.assertEqual(secondaryRecordsNumber, 10)

        os.remove(csvSecondaryDataFileName)

    def testStartModeSimulationBuildSeqDiag(self):
        if os.name == 'posix':
            # running on Android
            return

        csvPrimaryDataFileName = "primary-seqdiag.csv"
        csvSecondaryDataFileName = "secondary.csv"
        controller = Controller()
        classCtorArgsDic = {'ArchivedDatasource': ['primary-seqdiag.csv'], 'SecondaryDataAggregator': ['secondary.csv', False], 'Archiver': ['secondary.csv', 'csv dummy col titles', False]}

        SeqDiagBuilder.activate(parentdir, 'Controller', 'start', classCtorArgsDic)  # activate sequence diagram building

        #IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        controller.start(['-ms', '-p{}'.format(csvPrimaryDataFileName)])

        os.remove(csvSecondaryDataFileName)

        commands = SeqDiagBuilder.createSeqDiaqCommands(actorName='USER', title='C2 simulation mode sequence diagram', maxSigArgNum=None, maxSigCharLen=15, maxNoteCharLen=23)

        with open("c:\\temp\\C2 Simulation mode sequence diagram.txt", "w") as f:
            f.write(commands)

        SeqDiagBuilder.deactivate()  # deactivate sequence diagram building

        self.assertEqual(
'''@startuml

title C2 simulation mode sequence diagram
actor USER
participant Controller
	/note over of Controller
		Entry point of the C2 application.
		When started at the commandline,
		accepts parameters like RT or
		simulation mode.
	end note
participant ArchivedDatasource
	/note over of ArchivedDatasource
		In simulation mode, reads data
		line by line from a primary data
		file. For every data line read,
		calls the notifyObservers(data)
		method of its parent class,
		Observable.
	end note
participant Observable
	/note over of Observable
		Pivot class in the Observable
		design pattern. Each time its
		notifyObservers(data) method is
		called, Observable notifies its
		subscribed Observers of the
		received data calling update(data)
		on each registered Observer.
	end note
participant SecondaryDataAggregator
	/note over of SecondaryDataAggregator
		Implements the Observer part in
		the Observable design pattern.
		Each tima its update(data) method
		is called, it adds this data to
		the current secondary aggreagated
		data and sends the secondary data
		when appropriate to the Criterion
		calling its check() method.
	end note
participant PriceVolumeCriterion
	/note over of PriceVolumeCriterion
		Inherits from Criterion. Is
		responsible for computing if an
		alarm must be raised. Performs its
		calculation each time its check()
		method is called.
	end note
participant Archiver
	/note over of Archiver
		In simulation mode, this Observer
		(Archiver, like SecondaryData
		Aggregator, inherits from
		Observer) writes the secondary
		data on disk. In real time mode,
		saves on disk the primary data.
	end note
USER -> Controller: start(...)
	activate Controller
	Controller -> ArchivedDatasource: processArchivedData()
		activate ArchivedDatasource
		ArchivedDatasource -> Observable: notifyObservers(data)
			activate Observable
			Observable -> SecondaryDataAggregator: update(data)
				activate SecondaryDataAggregator
				SecondaryDataAggregator -> SecondaryDataAggregator: aggregateSecondaryData(...)
					activate SecondaryDataAggregator
					note right
						method to be implemented by
						Philippe
					end note
					SecondaryDataAggregator <-- SecondaryDataAggregator: 
					deactivate SecondaryDataAggregator
				SecondaryDataAggregator -> PriceVolumeCriterion: check(data)
					activate PriceVolumeCriterion
					note right
						method to be implemented by
						Philippe
					end note
					SecondaryDataAggregator <-- PriceVolumeCriterion: 
					deactivate PriceVolumeCriterion
				SecondaryDataAggregator -> SecondaryDataAggregator: storeAndPrintSecondaryData(...)
					activate SecondaryDataAggregator
					SecondaryDataAggregator -> Archiver: update(data)
						activate Archiver
						SecondaryDataAggregator <-- Archiver: 
						deactivate Archiver
					SecondaryDataAggregator <-- SecondaryDataAggregator: 
					deactivate SecondaryDataAggregator
				Observable <-- SecondaryDataAggregator: 
				deactivate SecondaryDataAggregator
			ArchivedDatasource <-- Observable: 
			deactivate Observable
		Controller <-- ArchivedDatasource: 
		deactivate ArchivedDatasource
	USER <-- Controller: 
	deactivate Controller
@enduml''', commands)

    @unittest.skip
    def testStartModeRTBuildSeqDiag(self):
        controller = Controller()
        classCtorArgsDic = {'ArchivedDatasource': ['primary-two.csv'],
                            'SecondaryDataAggregator': ['secondary.csv', False],
                            'Archiver': ['secondary.csv', 'csv dummy col titles', False]}

        # SeqDiagBuilder.activate(parentdir, 'Controller', 'start',
        #                         classCtorArgsDic)  # activate sequence diagram building

        duration = 3

        # IMPORTANT: when forcing execution parms, no space separate parm name and parm value !
        try:
            controller.start(['-mr', '-d{}'.format(duration)])
        except SystemExit:
            pass

        while not controller.wasStopped():
            print('controller still working')

        csvPrimaryDataFileName = controller.primaryDataFileName
        csvSecondaryDataFileName = controller.buildSecondaryFileNameFromPrimaryFileName(csvPrimaryDataFileName, "secondary")

        commands = SeqDiagBuilder.createSeqDiaqCommands(actorName='USER',
                                                        title='C2 simulation mode sequence diagram',
                                                        maxSigArgNum=None, maxSigCharLen=15, maxNoteCharLen=23)

        with open("c:\\temp\\C2 RT mode sequence diagram.txt", "w") as f:
            f.write(commands)

        SeqDiagBuilder.deactivate()  # deactivate sequence diagram building

        os.remove(csvPrimaryDataFileName)
        os.remove(csvSecondaryDataFileName)

        self.assertEqual(
'''@startuml

title C2 simulation mode sequence diagram
actor USER
participant Controller
    /note over of Controller
        Entry point of the C2 application.
        When started at the commandline,
        accepts parameters like RT or
        simulation mode.
    end note
participant ArchivedDatasource
    /note over of ArchivedDatasource
        In simulation mode, reads data
        line by line from a primary data
        file. For every data line read,
        calls the notifyObservers(data)
        method of its parent class,
        Observable.
    end note
participant Observable
    /note over of Observable
        Pivot class in the Observable
        design pattern. Each time its
        notifyObservers(data) method is
        called, Observable notifies its
        subscribed Observers of the
        received data calling update(data)
        on each registered Observer.
    end note
participant SecondaryDataAggregator
    /note over of SecondaryDataAggregator
        Implements the Observer part in
        the Observable design pattern.
        Each tima its update(data) method
        is called, it adds this data to
        the current secondary aggreagated
        data and sends the secondary data
        when appropriate to the Criterion
        calling its check() method.
    end note
participant PriceVolumeCriterion
    /note over of PriceVolumeCriterion
        Inherits from Criterion. Is
        responsible for computing if an
        alarm must be raised. Performs its
        calculation each time its check()
        method is called.
    end note
participant Archiver
    /note over of Archiver
        In simulation mode, this Observer
        (Archiver, like SecondaryData
        Aggregator, inherits from
        Observer) writes the secondary
        data on disk. In real time mode,
        saves on disk the primary data.
    end note
USER -> Controller: start(...)
    activate Controller
    Controller -> ArchivedDatasource: processArchivedData()
        activate ArchivedDatasource
        ArchivedDatasource -> Observable: notifyObservers(data)
            activate Observable
            Observable -> SecondaryDataAggregator: update(data)
                activate SecondaryDataAggregator
                SecondaryDataAggregator -> SecondaryDataAggregator: aggregateSecondaryData(...)
                    activate SecondaryDataAggregator
                    note right
                        method to be implemented by
                        Philippe
                    end note
                    SecondaryDataAggregator <-- SecondaryDataAggregator: 
                    deactivate SecondaryDataAggregator
                SecondaryDataAggregator -> PriceVolumeCriterion: check(data)
                    activate PriceVolumeCriterion
                    note right
                        method to be implemented by
                        Philippe
                    end note
                    SecondaryDataAggregator <-- PriceVolumeCriterion: 
                    deactivate PriceVolumeCriterion
                SecondaryDataAggregator -> Archiver: update(data)
                    activate Archiver
                    SecondaryDataAggregator <-- Archiver: 
                    deactivate Archiver
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


    @unittest.skip
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