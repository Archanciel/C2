import re

class PatternMatcher:
    '''
    Utility class in charge of pattern matching tasks
    '''

    @staticmethod
    def extractDateTimeStrFrom(primaryFileName):
        pattern = r"(\w*)-([0-9-]*).csv"

        match = re.match(pattern, primaryFileName)

        if match:
            dateTimeStr = match.group(2)

            return dateTimeStr

    @staticmethod
    def getDurationStrTuple(durationStr):
        '''
        Parses a duraton string like 22 for 22 seconds or 7-22 for 7 minutes 22 seconds
        and returns a tuple containing up to 4 strings for day, hour, minute and second.

        :param durationStr:

        :return: tuple of time value strings
        '''
        patternList = [r"(?:(\d{1,2})-(\d{1,2})-(\d{1,2})-(\d{1,2}))", r"(?:(\d{1,2})-(\d{1,2})-(\d{1,2}))", r"(?:(\d{1,2})-(\d{1,2}))", r"(\d{1,2})"]

        for pattern in patternList:
            match = re.match(pattern, durationStr)
            if match:
                return match.groups()
