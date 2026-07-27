from dataclasses import dataclass

@dataclass
class Course:
    course_id: str
    name: str
    max_grade: float = 100.0
    passing_grade: float = 50.0

    def __post_init__(self):
        # Division durch 0 wird nicht geben
        if self.max_grade <= 0:
            raise ValueError("Die maximale Note muss größer als 0 sein.")
        # Prüfung für die Bestehen-Note
        if self.passing_grade < 0 or self.passing_grade > self.max_grade:
            raise ValueError("Die Bestehensgrenze muss zwischen 0 und der maximalen Note liegen.")

    def __str__(self):
        return f"Kurs: {self.name} ({self.course_id})"