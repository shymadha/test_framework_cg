from abc import ABC, abstractmethod

class BaseInterface(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute(self, command):
        pass

    @abstractmethod
    def close(self):
        pass
