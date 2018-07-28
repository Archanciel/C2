from abc import ABCMeta
from abc import abstractmethod

class Observable(metaclass=ABCMeta):
    '''
    :seqdiag_note Pivot class in the Observable design pattern. Each time its notifyObservers(data) method is called, Observable notifies its subscribed Observers of the received data calling update(data) on each registered Observer.
    '''
    def __init__(self):
        self.obs = []

    def addObserver(self, observer):
        if observer not in self.obs:
            self.obs.append(observer)

    def deleteObserver(self, observer):
        self.obs.remove(observer)

    def notifyObservers(self, data):
        '''
        Each observer has its
        update() called with one argument: the generic 'data'.
        '''

        for observer in self.obs:
            observer.update(self.processData(data))

    def deleteObservers(self):
        self.obs = []

    def countObservers(self):
        return len(self.obs)

    def processData(self, data):
        return data

    def stopObservable(self):
        '''
        Notifies the Observers that the Observable has stopped notifying them
        updates.

        :return:
        '''

        for observer in self.obs:
            observer.close()
