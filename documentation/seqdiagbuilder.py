import traceback, re, ast, importlib, inspect
import webbrowser
import os
import copy
from inspect import signature
import collections

BIG_COMMENT_LENGTH = 100

SEQDIAG_RETURN_TAG = ":seqdiag_return"
SEQDIAG_SELECT_METHOD_TAG = ":seqdiag_select_method"
SEQDIAG_NOTE_TAG = ":seqdiag_note"
SEQDIAG_METHOD_RETURN_NOTE_TAG = ":seqdiag_return_note"

SEQDIAG_RETURN_TAG_PATTERN = r"%s (.*)" % SEQDIAG_RETURN_TAG
SEQDIAG_SELECT_METHOD_TAG_PATTERN = r"%s(.*)" % SEQDIAG_SELECT_METHOD_TAG
PYTHON_FILE_AND_FUNC_PATTERN = r"([\w:\\]+\\)(\w+)\.py, line (\d*) in (.*)"
FRAME_PATTERN = r"(?:<FrameSummary file ([\w:\\,._\s]+)(?:>, |>\]))"
SEQDIAG_NOTE_TAG_PATTERN = r"%s (.*)" % SEQDIAG_NOTE_TAG
SEQDIAG_METHOD_RETURN_NOTE_TAG_PATTERN = r"%s (.*)" % SEQDIAG_METHOD_RETURN_NOTE_TAG


TAB_CHAR = '\t'


class FlowEntry:
    def __init__(self, fromClass='', fromMethod='', toClass='', toMethod='', toMethodCalledFromLineNumber='',
                 toSignature='', toMethodNote='', toReturnType='', toReturnNote=''):
        '''

        :param fromClass:                       class containing the fromMethod
        :param fromMethod:                      method calling the toMethod
        :param toClass:                         class containing the toMethod
        :param toMethod:                        method called from the fromMethod
        :param toMethodCalledFromLineNumber:    line number in the fromMethod from which
                                                the toMethod was called
        :param toSignature:                     toMethod signature
        :param toMethodNote                     toMethod note
        :param toReturnType:                    return type of the toMethod
        :param toReturnNote:                    return type note
        '''
        self.fromClass = fromClass
        self.fromMethod = fromMethod
        self.toClass = toClass
        self.toMethod = toMethod
        self.toMethodCalledFromLineNumber = toMethodCalledFromLineNumber
        self.toSignature = toSignature
        self.toMethodNote = toMethodNote
        self.toReturnType = toReturnType
        self.toReturnNote = toReturnNote


    def __eq__(self, other):
        return self.fromClass == other.fromClass and \
               self.fromMethod == other.fromMethod and \
               self.toClass == other.toClass and \
               self.toMethod == other.toMethod and \
               self.toMethodCalledFromLineNumber == other.toMethodCalledFromLineNumber and \
               self.toSignature == other.toSignature and \
               self.toMethodNote == other.toMethodNote and \
               self.toReturnType == other.toReturnType and \
               self.toReturnNote == other.toReturnNote


    def isEntryPoint(self, targetClass, targetMethod):
        '''
        Returns True if the passed targetClass/targetMethod are equal to the toClass and
        toMethod of the flow entry, which means the flow entry corresponds to the seq diag
        entry point.

        :param targetClass:
        :param targetMethod:
        :return:
        '''
        return self.toClass == targetClass and \
               self.toMethod == targetMethod


    def equalFrom(self, entry):
        return self.fromClass == entry.fromClass and self.fromMethod == entry.fromMethod


    def differByLineNumberOnly(self, entry):
        '''
        Return True if entry and self denote the same class.method but called from a
        different location
        :param entry:
        :return:
        '''
        return self.equalFrom(entry) and self.toMethodCalledFromLineNumber != entry.toMethodCalledFromLineNumber


    def getIndentNumber(self):
        '''
        Calculate the number of time the Plant UML command must be indented in function
        of the call depth level of the FlowEntry
        :return:
        '''
        return self.toMethodCalledFromLineNumber.count('-')


    def createReturnType(self, maxArgNum, maxReturnTypeCharLen):
        '''
        Return a return type string which has no more arguments than maxArgNum and is not
        longer than maxReturnTypeCharLen.

        :param maxArgNum:
        :param maxReturnTypeCharLen:
        :return:
        '''

        # applying first the max return type arg number constraint

        if self.toReturnType == '':
            return self.toReturnType
        else:
            returnTypeStr = self.toReturnType
            if maxArgNum != None:
                if maxArgNum == 0:
                    return '...'

                tentativeReturnTypeArgNum = self.toReturnType.count(',') + 1

                if maxArgNum < tentativeReturnTypeArgNum:
                    # here, the return type must be reduced to maxArgNum arguments
                    returnTypeArgList = returnTypeStr.split(',')
                    returnTypeStr = ','.join(returnTypeArgList[:maxArgNum])
                    returnTypeStr = returnTypeStr + ', ...'

        # applying then the max return type length number constraint

        if maxReturnTypeCharLen != None:
            if returnTypeStr == '...' or len(returnTypeStr) <= maxReturnTypeCharLen:
                return returnTypeStr

            if '...' in returnTypeStr:
                returnTypeStr = returnTypeStr[:-5]  # removing , ...

            returnTypeArgList = returnTypeStr.split(', ')
            returnTypeStr = '...'
            tentativeReturnType = ''
            tentativeReturnTypeArgNum = 0

            for arg in returnTypeArgList:
                if tentativeReturnTypeArgNum == 0:
                    tentativeReturnType += arg
                else:
                    tentativeReturnType = tentativeReturnType + ', ' + arg

                tentativeReturnType = tentativeReturnType + ', ...'
                rtLen = len(tentativeReturnType)

                if rtLen > maxReturnTypeCharLen:
                    return returnTypeStr
                elif rtLen == maxReturnTypeCharLen:
                    return tentativeReturnType
                else:
                    returnTypeStr = tentativeReturnType
                    tentativeReturnType = returnTypeStr[:-5]
                    tentativeReturnTypeArgNum += 1

        return returnTypeStr


    def createSignature(self, maxSigArgNum, maxSigCharLen):
        '''
        Return a signature which has no more arguments than maxSigArgNum and is not
        longer than maxSigCharLen.

        :param maxSigArgNum:
        :param maxSigCharLen:
        :return:
        '''

        # applying first the max signature arg number constraint

        if self.toSignature == '()':
            return self.toSignature
        else:
            returnedSignature = self.toSignature
            if maxSigArgNum != None:
                if maxSigArgNum == 0:
                    return '(...)'

                tentativeSigArgNum = self.toSignature.count(',') + 1

                if maxSigArgNum < tentativeSigArgNum:
                    # here, the signature must be reduced to maxSigArgNum arguments
                    returnedSignature = returnedSignature[1:-1] # removing parenthesis
                    sigArgList = returnedSignature.split(',')
                    returnedSignature = ','.join(sigArgList[:maxSigArgNum])
                    returnedSignature = '(' + returnedSignature + ', ...)'

        # applying then the max signature length number constraint

        if maxSigCharLen != None:
            if returnedSignature == '(...)' or len(returnedSignature) <= maxSigCharLen:
                return returnedSignature

            if '...' in returnedSignature:
                returnedSignature = returnedSignature[1:-6]  # removing parenthesis and , ...
            else:
                returnedSignature = returnedSignature[1:-1]  # removing parenthesis

            sigArgList = returnedSignature.split(', ')
            returnedSignature = '(...)'
            tentativeSignature = ''
            tentativeSigArgNum = 0

            for arg in sigArgList:
                if tentativeSigArgNum == 0:
                    tentativeSignature += arg
                else:
                    tentativeSignature = tentativeSignature + ', ' + arg

                tentativeSignature = '(' + tentativeSignature + ', ...)'
                sigLen = len(tentativeSignature)

                if sigLen > maxSigCharLen:
                    return returnedSignature
                elif sigLen == maxSigCharLen:
                    return tentativeSignature
                else:
                    returnedSignature = tentativeSignature
                    tentativeSignature = returnedSignature[1:-6]
                    tentativeSigArgNum += 1

        return returnedSignature


    def __str__(self):
        return "{}.{}, {}.{}{}, {}, {}, {}, {}".format(self.fromClass, self.fromMethod, self.toClass, self.toMethod, self.toSignature, self.toMethodCalledFromLineNumber, self.toMethodNote, self.toReturnType, self.toMethodReturnNote)


