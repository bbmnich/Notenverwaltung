from dataclasses import dataclass

@dataclass
class Course:
    course_id: str
    name: str
    max_grade: float = 100.0
    passing_grade: float = 50.0

    def __str__(self):
        return f"Kurs: {self.name} ({self.course_id})"