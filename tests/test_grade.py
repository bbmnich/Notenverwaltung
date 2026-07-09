import pytest
from notenverwaltung.grade import GradeBook
from notenverwaltung.student import Student
from notenverwaltung.course import Course

@pytest.fixture
def test_gradebook():
    gb = GradeBook()
    
    
    s1 = Student("S01", "Barbara", "Mnich", "bmnich@coding.de")
    s2 = Student("S02", "Thomas", "Müller", "tmueller@coding.de")
    s3 = Student("S03", "Sabine", "Ohne-Note", "sabine@coding.de")
    
    # Zwei Kurse
    c1 = Course("C01", "Kochkurs", max_grade=100.0, passing_grade=50.0)
    c2 = Course("C02", "Mathekurs", max_grade=100.0, passing_grade=60.0)
    
    for s in [s1, s2, s3]: gb.add_student(s)
    for c in [c1, c2]: gb.add_course(c)
    
    
    # Barbara: Kochkurs 90 Punkte- Mathe 50 Punkte- Schnitt: 70%
    gb.record_grade("S01", "C01", 90.0)
    gb.record_grade("S01", "C02", 50.0)
    
    # Thomas: Kochkurs 80 Punkte- Mathe 80 Punkte - Schnitt- 80% Platz 1
    gb.record_grade("S02", "C01", 80.0)
    gb.record_grade("S02", "C02", 80.0)
    
    return gb

def test_statistics_and_edge_cases(test_gradebook):
    # Schnitte & Randfälle
    assert test_gradebook.student_average("S03") == 0.0      # Randfall Sabine hat keine Noten - Teilung durch 0
    assert test_gradebook.student_average("S01") == 70.0     
    assert test_gradebook.course_average("C01") == 85.0      

    # Bestehensquoten
    assert test_gradebook.course_pass_rate("C01") == 100.0   
    assert test_gradebook.course_pass_rate("C02") == 50.0    

    # Top & Gefährdete
    ergebnis_top = test_gradebook.top_students(1)
    assert len(ergebnis_top) == 1
    assert ergebnis_top[0].student_id == "S02"      # Thomas Müller  Platz 1
    
    assert test_gradebook.students_at_risk(75.0) == [test_gradebook.students[0]] # Barbara  ist unter 75%

def test_search_and_security(test_gradebook):
    # Regex-Muster (Gross/Klein & Teilwort)
    assert len(test_gradebook.search_students("barb")) == 1
    assert len(test_gradebook.search_students("BARB")) == 1
    assert len(test_gradebook.search_courses("the")) == 1

    # Interner Zustand geschützt
    treffer = test_gradebook.search_students("barb")
    treffer.clear() 
    assert len(test_gradebook.search_students("barb")) == 1