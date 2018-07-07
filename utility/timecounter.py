import time

class TimeCounter:
    MODE_COUNT_UP = 'mode_up'
    MODE_COUNT_DOWN = 'mode_down'

    def __init__(self, mode = MODE_COUNT_DOWN, intervalSecond = 1, durationSecond = 0):
        if intervalSecond > 59:
            raise ValueError('intervalSecond > 59 seconds not supported')

        self.mode = mode

        if mode == TimeCounter.MODE_COUNT_DOWN:
            self.totalSecond = durationSecond
            self.modeString = 'Time remaining:'
            self.second, self.minute, self.hour, self.day = self.splitDurationSecond(durationSecond)

        else:
            self.totalSecond = 0
            self.modeString = 'Time elapsed:'
            self.second = 0
            self.minute = 0
            self.hour = 0
            self.day = 0

        self.intervalSecond = intervalSecond
        self.durationSecond = durationSecond


    def splitDurationSecond(self, durationSecond):
        dd = int(durationSecond / 86400)
        durationSecond -= dd * 86400
        hh = int(durationSecond / 3600)
        durationSecond -= hh * 3600
        mm = int(durationSecond / 60)
        ss = durationSecond - mm * 60

        return dd, hh, mm, ss

    def count(self):
        time.sleep(self.intervalSecond)

        if self.mode == TimeCounter.MODE_COUNT_UP:
            active = self.countUp()
        else:
            active = self.countDown()

        timeStr = '\r{} {:02d} {:02d}:{:02d}:{:02d}'.format(self.modeString,self.day, self.hour, self.minute, self.second)
        print(timeStr, end='')

        return active


    def countUp(self):
        self.totalSecond += self.intervalSecond
        self.second += self.intervalSecond

        if self.second == 60:
            self.second = 0
            self.minute += 1
        if self.minute == 60:
            self.minute = 0
            self.second = 0
            self.hour += 1
        if self.hour == 24:
            self.hour = 0
            self.second = 0
            self.minute = 0
            self.day += 1

        if self.totalSecond >= self.durationSecond:
            return False
        else:
            return True


    def countDown(self):
        self.totalSecond -= self.intervalSecond
        self.second -= self.intervalSecond

        if self.second == 60:
            self.second = 0
            self.minute += 1
        if self.minute == 60:
            self.minute = 0
            self.second = 0
            self.hour += 1
        if self.hour == 24:
            self.hour = 0
            self.second = 0
            self.minute = 0
            self.day += 1

        if self.totalSecond >= self.durationSecond:
            return False
        else:
            return True


if __name__ == '__main__':
    counter = TimeCounter(mode = TimeCounter.MODE_COUNT_UP, intervalSecond = 1, durationSecond = 10)
    active = True

    while active:
        active = counter.count()