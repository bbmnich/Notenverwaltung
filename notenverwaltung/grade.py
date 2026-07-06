from dataclasses import dataclass
from notenverwaltung.student import Student
from notenverwaltung.course import Course

@dataclass
class Grade:
    student: Student
    course: Course
    score: float

    def __post_init__(self):
        # Score muss zwischen 0 und der maximalen Kurs-Note liegen
        if self.score < 0 or self.score > self.course.max_grade:
            raise ValueError("Der Score muss zwischen 0 und der maximalen Note des Kurses liegen.")

    @property
    def is_passing(self):
        # Prueft ob die erreichte Punke zum Bestehen ausreichen.
        return self.score >= self.course.passing_grade

    @property
    def percentage(self):
        # Prozentsatz- erreichte Punkte / maximale Punkte * 100
        return (self.score / self.course.max_grade) * 100

    @property
    def letter_grade(self):
        # Ermittelt die Note durch den Prozentsatz
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
        # Status als Text
        status = "Nicht Bestanden"
        if self.is_passing:
            status = "Bestanden"
            
        # Prozentsatz fuer die Textausgabe auf 1 Nachkommastelle runden
        rounded_percentage = round(self.percentage, 1)
            
        return "Note: " + self.student.full_name + " in " + self.course.course_name + " - " + str(self.score) + " Punkte (" + str(rounded_percentage) + "%, Note: " + self.letter_grade + ", Status: " + status + ")"