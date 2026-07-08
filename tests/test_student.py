import pytest
from notenverwaltung.student import Student



# Erkennt einen leeren Vornamen
def test_student_empty_first_name():
    with pytest.raises(ValueError):
        Student(student_id="B501",first_name="",last_name="Mnich",email="bmnich@coding.de",)

# Erkennt einen leeren Nachnamen
def test_student_empty_last_name():
    with pytest.raises(ValueError):
        Student(student_id="B501",first_name="Barbara",last_name="",email="bmnich@coding.de",)

# Erkennt eine leere ID?
def test_student_empty_id():
    with pytest.raises(ValueError):
        Student(student_id="",first_name="Barbara",last_name="Mnich",email="bmnich@coding.de",)

# Erkennt dass eine falsche E-Mail (ohne @)
def test_student_email():
    with pytest.raises(ValueError):
        Student(student_id="B501",first_name="Barbara",last_name="Mnich",email="bmnich-coding.de",)

# Prüft, ob Vor- und Nachname richtig zusammen ausgegeben werden 
def test_student_full_name():
    student = Student(student_id="B501",first_name="Barbara",last_name="Mnich",email="bmnich@coding.de",)
    assert student.full_name == "Barbara Mnich"