class RecordedFlowPath:
    '''
    This class stores in a flowEntryList of FlowEntry the succession of embedded method calls whic occurred
    until the point in a leaf method containing the SeqDiagBuilder.recordFlow() instruction.
    '''
    def __init__(self, entryClass, entryMethod):
        '''

        :param entryClass:  class containing the entry method
        :param entryMethod: method from which the embedded method calls are recorded in the
                            RecordedFlowPath. entryClass.entryMethod are labelled as entry point
                            and are stored as a FlowEntry in the internal RecordedFlowPath flowEntryList.
        '''
        self.entryClass = entryClass
        self.entryMethod = entryMethod
        self.entryPointReached = False
        self.flowEntryList = []


    def addIfNotIn(self, newFlowEntry):
        '''
        This method adds a flow entry to the internal flowEntryList if the internal flowEntryList
        already contains the entry point and provided this flow entry is not already in the
        flowEntryList.

        The addition is only possible if the entry point was reached. For example, if
        we have TestClass.testCaseMethod() --> A.f() --> A.g() --> B.h() and the entry class
        and entry method is A.f(), flow entries will be added only once A.f() was reached and was
        added to the flowEntryList.
        :param newFlowEntry:
        :return:
        '''
        if not self.entryPointReached:
            if newFlowEntry.isEntryPoint(self.entryClass, self.entryMethod):
                self.entryPointReached = True
            else:
                # exiting the method ignores flow entries preceeding the entry point
                return

        if self.flowEntryList == []:
            # the first encountered occurrence of entry point is added
            self.flowEntryList.append(newFlowEntry)
            return

        # exiting the method if the current flow entry is already in the flowEntryList
        for flowEntry in self.flowEntryList:
            if flowEntry == newFlowEntry:
                return

        self.flowEntryList.append(newFlowEntry)


    def size(self):
        return len(self.flowEntryList)


    def isEmpty(self):
        return self.size() == 0


    def __str__(self):
        outStr = ''

        for flowEntry in self.flowEntryList:
            outStr += str(flowEntry) + '\n'

        return outStr


