from dataclasses import dataclass

@dataclass
class Course:
    course_id: str
    course_name: str
    max_grade: float = 100.0
    passing_grade: float = 50.0

class Course:
    def __init__(self, course_id, name, max_grade=100.0, passing_grade=50.0):
        self.course_id = course_id
        self.name = name
        self.max_grade = max_grade
        self.passing_grade = passing_grade

def __str__(self):
    return f"Kurs: {self.course_name} ({self.course_id})"