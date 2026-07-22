from dataclasses import dataclass
from datetime import datetime
from .student import Student
from .course import Course

@dataclass
class Grade:
    student: Student
    course: Course
    score: float
    created: datetime

    def __post_init__(self):
        # Score muss zwischen 0 und der maximalen Kurs-Note liegen
        if self.score < 0 or self.score > self.course.max_grade:
            raise ValueError("Der Score muss zwischen 0 und der maximalen Note des Kurses liegen.")

    @property
    def is_passing(self) -> bool:
        # Prüft, ob die Punkte zum Bestehen ausreichen
        return self.score >= self.course.passing_grade

    @property
    def percentage(self) -> float:
        # Prozentsatz berechnen
        return (self.score / self.course.max_grade) * 100

    @property
    def letter_grade(self) -> str:
        # Letter Grade ermitteln
        p = self.percentage
        if p >= 90:
            return "A"
        if p >= 80:
            return "B"
        if p >= 70:
            return "C"
        if p >= 60:
            return "D"
        return "F"

    def __str__(self):
        status = "Bestanden" if self.is_passing else "Nicht Bestanden"
        rounded_percentage = round(self.percentage, 1)
        return (
            f"Note: {self.student.full_name} in {self.course.name} - "
            f"{self.score} Punkte ({rounded_percentage}%, Note: {self.letter_grade}, Status: {status})"
        )