class SeqDiagCommandStack:
    '''
    This flowEntryList stores the embedded calls used to build the sequence diagram commands. It is
    used to build the return commands of the diagram.
    '''


    def __init__(self):
        self.stack = []


    def pop(self):
        if self.isEmpty():
            return None
        else:
            return self.stack.pop()


    def push(self, flowEntry):
        '''
        Push on the flowEntryList a 2 elements flowEntryList, the first element being the couple <class name>.<toMethod name>
        and the second one being the string denoting the information returned to the caller by the toMethod.
        :param flowEntry:
        :return:
        '''
        self.stack.append(flowEntry)

        return self.stack


    def peek(self):
        if self.isEmpty():
            return None
        else:
            return self.stack[-1]


    def size(self):
        return len(self.stack)


    def isEmpty(self):
        return self.size() == 0


    def containsFromCall(self, flowEntry):
        '''
        Return True if the passed flow entry is in the SeqDiagCommandStack.
        :param flowEntry:
        :return:
        '''
        for entry in self.stack:
            if entry.equalFrom(flowEntry):
                return True

        return False


class ConstructorArgsProvider:
    def __init__(self, classArgDic):
        '''

        :param classArgDic: class cnstructor arguments dictionary
                            classArgDic format:
                                {
                                    'classNameA_usage_2': ['a_arg21', 'a_arg22'], #args used at second instanciation
                                    'classNameA_usage_1': ['a_arg11', 'a_arg12'], #args used at first instanciation
                                    'classNameB': ['b_arg1']
                                    'classNameC_usage_1': ['c_arg1'],
                                    'classNameC_usage_3': ['c_arg3'],
                                    'classNameC_usage_2': ['c_arg2']
                                }
        '''
        self.classArgDic = classArgDic

        # making a copy of the classArgDic so it can be added to a warning message to make it clearer.
        # Doing a deep copy does not seem necessary for now, but in the future ...
        self.savedClassArgDic = copy.deepcopy(classArgDic)


    def getArgsForClassConstructor(self, className):
        '''
        Return a list containing the ctor arguments for the passed className. If className is
        not found in the internal classArgDic, None is returned.

        :param className:
        :return: list containing the ctor arguments in their usage order, None if no entry exist
                 for the passed className
        '''

        # collecting all the keys in the classArgDic which are for the className.
        # The keys may contain a digit, which indicates that the entry can only be
        # used once to instanciate className
        keys = self.classArgDic.keys()
        keyList = []

        for key in keys:
            if className in key:
                keyList.append(key)

        if len(keyList) == 0:
            # here, no ctor arg definition for className found in the classArgDic
            return None
        elif len(keyList) == 1:
            classNameFromDic = keyList[0]
            if any(c.isdigit() for c in classNameFromDic):
                args = self.classArgDic[classNameFromDic]

                # since an entry in the classArgDic keyed by a key conttaining a digit
                # can be consumed only once, it must be deleted from the classArgDic
                del self.classArgDic[classNameFromDic]

                return args
            else:
                # here, the ctor argument(s) are reusable and need not be removed from the classArgDic
                return self.classArgDic.get(className, None)

        # here, the keyList contains more than one key, which means that several sets of ctor
        # arguments were specified for className, which means that at each instanciation, the used
        # entry must be removed from the classArgDic.
        orderedKeyList = sorted(keyList)
        firstKey = orderedKeyList[0]
        firstKeyArgs = self.classArgDic[firstKey]
        del self.classArgDic[firstKey]

        return firstKeyArgs


