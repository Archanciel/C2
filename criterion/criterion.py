from abc import ABCMeta
from abc import abstractmethod

class Criterion(metaclass=ABCMeta):
    @abstractmethod
    def check(self, data):
        '''
        Check if the criterion is reached.
        '''
        pass


if __name__ == '__main__':
    pass