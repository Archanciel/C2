from abc import ABCMeta
from abc import abstractmethod

class Observable(metaclass=ABCMeta):
    def __init__(self):
        self.obs = []

    def addObserver(self, observer):
        if observer not in self.obs:
            self.obs.append(observer)

    def deleteObserver(self, observer):
        self.obs.remove(observer)

    def notifyObservers(self, data = None):
        '''
        Each observer has its
        update() called with two arguments: this
        observable object and the generic 'arg'.
        '''

        for observer in self.obs:
            observer.update(self.processData(data))

    def deleteObservers(self):
        self.obs = []

    def countObservers(self):
        return len(self.obs)

    @abstractmethod
    def processData(self, data):
        pass