class SeqDiagBuilder:
    '''
    This class contains a static utility methods used to build a sequence diagram from the
    call flowEntryList as at the point in the python code were it is called.

    To build the diagram, type seqdiag -Tsvg flowEntryList.txt in a command line window.
    This build a svg file which can be displayed in a browsxer.
    '''

    seqDiagWarningList = []
    _projectPath = None
    _isActive = False
    _recordFlowCalled = False
    _seqDiagEntryClass = None
    _seqDiagEntryMethod = None
    recordedFlowPath = None
    _participantDocOrderedDic = None
    _constructorArgProvider = None

    @staticmethod
    def activate(projectPath, entryClass, entryMethod, classArgDic = None):
        '''
        Initialise and activate SeqDiagBuilder. This method must be called before calling any method
        on the entry class.

        :param projectPath: for example 'D:\\Development\\Python\\seqdiagbuilder' or
                            'D:/Development/Python/seqdiagbuilder'
        :param entryClass:
        :param entryMethod:
        :param classArgDic: class cnstructor arguments dictionary
                            classArgDic format:
                                {
                                    'classNameA_usage_2': ['a_arg21', 'a_arg22'], #args used at second instanciation
                                    'classNameA_usage_1': ['a_arg11', 'a_arg12'], #args used at first instanciation
                                    'classNameB': ['b_arg1']
                                    'classNameC_usage_1': ['c_arg1'],
                                    'classNameC_usage_3': ['c_arg3'],
                                    'classNameC_usage_2': ['c_arg2']
                                }

        :return:
        '''
        SeqDiagBuilder._projectPath = projectPath
        SeqDiagBuilder._seqDiagEntryClass = entryClass
        SeqDiagBuilder._seqDiagEntryMethod = entryMethod
        SeqDiagBuilder.recordedFlowPath = RecordedFlowPath(SeqDiagBuilder._seqDiagEntryClass, SeqDiagBuilder._seqDiagEntryMethod)
        SeqDiagBuilder._isActive = True
        SeqDiagBuilder._participantDocOrderedDic = collections.OrderedDict()

        if classArgDic:
            SeqDiagBuilder._constructorArgProvider = ConstructorArgsProvider(classArgDic)


    @staticmethod
    def deactivate():
        '''
        Reinitialise the class level seq diag variables and data structures and sets its
        build mode to False
        :return:
        '''
        SeqDiagBuilder._seqDiagEntryClass = None
        SeqDiagBuilder._seqDiagEntryMethod = None
        SeqDiagBuilder.recordedFlowPath = None
        SeqDiagBuilder.seqDiagWarningList = []
        SeqDiagBuilder._isActive = False
        SeqDiagBuilder._recordFlowCalled = False
        SeqDiagBuilder._participantDocOrderedDic = collections.OrderedDict()
        SeqDiagBuilder._constructorArgProvider = None


    @staticmethod
    def _buildCommandFileHeaderSection():
        '''
        This toMethod create the first line of the PlantUML command file,
        adding a header section in case of warnings.
        :return:
        '''
        commandFileHeaderSectionStr = "@startuml\n"

        warningNb = len(SeqDiagBuilder.seqDiagWarningList)

        if warningNb > 0:
            # building a header containing the warnings. If several warnings are issued, they are numbered.
            commandFileHeaderSectionStr += "center header\n<b><font color=red size=20> Warnings</font></b>\n"
            warningIndex = 0

            if warningNb > 1:
                warningIndex = 1

            for warning in SeqDiagBuilder.seqDiagWarningList:
                if warningIndex:
                    commandFileHeaderSectionStr += "<b><font color=red size=20> {}</font></b>\n".format(warningIndex)
                    warningIndex += 1
                commandFileHeaderSectionStr += SeqDiagBuilder._splitWarningToLines(warning)

            commandFileHeaderSectionStr += "endheader\n\n"

        return commandFileHeaderSectionStr


    @staticmethod
    def _splitNoteToLines(oneLineNote, maxNoteLineLen):
        '''
        Splits the oneLineNote string into lines not exceeding maxNoteLineLen and returns the lines
        into a list.

        :param oneLineNote:
        :param maxNoteLineLen:
        :return:
        '''
        if oneLineNote == '':
            return []

        noteWordList = oneLineNote.split(' ')
        noteLine = noteWordList[0]
        noteLineLen = len(noteLine)
        noteLineList = []

        for word in noteWordList[1:]:
            wordLen = len(word)

            if noteLineLen + wordLen + 1 > maxNoteLineLen:
                noteLineList.append(noteLine)
                noteLine = word
                noteLineLen = wordLen
            else:
                noteLine += ' ' + word
                noteLineLen += wordLen + 1

        noteLineList.append(noteLine)

        return noteLineList


    @staticmethod
    def _buildClassNoteSection(participantDocOrderedDic, maxNoteCharLen):
        classNoteSectionStr = ''

        for className, classNote in participantDocOrderedDic.items():
            if classNote == '':
                participantEntry = 'participant {}\n'.format(className)
            else:
                classNoteLineList = SeqDiagBuilder._splitNoteToLines(classNote, maxNoteCharLen * 1.5)

                #adding a '/' before 'note over ...' causes PlantUML to position participant notes on the same line !
                participantEntry = 'participant {}\n{}/note over of {}\n'.format(className, TAB_CHAR, className)

                for classNoteLine in classNoteLineList:
                    participantEntry += '{}{}{}\n'.format(TAB_CHAR, TAB_CHAR, classNoteLine)

                participantEntry += '{}end note\n'.format(TAB_CHAR)

            classNoteSectionStr += participantEntry

        return classNoteSectionStr


    @staticmethod
    def _splitWarningToLines(warningStr):
        '''

        :param warningStr:
        :return:
        '''
        formattedWarnings = ''
        lines = warningStr.split('. ')

        for line in lines:
            formattedWarnings += '<b><font color=red size=14>  {}.</font></b>\n'.format(line)

        return formattedWarnings

    @staticmethod
    def createDiagram(targetDriveDirName, actorName, title=None, maxSigArgNum=None, maxSigCharLen=BIG_COMMENT_LENGTH, maxNoteCharLen=BIG_COMMENT_LENGTH):
        '''
        This method create a Plant UML command file, launch Plant UML on it and open the
        created sequence diagram svg file in a browser.

        :param targetDriveDirName:  folder in which the generated command file and svg diagram
                                    are saved. Ex: c:/temp.
        :param actorName:           name of the sequence diagram actor.
        :param title:               title of the sequence diagram.
        :param maxSigArgNum:        maximum arguments number of a called toMethod
                                    toSignature. Applies to return type aswell.
        :param maxSigCharLen:       maximum length a method signature can occupy.
                                    Applies to return type aswell.
        :param maxNoteCharLen:      maximum length a method or participant note can occupy.
        :return:                    nothing.
        '''
        seqDiagCommands = SeqDiagBuilder.createSeqDiaqCommands(actorName, maxSigArgNum, maxSigCharLen, maxNoteCharLen)
        targetCommandFileName = SeqDiagBuilder._seqDiagEntryMethod + '.txt'
        targetDriveDirName = targetDriveDirName.replace('\\','/')

        if targetDriveDirName[-1] != '/':
            targetDriveDirName = targetDriveDirName + '/'

        targetCommandFilePathName = '{}{}'.format(targetDriveDirName, targetCommandFileName)

        with open(targetCommandFilePathName, "w") as f:
            f.write(seqDiagCommands)

        os.chdir(targetDriveDirName)

        os.system('java -jar plantuml.jar -tsvg ' + targetCommandFileName)
        webbrowser.open("file:///{}{}.svg".format(targetDriveDirName, SeqDiagBuilder._seqDiagEntryMethod))


    @staticmethod
    def createSeqDiaqCommands(actorName, title=None, maxSigArgNum=None, maxSigCharLen=BIG_COMMENT_LENGTH, maxNoteCharLen=BIG_COMMENT_LENGTH):
        '''
        This method uses the control flow data collected during execution to create
        the commands Plantuml will use to draw the sequence diagram.

        To build the diagram itself, type java -jar plantuml.jar -tsvg seqdiagcommands.txt
        in a command line window. This build a svg file which can be displayed in a browser.

        :param actorName:       name of the sequence diagram actor.
        :param title:           title of the sequence diagram.
        :param maxSigArgNum:    maximum arguments number of a called toMethod
                                toSignature. Applies to return type aswell.
        :param maxSigCharLen:   maximum length a toMethod toSignature can occupy.
                                Applies to return type aswell.
        :param maxNoteCharLen:      maximum length a method or participant note can occupy.
        :return:                nothing.
        '''
        isFlowRecorded = True

        if SeqDiagBuilder.recordedFlowPath == None:
            isEntryPointReached = False
            isFlowRecorded = False
            SeqDiagBuilder._issueNoFlowRecordedWarning(isEntryPointReached)
        elif SeqDiagBuilder.recordedFlowPath.isEmpty():
            isEntryPointReached = SeqDiagBuilder.recordedFlowPath.entryPointReached
            isFlowRecorded = False
            SeqDiagBuilder._issueNoFlowRecordedWarning(isEntryPointReached)

        seqDiagCommandStr = SeqDiagBuilder._buildCommandFileHeaderSection()

        if isFlowRecorded:
            classMethodReturnStack = SeqDiagCommandStack()
            if title:
                seqDiagCommandStr += "\ntitle {}\n".format(title)
                seqDiagCommandStr += "actor {}\n".format(actorName)
            else:
                seqDiagCommandStr += "\nactor {}\n".format(actorName)
            seqDiagCommandStr += SeqDiagBuilder._buildClassNoteSection(SeqDiagBuilder._participantDocOrderedDic,
                                                                       maxNoteCharLen)
            firstFlowEntry = SeqDiagBuilder.recordedFlowPath.flowEntryList[0]
            firstFlowEntry.fromClass = actorName
            fromClass = firstFlowEntry.fromClass
            commandStr = SeqDiagBuilder._handleSeqDiagForwardMesssageCommand(fromClass, firstFlowEntry, classMethodReturnStack, maxSigArgNum, maxSigCharLen, maxNoteCharLen)
            seqDiagCommandStr += commandStr
            fromClass = firstFlowEntry.toClass

            for flowEntry in SeqDiagBuilder.recordedFlowPath.flowEntryList[1:]:
                if not classMethodReturnStack.containsFromCall(flowEntry):
                    commandStr = SeqDiagBuilder._handleSeqDiagForwardMesssageCommand(fromClass, flowEntry, classMethodReturnStack, maxSigArgNum, maxSigCharLen, maxNoteCharLen)
                    seqDiagCommandStr += commandStr
                    fromClass = flowEntry.toClass
                else:
                    stopUnfolding = False
                    while not stopUnfolding and classMethodReturnStack.containsFromCall(flowEntry):
                        returnEntry = classMethodReturnStack.pop()
                        # handle deepest or leaf return message, the one which did not
                        # generate an entry in the classMethodReturnStack
                        commandStr = SeqDiagBuilder._handleSeqDiagReturnMesssageCommand(returnEntry, maxSigArgNum, maxSigCharLen)
                        seqDiagCommandStr += commandStr

                        # handle return message for the method which called the
                        # deepest or leaf method and which generated an entry in the
                        # classMethodReturnStack
                        if flowEntry.differByLineNumberOnly(returnEntry):
                            stopUnfolding = True
                            fromClass = flowEntry.fromClass
                            continue
                        returnEntry = classMethodReturnStack.pop()
                        commandStr = SeqDiagBuilder._handleSeqDiagReturnMesssageCommand(returnEntry, maxSigArgNum, maxSigCharLen)
                        seqDiagCommandStr += commandStr
                        fromClass = returnEntry.fromClass
                    commandStr = SeqDiagBuilder._handleSeqDiagForwardMesssageCommand(fromClass, flowEntry, classMethodReturnStack, maxSigArgNum, maxSigCharLen, maxNoteCharLen)
                    seqDiagCommandStr += commandStr
                    fromClass = flowEntry.toClass
                    deepestReached = True

            while not classMethodReturnStack.isEmpty():
                returnEntry = classMethodReturnStack.pop()
                commandStr = SeqDiagBuilder._handleSeqDiagReturnMesssageCommand(returnEntry, maxSigArgNum, maxSigCharLen)
                seqDiagCommandStr += commandStr
        else:
            # adding dummy line to stick to Plantuml command file syntax and prevent
            # error messages in built diagram
            seqDiagCommandStr += "actor {}\n\n".format(actorName)

        seqDiagCommandStr += "@enduml"

        return seqDiagCommandStr

    @staticmethod
    def _issueNoFlowRecordedWarning(isEntryPointReached):
        if SeqDiagBuilder._constructorArgProvider:
            savedClassArgDic = SeqDiagBuilder._constructorArgProvider.savedClassArgDic
        else:
            savedClassArgDic = None

        if SeqDiagBuilder._isActive:
            warning = "No control flow recorded. Method activate() called with arguments {}, {}, {}, {}: {}. Method recordFlow() called: {}. Specified entry point: {}.{} reached: {}".format(
                SeqDiagBuilder._projectPath,
                SeqDiagBuilder._seqDiagEntryClass,
                SeqDiagBuilder._seqDiagEntryMethod,
                savedClassArgDic,
                SeqDiagBuilder._isActive,
                SeqDiagBuilder._recordFlowCalled,
                SeqDiagBuilder._seqDiagEntryClass,
                SeqDiagBuilder._seqDiagEntryMethod,
                isEntryPointReached)
        else:
            warning = "No control flow recorded. Method activate() called: {}. Method recordFlow() called: {}. Specified entry point: {}.{} reached: {}".format(
                SeqDiagBuilder._isActive,
                SeqDiagBuilder._recordFlowCalled,
                SeqDiagBuilder._seqDiagEntryClass,
                SeqDiagBuilder._seqDiagEntryMethod,
                isEntryPointReached)
        SeqDiagBuilder._issueWarning(warning)


    @staticmethod
    def _handleSeqDiagReturnMesssageCommand(returnEntry, maxArgNum, maxReturnTypeCharLen):
        fromClass = returnEntry.toClass
        toClass = returnEntry.fromClass
        toReturnType = returnEntry.createReturnType(maxArgNum, maxReturnTypeCharLen)
        toMethodReturnNote = returnEntry.toReturnNote
        indentStr = SeqDiagBuilder._getReturnIndent(returnEntry)
        commandStr = SeqDiagBuilder._addReturnSeqDiagCommand(fromClass, toClass, toReturnType, indentStr)

        # adding return note
        if toMethodReturnNote != '':
            toMethoReturndNoteLineList = SeqDiagBuilder._splitNoteToLines(toMethodReturnNote, maxReturnTypeCharLen * 1.5)
            noteSection = '{}note right\n'.format(indentStr)

            for noteLine in toMethoReturndNoteLineList:
                noteSection += '{}{}{}\n'.format(indentStr, TAB_CHAR, noteLine)

            noteSection += '{}end note\n'.format(indentStr)
            commandStr += noteSection

        return commandStr


    @staticmethod
    def _handleSeqDiagForwardMesssageCommand(fromClass, flowEntry, classMethodReturnStack, maxSigArgNum, maxSigCharLen, maxNoteCharLen):
        '''
        Controls the creation of the Plant UML call commands.
        :param fromClass:
        :param flowEntry:
        :param classMethodReturnStack:
        :param maxSigArgNum:
        :param maxSigCharLen:
        :return:
        '''
        classMethodReturnStack.push(flowEntry)
        toClass = flowEntry.toClass
        toMethod = flowEntry.toMethod
        toSignature = flowEntry.createSignature(maxSigArgNum, maxSigCharLen)
        toMethodNote = flowEntry.toMethodNote
        indentStr = SeqDiagBuilder._getForwardIndent(flowEntry)
        commandStr = SeqDiagBuilder._addForwardSeqDiagCommand(fromClass, toClass, toMethod, toSignature, indentStr)

        # adding method note
        if toMethodNote != '':
            toMethodNoteLineList = SeqDiagBuilder._splitNoteToLines(toMethodNote, maxNoteCharLen * 1.5)
            indentStr += TAB_CHAR
            noteSection = '{}note right\n'.format(indentStr)

            for noteLine in toMethodNoteLineList:
                noteSection += '{}{}{}\n'.format(indentStr, TAB_CHAR, noteLine)

            noteSection += '{}end note\n'.format(indentStr)
            commandStr += noteSection

        return commandStr


    @staticmethod
    def _getForwardIndent(flowEntry):
        '''
        Returns the forward ident string.
        :param flowEntry:
        :return:
        '''
        return flowEntry.getIndentNumber() * TAB_CHAR

    @staticmethod
    def _getReturnIndent(returnEntry):
        '''
        Returns the return ident string .
        :param returnEntry:
        :return:
        '''
        return (returnEntry.getIndentNumber() + 1) * TAB_CHAR

    @staticmethod
    def _addForwardSeqDiagCommand(fromClass, toClass, method, signature, indentStr):
        return "{}{} -> {}: {}{}\n{}activate {}\n".format(indentStr,
                                                          fromClass,
                                                          toClass,
                                                          method,
                                                          signature,
                                                          indentStr + TAB_CHAR,
                                                          toClass)


    @staticmethod
    def _addReturnSeqDiagCommand(fromClass, toClass, returnType, indentStr):
        returnMessage = ''

        if returnType != '':
            returnMessage = 'return {}'.format(returnType)

        return "{}{} <-- {}: {}\n{}deactivate {}\n".format(indentStr,
                                                         toClass,
                                                         fromClass,
                                                         returnMessage,
                                                           indentStr,
                                                         fromClass)

    @staticmethod
    def recordFlow():
        '''
        Records in a FlowEntry list the control flow information which will be used later to build
        the Plantuml sequence diagram creation commands. Information is recorded only if the
        SeqDiagBuilder was activated using SeqDiagBuilder.activate().

        :return:
        '''
        SeqDiagBuilder._recordFlowCalled = True

        if not SeqDiagBuilder._isActive:
            return

        SeqDiagBuilder.recordedFlowPath.entryPointReached = False

        # get the stack trace at this point of execution
        frameListLine = repr(traceback.extract_stack())

        # convert the stack trace to a list ...
        frameList = re.findall(FRAME_PATTERN, frameListLine)

        if frameList:
            fromClassName = ''              # class containing the method calling the toMethod
            fromMethodName = ''             # method calling the toMethod
            toMethodCallLineNumber = '0'    # line number in the fromMethod of the toMethod call
            entryClassEncountered = False   # enables optimization: before the entry class was found in a module
                                            # referenced in a frame, searching classes supporting a method
                                            # in this module does not make sense. This saves about 20 %
                                            # of recordFlow() execution time ...

            for frame in frameList[:-1]: #last line in frameList is the call to the recordFlow() method !
                match = re.match(PYTHON_FILE_AND_FUNC_PATTERN, frame)
                if match:
                    pythonClassFilePath = match.group(1)
                    packageSpec = SeqDiagBuilder._extractPackageSpec(pythonClassFilePath)
                    moduleName = match.group(2)
                    methodCallLineNumber = match.group(3)
                    currentMethodName = match.group(4)

                    # now the current module is opened and its source code is parsed. Then, the classes
                    # it contains are instanciated in order to select the one supporting the current
                    # method methodName. The purpose is to be able to access to various informations
                    # used later to build the sequence diagram, namely the method signature and tagged
                    # informations potentially contained in the method documentation.
                    with open(pythonClassFilePath + moduleName + '.py', "r") as sourceFile:
                        source = sourceFile.read()
                        parsedSource = ast.parse(source)

                        # extracting from the parsed source the name of the classes it contains
                        moduleClassNameList = [node.name for node in ast.walk(parsedSource) if isinstance(node, ast.ClassDef)]

                        if not entryClassEncountered and not SeqDiagBuilder._seqDiagEntryClass in moduleClassNameList:
                            # optimization: if the entry class was not yet found and if moduleName
                            # does not contain the definition of the entry class, searching an instance
                            # supporting the entry method in this module does not make sense !
                            continue
                        else:
                            entryClassEncountered = True

                        toClassName, toClassNote, toMethodReturn, toMethodSignature, toMethodNote, toMethodReturnNote = SeqDiagBuilder._extractToClassMethodInformation(moduleClassNameList, packageSpec, moduleName, currentMethodName)

                        if toClassName == None:
                            continue

                        # storing the class note for further use when creating the Plantuml seq diag
                        # command file
                        SeqDiagBuilder._participantDocOrderedDic[toClassName] = toClassNote

                        toMethodName = currentMethodName
                        flowEntry = FlowEntry(fromClassName, fromMethodName, toClassName, toMethodName, toMethodCallLineNumber,
                                              toMethodSignature, toMethodNote, toMethodReturn, toMethodReturnNote)
                        fromClassName = toClassName
                        fromMethodName = toMethodName
                        toMethodCallLineNumber = "{}-{}".format(toMethodCallLineNumber, methodCallLineNumber)
                        SeqDiagBuilder.recordedFlowPath.addIfNotIn(flowEntry)


    @staticmethod
    def _extractPackageSpec(pythonClassFilePath):
        '''
        Extract the package part of the class file path. The package component will be required
        later when instanciating the class.

        :param pythonClassFilePath:
        :return:
        '''
        pythonisedPythonClassFilePath = SeqDiagBuilder._pythoniseFilePath(pythonClassFilePath)
        pythonisedProjectPath = SeqDiagBuilder._pythoniseFilePath(SeqDiagBuilder._projectPath)
        packageSpec = pythonisedPythonClassFilePath.replace(pythonisedProjectPath, '')

        #handling file path containg either \\ (windows like) or / (unix like)
        packageSpec = packageSpec.replace('.', '', 1)

        return packageSpec


    @staticmethod
    def _pythoniseFilePath(packageSpec):
        '''
        In order to liberate SeqDiagBuilder from sub dir separators different in Windows and
        in Unix, simply replaces them with a period.

        :param packageSpec:
        :return:
        '''
        packageSpec = packageSpec.replace('\\', '.')
        packageSpec = packageSpec.replace('/', '.')

        return packageSpec

    #            print(SeqDiagBuilder.recordedFlowPath)


    @staticmethod
    def _issueWarning(warningStr):
        SeqDiagBuilder.seqDiagWarningList.append(warningStr)


    @staticmethod
    def getWarningList():
        return SeqDiagBuilder.seqDiagWarningList


    @staticmethod
    def _extractToClassMethodInformation(moduleClassNameList, packageSpec, moduleName, methodName):
        '''
        This method returns informations specific to the target class and method, namely, the name
        of the class supporting methodName, its seqdiag note, the target method return type,
        the target method return note, the method signature and its seqdiag note.

        Normally, only one class supporting methodName should be found in moduleName. If more
        than one class are found, this indicates that the module contains a class hierarchy with
        method methodName defined in the base class (and so inherited or overridden by its
        subclasses). More than one class are found aswell if the module contains two or more
        unrelated classes with the same method methodName.

        In case of multiple classes found, the first encountered class is selected by default, i.e.
        the first defined class in the module which is the root class in case of a hierarchy.

        To override this choice, the tag :seq_diag_select_method can be used in the right method
        documentation.

        :param moduleClassNameList: contains the names of all the classes defined in module moduleName
        :param packageSpec:         package containing the module
        :param moduleName:          name of module containing the classes
        :param methodName:          name of the method whose doc is searched for the :seqdiag_return tag so
                                    the associated value can be returned as the method return value.
                                    In case the method doc contains the :seqdiag_select_method tag,
                                    the class containing the method is the unique one to be retained

        :return:                    className, classNote, methodReturn, methodSignature, methodNote, methodReturnNote
        '''

        instanceList = []
        methodReturn = ''
        methodSignature = ''
        methodNote = ''
        methodReturnNote = ''
        selectedMethodFound = False

        for className in moduleClassNameList:
            if selectedMethodFound:
                break

            instance = SeqDiagBuilder._instanciateClass(className, packageSpec, moduleName)

            # obtain the list of methods of the instance
            methodTupplesList = inspect.getmembers(instance, predicate=inspect.ismethod)

            for methodTupple in methodTupplesList:
                if methodName == methodTupple[0]:
                    # here, methodName is a member of className

                    methodObj = methodTupple[1]
                    methodSignature = str(signature(methodObj))
                    methodDoc = methodObj.__doc__

                    if methodDoc:
                        # get method return type from method documentation
                        match = re.search(SEQDIAG_RETURN_TAG_PATTERN, methodDoc)
                        if match:
                            methodReturn = match.group(1)

                        # get method note from method documentation
                        match = re.search(SEQDIAG_NOTE_TAG_PATTERN, methodDoc)
                        if match:
                            methodNote = match.group(1)

                        # get method return note from method documentation
                        match = re.search(SEQDIAG_METHOD_RETURN_NOTE_TAG_PATTERN, methodDoc)
                        if match:
                            methodReturnNote = match.group(1)

                        # chech if method documentation contains :seqdiag_select_method tag
                        match = re.search(SEQDIAG_SELECT_METHOD_TAG_PATTERN, methodDoc)
                        if match:
                            # in case several instances do support methodName, the first one containing
                            # the method whose doc is tagged with :seqdiag_select_method is returned in
                            # the instance list and all the other instances are ignored.
                            instanceList = [instance]
                            selectedMethodFound = True
                            break

                    instanceList.append(instance)

        if instanceList == []:
            # no class supporting methodName found in moduleName
            return None, None, None, None, None, None

        instance = instanceList[0]
        className = instance.__class__.__name__
        classDoc =  instance.__class__.__doc__
        classNote = ''

        if classDoc:
            # get class note from class documentation
            match = re.search(SEQDIAG_NOTE_TAG_PATTERN, classDoc)
            if match:
                classNote = match.group(1)

        if len(instanceList) > 1:
            filteredClassNameList = []
            for filteredInstance in instanceList:
                filteredClassNameList.append(filteredInstance.__class__.__name__)
            SeqDiagBuilder._issueWarning(
                "More than one class {} found in module {} do support method {}{}. Since Python provides no way to determine the exact target class, class {} was chosen by default for building the sequence diagram. To override this selection, put tag {} somewhere in the target method documentation or define every class of the hierarchy in its own file. See help for more information".format(
                    str(filteredClassNameList), moduleName, methodName, methodSignature,
                    instance.__class__.__name__,
                    SEQDIAG_SELECT_METHOD_TAG))

        return className, classNote, methodReturn, methodSignature, methodNote, methodReturnNote


    @staticmethod
    def _instanciateClass(className, packageSpec, moduleName):
        '''
        This method instanciate the passed className defined in the passed package + module name
        whatever the number of required arguments in the __init__ method.
        :param className:
        :param packageSpec:
        :param moduleName:
        :return:
        '''
        module = None

        try:
            module = importlib.import_module(packageSpec + moduleName)
        except ModuleNotFoundError:
            return None

        class_ = getattr(module, className)
        instance = None
        noneStr = ''
        ctorArgValueList = None

        if SeqDiagBuilder._constructorArgProvider:
            ctorArgValueList = SeqDiagBuilder._constructorArgProvider.getArgsForClassConstructor(className)

        try:
            if ctorArgValueList:
                evaluationString = 'class_('
                for argValue in ctorArgValueList:
                    evaluationString += "'" + str(argValue) + "',"

                evaluationString = evaluationString[:-1] + ')'
                instance = eval(evaluationString)
            else:
                instance = eval('class_(' + noneStr + ')')
        except TypeError:
            # here, the clasa we try to instanciate has an __init__ method with one or more
            # arguments. We enter in a loop, trying to instanciate the class adding one argument
            # at each loop run.
            noneStr = 'None'
            if not ctorArgValueList:
                while not instance:
                    try:
                        instance = eval('class_(' + noneStr + ')')
                    except TypeError:
                        noneStr += ', None'
                    except SyntaxError as e:
                        SeqDiagBuilder._issueWarning('ERROR - constructor for class {} in module {} failed due to invalid argument(s). To solve the problem, pass a class argument dictionary with an entry for {} to the SeqDiagBuilder.activate() method'.format(
                            className, packageSpec + moduleName, className))
                        break
            else:
                SeqDiagBuilder._issueWarning('ERROR - constructor for class {} in module {} failed due to invalid \
                argument(s) ({}) defined in the class argument dictionary passed to the SeqDiagBuilder.activate() method'.format(
                    className, packageSpec + moduleName, ctorArgValueList))

        return instance


if __name__ == '__main__':
    # testing ConstructorArgsProvider
    dic = {'cl_2': ['clarg21', 'clarg22'],
           'cl_1': ['clarg11', 'clarg12'],
           'ca': ['ca_arg1'],
           'cc1': ['ccarg1'],
           'cc3': ['ccarg3'],
           'cc2': ['ccarg2']}
    cap = ConstructorArgsProvider(dic)
    print('cc {}'.format(cap.getArgsForClassConstructor('cc')))
    print('cl {}'.format(cap.getArgsForClassConstructor('cl')))
    print('ca {}'.format(cap.getArgsForClassConstructor('ca')))
    print()
    print('cc {}'.format(cap.getArgsForClassConstructor('cc')))
    print('cl {}'.format(cap.getArgsForClassConstructor('cl')))
    print('ca {}'.format(cap.getArgsForClassConstructor('ca')))
    print()
    print('cc {}'.format(cap.getArgsForClassConstructor('cc')))
    print('cl {}'.format(cap.getArgsForClassConstructor('cl')))
    print('ca {}'.format(cap.getArgsForClassConstructor('ca')))
