from dataclasses import dataclass
from notenverwaltung.student import Student
from notenverwaltung.course import Course
from dataclasses import dataclass, field

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
    

    #########################################################################
    #GradeBook
    #########################################################################


@dataclass
class GradeBook:
    # Daten für Noten , Students und Kurse werden in einzelnen Listen gesammelt 
    grades: list[Grade] = field(default_factory=list)
    students: list[Student] = field(default_factory=list)
    courses: list[Course] = field(default_factory=list)

    def add_student(self, student: Student):
        """Prüft, ob die ID schon existiert."""
        for s in self.students:
            if s.student_id == student.student_id:
                raise ValueError("Student-ID existiert bereits im Notenbuch.")
        self.students.append(student)

    def add_course(self, course: Course):
        """Prüft, ob die Kurs ID schon existiert."""
        for c in self.courses:
            if c.course_id == course.course_id:
                raise ValueError("Kurs-ID existiert bereits im Notenbuch.")
        self.courses.append(course)

    def record_grade(self, student_id: str, course_id: str, score: float):
        """Sucht nach dem Studenten und dem Kurs , wenn nicht vorhanden , dann Fehlermeldung"""
        found_student = None
        for s in self.students:
            if s.student_id == student_id:
                found_student = s

        found_course = None
        for c in self.courses:
            if c.course_id == course_id:
                found_course = c

        if found_student is None:
            raise ValueError("Student wurde im Notenbuch nicht gefunden.")
        if found_course is None:
            raise ValueError("Kurs wurde im Notenbuch nicht gefunden.")

        # Wenn Student und Kurs existieren, wird die Note gespeichert
        new_grade = Grade(student=found_student, course=found_course, score=score)
        self.grades.append(new_grade)

    def get_student_grades(self, student_id: str):
        """Liste aller Noten für diesen einen Studenten."""
        filtered_grades = []
        for g in self.grades:
            if g.student.student_id == student_id:
                filtered_grades.append(g)
        return filtered_grades

    def get_course_grades(self, course_id: str):
        """Liste aller Noten für diesen einen Kurs."""
        filtered_grades = []
        for g in self.grades:
            if g.course.course_id == course_id:
                filtered_grades.append(g)
        return filtered_grades