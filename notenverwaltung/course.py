from dataclasses import dataclass

@dataclass
class Course:
    course_id: str
    course_name: str
    max_grade: float = 100.0
    passing_grade: float = 50.0

    def __post_init__(self):
        #IDs und Namen dürfen nicht leer sein
        if self.course_id == "":
            raise ValueError("Kurs-ID darf nicht leer sein.")
        if self.course_name == "":
            raise ValueError("Kursname darf nicht leer sein.")
        #Note muss groesser als 0 sein
        if self.max_grade <= 0:
            raise ValueError("Die maximale Note muss groesser als 0 sein.")
        #Note darf nicht 0 sein und nicht Groesser als Max_Note
        if self.passing_grade <= 0 or self.passing_grade > self.max_grade:
            raise ValueError("Die Note muss groesser als 0 und kleiner oder gleich der max_Note sein.")

def __str__(self):
    return f"Kurs: {self.course_name} ({self.course_id})"