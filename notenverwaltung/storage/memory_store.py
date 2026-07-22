
from .base import GradeStore

class InMemoryGradeStore(GradeStore):
    """Speicher-Variante für den Arbeitsspeicher (RAM)"""
    
    def __init__(self):
        self.students = []
        self.courses = []
        self.grades = []

    def add_student(self, student):
        self.students.append(student)

    def get_student(self, student_id):
        for s in self.students:
            if s.student_id == student_id:
                return s
        return None
    def add_course(self, course):
       self.courses.append(course)
    
    def get_course(self, course_id):
        for c in self.courses:
            if c.course_id == course_id:
                return c
        return None

    def record_grade(self, grade):
        self.grades.append(grade)

    def get_student_grades(self, student_id):
        result = []
        for g in self.grades:
            if g.student.student_id == student_id:
                result.append(g)
        return result
