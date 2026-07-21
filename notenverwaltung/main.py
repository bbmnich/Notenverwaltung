from database import DbManager
from storage import SqliteGradeStore
from gradebook import GradeBook
from student import Student
from course import Course
from grade import Grade

def main():
    print("--- Starte Notenverwaltung ---")
    
    # Datenbank-Manager initialisieren
    db = DbManager("notenverwaltung.db")
    db.create()
    
    # SQLite-Store und GradeBook initialisieren
    store = SqliteGradeStore(db)
    book = GradeBook(store)
    
    # Test-Studenten und Kurs
    student = Student("S100", "Barbara", "Mnich", "bbmnich@example.com")
    course = Course("Python101", "Software Engineering", 100.0, 50.0)
    
    book.add_student(student)
    book.add_course(course)
    
    # Note erfassen
    grade = Grade(student, course, 92.5, "2026-07-20")
    book.record_grade(grade)
    print("Note gespeichert!")
    
    # Statistiken vergleichen
    print("\n--- Statistik-Vergleich ---")
    count_py, avg_py = book.get_student_statistics_python("S100")
    print(f"Python-Ansatz: {count_py} Noten, Durchschnitt = {avg_py}")
    
    count_sql, avg_sql = db.get_student_statistics_sql("S100")
    print(f"SQL-Ansatz:    {count_sql} Noten, Durchschnitt = {avg_sql}")
    
    # Kurs-Statistik (GROUP BY)
    print("\n--- Kurs-Statistik (GROUP BY) ---")
    kurs_stats = db.get_courses_statistics_sql()
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