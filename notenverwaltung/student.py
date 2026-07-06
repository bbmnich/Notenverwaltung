from dataclasses import dataclass

@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: str

    def __post_init__(self):
        #ID darf nicht leer sein
        if self.student_id == "":
            raise ValueError("Student-ID darf nicht leer sein.")
        # Namen dürfen nicht leer sein
        if self.first_name == "":
            raise ValueError("Vorname darf nicht leer sein.")
        if self.last_name == "":
            raise ValueError("Nachname darf nicht leer sein.")
            #E-Mail muss ein @ enthalten
        if "@" not in self.email:
            raise ValueError("Ungueltige E-Mail-Adresse: Muss ein @ enthalten.")

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return "Student: " + self.full_name + " (" + self.student_id + ") - E-Mail: " + self.email