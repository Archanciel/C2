import time
from threading import Thread
import sys


class TimeCounter(Thread):
    MODE_COUNT_UP = 'mode_up'
    MODE_COUNT_DOWN = 'mode_down'

    def __init__(self, mode = MODE_COUNT_DOWN, intervalSecond = 1, durationSecond = 0):
        '''

         In case a test list
        is passed as parm, the printed time string is added to the list.
        :param mode:
        :param intervalSecond:
        :param durationSecond:
        :param testTimeStrList: is value not None, the printed time string is appended to it
        '''
        Thread.__init__(self)
        self.mode = mode

        if mode == TimeCounter.MODE_COUNT_DOWN:
            self.totalSecond = durationSecond
            self.modeString = 'Time remaining:'
            self.splitDurationSecond(durationSecond)
            self.initialCountDownTimeStr = ' (from {:02d} {:02d}:{:02d}:{:02d})'.format(self.day, self.hour, self.minute, self.second)
        else:
            self.totalSecond = 0
            self.modeString = 'Time elapsed:'
            self.second = 0
            self.minute = 0
            self.hour = 0
            self.day = 0
            self.initialCountDownTimeStr = ''

        self.intervalSecond = intervalSecond
        self.durationSecond = durationSecond


    def run(self):
        active = True

        while active:
            active = self.count()

    def splitDurationSecond(self, durationSecond):
        '''
        Computes the time components corresponding to the passed duration in seconds.

        :param durationSecond:
        :return:
        '''
        self.day = int(durationSecond / 86400)
        durationSecond -= self.day * 86400
        self.hour = int(durationSecond / 3600)
        durationSecond -= self.hour * 3600
        self.minute = int(durationSecond / 60)
        self.second = durationSecond - self.minute * 60


    def count(self):
        '''
        Print a DD HH:MM:SS count down or elapsed time string in the console.

        :return:
        '''
        time.sleep(self.intervalSecond)

        if self.mode == TimeCounter.MODE_COUNT_UP:
            active = self.countUp()
        else:
            active = self.countDown()

        timeStr = '\r{} {:02d} {:02d}:{:02d}:{:02d}{}'.format(self.modeString, self.day, self.hour, self.minute, self.second, self.initialCountDownTimeStr)
#        print(timeStr, end='')
        sys.stdout.write(timeStr)
        sys.stdout.flush()

        return active


    def countUp(self):
        self.splitDurationSecond(self.totalSecond)
        self.totalSecond += self.intervalSecond

        if self.totalSecond > self.durationSecond:
            self.splitDurationSecond(self.totalSecond - 1)
            return False
        else:
            return True


    def countDown(self):
        self.splitDurationSecond(self.totalSecond)
        self.totalSecond -= self.intervalSecond

        if self.totalSecond < 0:
            self.splitDurationSecond(self.totalSecond + 1)
            return False
        else:
            return True


if __name__ == '__main__':
    counter = TimeCounter(mode = TimeCounter.MODE_COUNT_DOWN, intervalSecond = 1, durationSecond = 10)
    active = True

    while active:
        active = counter.count()

    print()

    counter = TimeCounter(mode = TimeCounter.MODE_COUNT_UP, intervalSecond = 1, durationSecond = 10)
    active = True

    while active:
        active = counter.count()

    print()

    counter = TimeCounter(mode = TimeCounter.MODE_COUNT_DOWN, intervalSecond = 1, durationSecond = 10)
    counter.start()
