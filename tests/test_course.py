import pytest
from Notenverwaltung_Projekt.notenverwaltung.models.course import Course


# prüft ob Kurs korrekt angelegt wird
def test_course_creation():
    course = Course(course_id="K555",course_name="Kochen lernen",max_grade=100.0,passing_grade=50.0,)
    assert course.course_id == "K555"
    assert course.course_name == "Kochen lernen"


# Leere Kurs-ID prüfen
def test_course_empty_id():
    with pytest.raises(ValueError):
        Course(course_id="", course_name="Kochen lernen")


# leeren Kursnamen prüfen
def test_course_empty_name():
    with pytest.raises(ValueError):
        Course(course_id="K555", course_name="")


# maximale Note 0 oder kleiner
def test_course_invalid_max_grade():
    with pytest.raises(ValueError):
        Course(course_id="K555", course_name="Kochen lermnen", max_grade=0)


# Note für Bestehen ungültig  (höher als Max)
def test_course_invalid_passing_grade():
    with pytest.raises(ValueError):
        Course(course_id="K555",course_name="Kochen lernen",max_grade=100.0,passing_grade=150.0,)  # Höher als max Note