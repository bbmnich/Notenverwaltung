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
        # Tabellen-Schema als SQL
        schema = """
        CREATE TABLE IF NOT EXISTS students ( student_id TEXT PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS courses (course_id TEXT PRIMARY KEY,name TEXT NOT NULL,max_grade REAL NOT NULL DEFAULT 100.0,passing_grade REAL NOT NULL DEFAULT 50.0);
        CREATE TABLE IF NOT EXISTS grades (id INTEGER PRIMARY KEY AUTOINCREMENT,student_id TEXT NOT NULL,course_id TEXT NOT NULL,score REAL NOT NULL,date TEXT NOT NULL,notes TEXT DEFAULT '',FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,FOREIGN KEY (course_id) REFERENCES courses(course_id));"""
        # Führt das Schema aus und Speichern
        with self.get_connection() as conn:
            conn.executescript(schema)
            conn.commit()

    def add_student(self, student_or_id, first_name=None, last_name=None, email=None):
        """
        Fügt einen neuen Studenten hinzu oder ersetzt ihn bei gleicher ID.
        Unterstützt sowohl die Übergabe eines Student-Objekts als auch von Einzelwerten.
        """
        # Prüfen, ob ein Student-Objekt übergeben wurde
        if hasattr(student_or_id, 'student_id'):
            s_id = student_or_id.student_id
            f_name = student_or_id.first_name
            l_name = student_or_id.last_name
            mail = student_or_id.email
        else:
            # Einzelwerte wurden übergeben
            s_id = student_or_id
            f_name = first_name
            l_name = last_name
            mail = email

        sql = "INSERT OR REPLACE INTO students (student_id, first_name, last_name, email) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            conn.execute(sql, (s_id, f_name, l_name, mail))
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
        """Löscht einen Studenten (auch die Noten)."""
        sql = "DELETE FROM students WHERE student_id = ?"
        with self.get_connection() as conn:
            conn.execute(sql, (student_id,))
            conn.commit()    


    def get_student_by_id(self, student_id):
        """Sucht einen Studenten mit ID"""
        sql = "SELECT * FROM students WHERE student_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_id,))
            return cursor.fetchone()

    def get_course_by_id(self, course_id):
        """Sucht einen Kurs mit ID"""
        sql = "SELECT * FROM courses WHERE course_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (course_id,))
            return cursor.fetchone()

    def get_grades_by_student(self, student_id):
        """Gibt alle Noten eines Studenten zurück"""
        sql = "SELECT * FROM grades WHERE student_id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(sql, (student_id,))
            return cursor.fetchall()
        
    def get_all_grades(self):
        """Gibt alle Noten als Liste von sqlite3.Row zurück."""
        sql = "SELECT * FROM grades"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()

    def get_all_students(self):
        """Gibt alle Studenten als Liste von sqlite3.Row zurück."""
        sql = "SELECT * FROM students"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()

    def add_course(self, course_or_id, name=None, max_grade=100.0, passing_grade=50.0):
        """
        Fügt einen Kurs hinzu oder ersetzt ihn bei gleicher ID.
        Unterstützt sowohl Course-Objekte als auch Einzelwerte.
        """
        if hasattr(course_or_id, 'course_id'):
            c_id = course_or_id.course_id
            c_name = course_or_id.name
            c_max = getattr(course_or_id, 'max_grade', 100.0)
            c_pass = getattr(course_or_id, 'passing_grade', 50.0)
        else:
            c_id = course_or_id
            c_name = name
            c_max = max_grade
            c_pass = passing_grade

        sql = "INSERT OR REPLACE INTO courses (course_id, name, max_grade, passing_grade) VALUES (?, ?, ?, ?)"
        with self.get_connection() as conn:
            conn.execute(sql, (c_id, c_name, c_max, c_pass))
            conn.commit()
######################################
    #Statistik-Methoden
######################################
    def get_student_statistics_sql(self, student_id):
        """Berechnet die Anzahl und den Durchschnitt der Noten in der Datenbank via SQL"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SQL-Abfrage: Zählt alle Noten (COUNT) und berechnet den Durchschnitt (AVG)
            query = """SELECT COUNT(score), AVG(score) FROM grades WHERE student_id = ?"""
            cursor.execute(query, (student_id,))
            result = cursor.fetchone()  # Holt das Ergebnis aus der Datenbank
            
        # Falls keine Noten gefunden wurden dann 0 und 0.0 zurück
        if result is None or result[0] == 0:
            return 0, 0.0
        return result[0], result[1]
    
    def get_courses_statistics_sql(self):
        """Gibt Anzahl und Durchschnitt aller Noten, gruppiert nach Kurs (GROUP BY)"""
        sql = "SELECT course_id, COUNT(score), AVG(score) FROM grades GROUP BY course_id"
        with self.get_connection() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()