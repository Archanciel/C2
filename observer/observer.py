from abc import ABCMeta
from abc import abstractmethod

class Observer(metaclass=ABCMeta):
    @abstractmethod
    def update(observable, arg):
        '''
        Called when the observed object is
        modified. You call an Observable object's
        notifyObservers method to notify all the
        object's observers of the change.
        '''
        pass
