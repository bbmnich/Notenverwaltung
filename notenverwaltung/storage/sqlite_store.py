import sqlite3
from datetime import datetime
from .base import GradeStore
from ..models.student import Student
from ..models.course import Course
from ..models.grade import Grade

class SqliteGradeStore(GradeStore):
    """Direkte SQLite-Implementierung für das Speicher-Interface"""
    
    def __init__(self, db_path="notenverwaltung.db"):
        self.db_path = db_path
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        """Erstellt die Tabellen, falls sie noch nicht existieren"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    course_id TEXT PRIMARY KEY,
                    name TEXT,
                    max_grade REAL,
                    passing_grade REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    course_id TEXT,
                    score REAL,
                    created TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (student_id),
                    FOREIGN KEY (course_id) REFERENCES courses (course_id)
                )
            """)
            conn.commit()

    def add_student(self, student):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO students (student_id, first_name, last_name, email) VALUES (?, ?, ?, ?)",
                (student.student_id, student.first_name, student.last_name, student.email)
            )
            conn.commit()

    def get_student(self, student_id):
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                return Student(row["student_id"], row["first_name"], row["last_name"], row["email"])
            return None

    def add_course(self, course):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO courses (course_id, name, max_grade, passing_grade) VALUES (?, ?, ?, ?)",
                (course.course_id, course.name, course.max_grade, course.passing_grade)
            )
            conn.commit()

    def get_course(self, course_id):
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
            row = cursor.fetchone()
            if row:
                return Course(row["course_id"], row["name"], row["max_grade"], row["passing_grade"])
            return None

    def record_grade(self, grade):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO grades (student_id, course_id, score, created) VALUES (?, ?, ?, ?)",
                (grade.student.student_id, grade.course.course_id, grade.score, grade.created.strftime("%Y-%m-%d"))
            )
            conn.commit()

    def get_student_grades(self, student_id):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT g.*, s.first_name, s.last_name, s.email, 
                       c.name as course_name, c.max_grade, c.passing_grade
                FROM grades g
                JOIN students s ON g.student_id = s.student_id
                JOIN courses c ON g.course_id = c.course_id
                WHERE g.student_id = ?
            """, (student_id,))
            rows = cursor.fetchall()
            grades = []
            for row in rows:
                student = Student(row["student_id"], row["first_name"], row["last_name"], row["email"])
                course = Course(row["course_id"], row["course_name"], row["max_grade"], row["passing_grade"])
                created_date = datetime.strptime(row["created"], "%Y-%m-%d")
                grades.append(Grade(student=student, course=course, score=row["score"], created=created_date))
            return grades

    def get_student_statistics_sql(self, student_id):
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(score), AVG(score) FROM grades WHERE student_id = ?", 
                (student_id,)
            )
            row = cursor.fetchone()
            return (row[0] or 0, row[1] or 0.0)

    def get_courses_statistics_sql(self):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT course_id, COUNT(score), AVG(score) 
                FROM grades 
                GROUP BY course_id
            """)
            return cursor.fetchall()