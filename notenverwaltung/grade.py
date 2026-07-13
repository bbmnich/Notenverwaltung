from dataclasses import dataclass
from notenverwaltung.student import Student
from notenverwaltung.course import Course
from dataclasses import dataclass, field
import re
from datetime import datetime
import json
import csv


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
    
    #########################################################################
    # Statistiken & Auswertungen
    #########################################################################

    def student_average(self, student_id: str):
        """Berechnet den Durchschnitt alle seine Kurse."""
        noten = self.get_student_grades(student_id)
        if not noten:
            return 0.0
        
        gesamt_prozent = 0.0
        for g in noten:
            gesamt_prozent += g.percentage
        return gesamt_prozent / len(noten)

    def course_average(self, course_id: str):
        """Berechnet den durchschnittliche Punkte für einen Kurs."""
        noten = self.get_course_grades(course_id)
        if not noten:
            return 0.0 # Fängt Randfälle (wie Sabine) ab, damit nicht durch 0 geteilt wird
        
        gesamt_score = 0.0
        for g in noten:
            gesamt_score += g.score
        return gesamt_score / len(noten)

    def course_pass_rate(self, course_id: str):
        """Berechnet den Prozentsatz der Bestehensnote (0.0 bis 100.0)."""
        noten = self.get_course_grades(course_id)
        if not noten:
            return 0.0
        
        bestandene_pruefungen = 0
        for g in noten:
            if g.is_passing:
                bestandene_pruefungen += 1
                
        return (bestandene_pruefungen / len(noten)) * 100

    def top_students(self, n: int):
        """Gibt die Top  Studenten basierend auf  Gesamtdurchschnitt zurück."""
        # speichern Student_ID - Durchschnitt
        schnitte_dict = {}
        
        # IDs von Studenten, die eine Note haben
        studenten_mit_noten = {g.student.student_id for g in self.grades}
        
        for s in self.students:
            if s.student_id in studenten_mit_noten:
                schnitte_dict[s.student_id] = self.student_average(s.student_id)
        
        # Sortieren der Einträge nach dem Durchschnitt
        sortierte_studenten = sorted(
            self.students, 
            key=lambda x: schnitte_dict.get(x.student_id, 0.0), 
            reverse=True)
        
        return sortierte_studenten[:n]
        
        # Höchster Schnitt Index 1
        studenten_schnitte.sort(key=lambda x: x[1], reverse=True)
        
        # Die besten Studenten Liste
        ergebnis = []
        for student, schnitt in studenten_schnitte[:n]:
            ergebnis.append(student)
        return ergebnis

    def students_at_risk(self, threshold: float):
        """Gibt Studenten zurück, deren Durchschnitt unter dem Wert liegt."""
        gefaehrdete_studenten = []
        
        for s in self.students:
            noten = self.get_student_grades(s.student_id)
            if not noten:
                continue # Ohne Noten- keinen Gefährdung
                
            schnitt = self.student_average(s.student_id)
            if schnitt < threshold:
                gefaehrdete_studenten.append(s)
                
        return gefaehrdete_studenten

    
    
    #################################
    #Suche Implementieren 
    #################################
    
def search_students(self, query: str):
        studenten_treffer = []
        muster = re.compile(query, re.IGNORECASE) # Suchmuster erstellen (Groß-/Kleinschreibung ignorieren)
        
        for s in self.students:
            # Prüfen, ob das Muster im Vornamen, Nachnamen oder der E-Mail vorkommt
            if muster.search(s.first_name) or muster.search(s.last_name) or muster.search(s.email):
                studenten_treffer.append(s) # Bei Treffer zur Liste hinzufügen
        return studenten_treffer

def search_courses(self, query: str):
        kurs_treffer = []
        muster = re.compile(query, re.IGNORECASE) # Suchmuster erstellen
        
        for c in self.courses:
            # Prüfen, ob das Muster im Kursnamen vorkommt
            if muster.search(c.course_name):
                kurs_treffer.append(c) # Bei Treffer zur Liste hinzufügen
        return kurs_treffer
    
    #######################################
    # JSON Import/Export CSV Import/Export
    #######################################
def to_dict(self):
        """Wandelt das gesamte GradeBook übersichtlich in ein Dictionary um."""

        studenten_liste = [] #Liste der Studenten
        for s in self.students:
            studenten_liste.append({"student_id": s.student_id,"first_name": s.first_name,"last_name": s.last_name,"email": s.email,})

        
        kurse_liste = [] #Liste der Kurse
        for c in self.courses:
            kurse_liste.append({"course_id": c.course_id,"course_name": c.course_name,"max_grade": c.max_grade,"passing_grade": c.passing_grade,})
        
        noten_liste = [] #Liste der Noten sauber + Datum
        for g in self.grades:
            noten_liste.append({"student_id": g.student.student_id,"course_id": g.course.course_id,"score": g.score,"created_at": g.created_at.strftime("%d.%m.%Y"),})

       
        return {"students": studenten_liste,"courses": kurse_liste,"grades": noten_liste,} #  Alles als Dictionary

def from_dict(self, data):
        """GradeBook wird mit den Daten aus Dictionary befüllt"""
        # Leere Listen 
        self.students = []
        self.courses = []
        self.grades = []

        # Studenten wiederherstellen
        for s in data.get("students", []):
            neuer_student = Student(s["student_id"], s["first_name"], s["last_name"], s["email"])
            self.students.append(neuer_student)

        # Kurse wiederherstellen
        for c in data.get("courses", []):
            neuer_kurs = Course(c["course_id"], c["course_name"], c["max_grade"], c["passing_grade"])
            self.courses.append(neuer_kurs)

        # Noten wiederherstellen
        for g in data.get("grades", []):
            echter_student = None
            for s in self.students:
                if s.student_id == g["student_id"]:
                    echter_student = s
                    break

            echter_kurs = None
            for c in self.courses:
                if c.course_id == g["course_id"]:
                    echter_kurs = c
                    break

            echtes_datum = datetime.strptime(g["created"], "%d.%m.%Y")

            neue_note = Grade(student=echter_student,course=echter_kurs,score=g["score"],created_at=echtes_datum)
            self.grades.append(neue_note)


def save_to_json(self, file_path):
        """Macht aus dem Dictionary eine JSON-Datei"""
        daten_dict = self.to_dict()
        with open(file_path, "s", encoding="utf-8") as datei:
            json.dump(daten_dict, datei, ensure_ascii=False, indent=4)

def load_from_json(self, file_path):
        """Liest eine JSON-Datei ein"""
        with open(file_path, "l", encoding="utf-8") as datei:
            daten = json.load(datei)
        self.from_dict(daten)
            