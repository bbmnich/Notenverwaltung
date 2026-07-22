from .storage.base import GradeStore
from .reports.text_report import TextReportGenerator

class GradeBook:
    """Verwaltet Noten, Studenten und Kurse über ein Speicher-Interface."""
    
    def __init__(self, store: GradeStore):
        self.store = store
        # Bindet den Text-Report-Generator ein und übergibt sich selbst
        self.text_reporter = TextReportGenerator(self)

    def add_student(self, student):
        self.store.add_student(student)

    def get_student(self, student_id):
        return self.store.get_student(student_id)

    def add_course(self, course):
        self.store.add_course(course)

    def get_course(self, course_id):
        return self.store.get_course(course_id)

    def record_grade(self, grade):
        self.store.record_grade(grade)

    def get_student_grades(self, student_id):
        return self.store.get_student_grades(student_id)

    def get_student_statistics_python(self, student_id):
        """Berechnet Anzahl und Durchschnitt der Noten für einen Studenten."""
        grades = self.get_student_grades(student_id)
        if not grades:
            return 0, 0.0
        count = len(grades)
        total_score = sum(g.score if hasattr(g, 'score') else g['score'] for g in grades)
        average = total_score / count
        return count, average

    # ==========================================
    # BERICHTE (an TextReportGenerator)
    # ==========================================
    def generate_student_report(self, student_id: str) -> str:
        return self.text_reporter.generate_student_report(student_id)

    def generate_course_report(self, course_id: str) -> str:
        return self.text_reporter.generate_course_report(course_id)

    def generate_summary_report(self) -> str:
        return self.text_reporter.generate_summary_report()