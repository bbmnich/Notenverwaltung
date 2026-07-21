from abc import ABC, abstractmethod

class GradeStore(ABC):
    """Interface für alle Speicher-Varianten"""
    
    @abstractmethod
    def add_student(self, student):
        """Fügt einen neuen Studenten hinzu."""
        pass
    
    @abstractmethod
    def get_student(self, student_id):
        """Sucht einen Studenten mit der ID"""
        pass
    
    @abstractmethod
    def add_course(self, course):
        """Fügt einen neuen Kurs hinzu."""
        pass
        
    @abstractmethod
    def get_course(self, course_id):
        """Sucht einen Kurs mit der ID"""
        pass
    
    @abstractmethod
    def record_grade(self, grade):
        """Speichert ein Noten-Objekt"""
        pass
    
    @abstractmethod
    def get_student_grades(self, student_id):
        """Gibt eine Liste aller Noten für einen Studenten zurück."""
        pass

class InMemoryGradeStore(GradeStore):
    """Speicher-Variante für den Arbeitsspeicher (RAM)"""
    
    def __init__(self):
        self.students = []
        self.courses = []
        self.grades = []

    def add_student(self, student):
        self.students.append(student)

    def get_student(self, student_id):
        for s in self.students:
            if s.student_id == student_id:
                return s
        return None

    def add_course(self, course):
       self.db.add_course(course.course_id, course.title, course.max_grade, course.passing_grade)

    def get_course(self, course_id):
        for c in self.courses:
            if c.course_id == course_id:
                return c
        return None

    def record_grade(self, grade):
        self.grades.append(grade)

    def get_student_grades(self, student_id):
        result = []
        for g in self.grades:
            if g.student.student_id == student_id:
                result.append(g)
        return result

class SqliteGradeStore(GradeStore):
    """Implementierung für SQLite - leitet Anfragen an den DbManager weiter"""
    
    def __init__(self, db_manager):
        self.db = db_manager

    def add_student(self, student):
        # Übergibt die Studentendaten an den DBManager
        self.db.add_student(student.student_id, student.first_name, student.last_name, student.email)

    def get_student(self, student_id):
        # Sucht den Studenten mit ID
        return self.db.get_student_by_id(student_id)

    def add_course(self, course):
        # Übergibt alle Kursdaten an den DBManager (max_grade und passing_grade)
        self.db.add_course(course.course_id, course.name, course.max_grade, course.passing_grade)

    def get_course(self, course_id):
        # Sucht den Kurs mit seiner ID
        return self.db.get_course_by_id(course_id)

    def record_grade(self, grade):
        # Note in die Datenbank eintragen
        self.db.add_grade(grade.student.student_id, grade.course.course_id, grade.score, str(grade.created))

    def get_student_grades(self, student_id):
        # Gibt alle Noten zurück, von einem Studenten
        return self.db.get_grades_by_student(student_id)