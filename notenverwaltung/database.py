import sqlite3


class DbManager:
    def __init__(self, db_name="notenverwaltung.db"):
        # Speichert den Dateinamen für die Datenbank
        self.db_name = db_name

    def get_connection(self):
        # Verbindung zur SQL herstellen
        conn = sqlite3.connect(self.db_name)
        # Verbindung aktivieren
        conn.execute("PRAGMA foreign_keys = ON;")
        # Zugriff auf Spalten über deren Namen
        conn.row_factory = sqlite3.Row
        return conn

    def create(self):
        #  Tabellen-Schema als SQL
        schema = """
        CREATE TABLE IF NOT EXISTS students ( student_id TEXT PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT NOT NULL;)
        CREATE TABLE IF NOT EXISTS courses (course_id TEXT PRIMARY KEY,name TEXT NOT NULL,max_grade REAL NOT NULL DEFAULT 100.0,passing_grade REAL NOT NULL DEFAULT 50.0);
        CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,course_id TEXT NOT NULL,score REAL NOT NULL,date TEXT NOT NULL,notes TEXT DEFAULT '',FOREIGN KEY (student_id) REFERENCES students(student_id),FOREIGN KEY (course_id) REFERENCES courses(course_id));"""
        # Führt das Schema aus und Speichern
        with self.get_connection() as conn:
            conn.executescript(schema)
            conn.commit()

    def add_student(self, student_id, first_name, last_name, email):
        # Fügt neuen Studenten hinzu oder ersetzt bei gleicher ID
        sql = "INSERT OR REPLACE INTO students (student_id, first_name, last_name, email) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            conn.execute(sql, (student_id, first_name, last_name, email))
            conn.commit()

    def add_course(self, course_id, name, max_grade, passing_grade):
        # Fügt neuen Kurs hinzu oder ersetzt bei gleicher ID
        sql = "INSERT OR REPLACE INTO courses (course_id, name, max_grade, passing_grade) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            conn.execute(sql, (course_id, name, max_grade, passing_grade))
            conn.commit()

    def add_grade(self, student_id, course_id, score, date, notes=""):
        # Speichert eine einzelne Note in die Tabelle
        sql = "INSERT INTO grades (student_id, course_id, score, date, notes) VALUES (?, ?, ?, ?, ?)"
        with self.get_connection() as conn:
            conn.execute(sql, (student_id, course_id, score, date, notes))
            conn.commit()
    
    
    
    def update_grade(self, grade_id, new_score):
        """Aktualisiert eine Note."""
        sql = "UPDATE grades SET score = ? WHERE id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (new_score, grade_id))
            conn.commit()

    def delete_student(self, student_id):
        """Löscht einen Studenten (und auch dessen Noten)."""
        sql = "DELETE FROM students WHERE student_id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (student_id,))
            conn.commit()    