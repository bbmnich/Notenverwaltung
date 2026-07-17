from dataclasses import dataclass, field
from grade import Student, Course, Grade
from datetime import datetime


@dataclass
class GradeBook:
    # Noten, Students und Kurse werden in Listen gesammelt 
    grades: list[Grade] = field(default_factory=list)
    students: list[Student] = field(default_factory=list)
    courses: list[Course] = field(default_factory=list)

    def add_student(self, student: Student):
        """Prüft, ob die ID existiert."""
        for s in self.students:
            if s.student_id == student.student_id:
                raise ValueError("Student-ID existiert im Notenbuch.")
        self.students.append(student)

    def add_course(self, course: Course):
        """Prüft, ob die Kurs ID schon existiert."""
        for c in self.courses:
            if c.course_id == course.course_id:
                raise ValueError("Kurs-ID existiert im Notenbuch.")
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
        new_grade = Grade(student=found_student, course=found_course, score=score, created=datetime.now())
        self.grades.append(new_grade)

    def get_student_grades(self, student_id: str):
        """Liste aller Noten für diesen Studenten."""
        filtered_grades = []
        for g in self.grades:
            if g.student.student_id == student_id:
                filtered_grades.append(g)
        return filtered_grades

    def get_course_grades(self, course_id: str):
        """Liste aller Noten für diesen Kurs."""
        filtered_grades = []
        for g in self.grades:
            if g.course.course_id == course_id:
                filtered_grades.append(g)
        return filtered_grades
    #######################################
    #DB Anbindung
    #######################################
    

    def save_to_database(self, db_manager):
        """Speichert alle Daten"""
        # Studenten speichern
        for s in self.students:
            db_manager.add_student(s.student_id, s.first_name, s.last_name, s.email)
        
        # Kurse speichern
        for c in self.courses:
            db_manager.add_course(c.course_id, c.course_name, c.max_grade, c.passing_grade)
            
        # Noten speichern
        for g in self.grades:
            datum_str = g.created.strftime("%d.%m.%Y")
            db_manager.add_grade(g.student.student_id, g.course.course_id, g.score, datum_str)
        
        print("Daten wurden gespeichert")