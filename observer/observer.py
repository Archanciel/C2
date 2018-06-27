from abc import ABCMeta
from abc import abstractmethod

class Observer(metaclass=ABCMeta):
    @abstractmethod
    def update(self, arg):
        '''
        Called when the observed object is
        modified. You call an Observable object's
        notifyObservers method to notify all the
        object's observers of the change.
        '''
        pass

    @abstractmethod
    def close(self):
        '''
        Called when the observed object is
        closed and has stopped notifying all the
        object's observers of the change.
        '''
        pass
