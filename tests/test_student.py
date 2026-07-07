import pytest

from notenverwaltung.student import Student


def test_student_full_name():  # Testet das @property für den Namen
    student = Student(student_id="B501",first_name="Barbara",last_name="Mnich",email="bmnich@coding.de",)  # Test-Studenten anlegen

    assert (student.full_name == "Barbara Mnich")  # Prüft, ob das Property den Vornamen und Nachnamen richtig verbindet


def test_student_email():  # Testet, ob eine E-Mail ohne '@' ist
    with pytest.raises(ValueError, match="Muss ein @ enthalten."):
        # kein @ in der E-Mail
        Student(student_id="B501",first_name="Barbara",last_name="Mnich",email="bmnich-coding.de",)