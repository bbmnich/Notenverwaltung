
from abc import ABC, abstractmethod


class GradeStore(ABC):
    """Interface für alle Speicher-Varianten"""
    
    @abstractmethod
    def add_student(self, student):
        """Fügt einen neuen Studenten hinzu."""
        pass
    
    @abstractmethod
    def get_student(self, student_id):
        """Sucht einen Studenten mit der ID"""
        pass
    
    @abstractmethod
    def add_course(self, course):
        """Fügt einen neuen Kurs hinzu."""
        pass
        
    @abstractmethod
    def get_course(self, course_id):
        """Sucht einen Kurs mit der ID"""
        pass
    
    @abstractmethod
    def record_grade(self, grade):
        """Speichert ein Noten-Objekt"""
        pass
    
    @abstractmethod
    def get_student_grades(self, student_id):
        """Gibt eine Liste aller Noten für einen Studenten zurück."""
        pass