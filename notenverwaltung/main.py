from datetime import datetime
from .storage import SqliteGradeStore
from .gradebook import GradeBook
from .models.student import Student
from .models.course import Course
from .models.grade import Grade

def main():
    print("--- Starte Notenverwaltung ---")
    
    # SQLite-Store und GradeBook initialisieren
    store = SqliteGradeStore("notenverwaltung.db")
    book = GradeBook(store)

    # Alte Testdaten vor dem Start bereinigen, damit nichts doppelt ist
    with store.get_connection() as conn:
        conn.execute("DELETE FROM grades")
        conn.execute("DELETE FROM students")
        conn.execute("DELETE FROM courses")
        conn.commit()
    
    # Test-Studenten und Kurs
    student = Student("S100", "Barbara", "Mnich", "bbmnich@example.com")
    course = Course("Python101", "Software Engineering", 100.0, 50.0)
    
    book.add_student(student)
    book.add_course(course)
    
    # Note erfassen
    grade = Grade(student, course, 92.5, datetime(2026, 7, 20))
    book.record_grade(grade)
    print("Note gespeichert!")
    
    # Statistiken vergleichen
    print("\n--- Statistik-Vergleich ---")
    count_py, avg_py = book.get_student_statistics_python("S100")
    print(f"Python-Ansatz: {count_py} Noten, Durchschnitt = {avg_py}")
    
    count_sql, avg_sql = store.get_student_statistics_sql("S100")
    print(f"SQL-Ansatz:    {count_sql} Noten, Durchschnitt = {avg_sql}")
    
    # Kurs-Statistik (GROUP BY)
    print("\n--- Kurs-Statistik (GROUP BY) ---")
    kurs_stats = store.get_courses_statistics_sql()
    for row in kurs_stats:
        print(f"Kurs-ID: {row['course_id']}, Anzahl Noten: {row['COUNT(score)']}, Schnitt: {row['AVG(score)']}")

    # Berichte aufrufen
    print("\n")
    print(book.generate_student_report("S100"))
    
    print("\n")
    print(book.generate_course_report("Python101"))
    
    print("\n")
    print(book.generate_summary_report())

if __name__ == "__main__":
    main()