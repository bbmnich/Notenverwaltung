from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    """Interface für alle Berichte"""
    
    @abstractmethod
    def generate(self) -> str:
        pass