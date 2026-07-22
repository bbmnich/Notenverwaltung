from .base import ReportGenerator

class TextReportGenerator(ReportGenerator):
    """Erstellt Berichte"""
    
    def __init__(self, gradebook):
        self.gradebook = gradebook

    def generate(self) -> str:
        # Platzhalter falls ein allgemeiner Report aufgerufen wird
        return self.generate_summary_report()

    def generate_student_report(self, student_id: str) -> str:
        student = self.gradebook.get_student(student_id)
        if not student:
            return f"Student mit ID {student_id} wurde nicht gefunden."
            
        grades = self.gradebook.get_student_grades(student_id)
        
        # Namen sicher auslesen (egal ob Objekt oder Dictionary)
        try:
            s_name = f"{student.first_name} {student.last_name}"
        except AttributeError:
            try:
                s_name = f"{student['first_name']} {student['last_name']}"
            except (KeyError, TypeError):
                s_name = "Unbekannt"

        report = []
        report.append("=" * 55)
        report.append("STUDENTEN-BERICHT")
        report.append("=" * 55)
        report.append(f"Student: {s_name} (ID: {student_id})")
        report.append("-" * 55)
        report.append(f"{'Kurs-ID':<12} | {'Note':<6} | {'Status':<15}")
        report.append("-" * 55)
        
        total_score = 0.0
        count = 0
        
        for g in grades:
            # Werte aus SQLite-Zeile oder Objekt extrahieren
            try:
                c_id = g['course_id']
                score = float(g['score'])
            except (KeyError, TypeError, IndexError):
                try:
                    c_id = g.course.course_id
                    score = float(g.score)
                except AttributeError:
                    continue
            
            # Bestehensgrenze des Kurses ermitteln
            passing_grade = 50.0
            course = self.gradebook.get_course(c_id)
            if course:
                try:
                    passing_grade = float(course['passing_grade'])
                except (KeyError, TypeError, ValueError):
                    try:
                        passing_grade = float(course.passing_grade)
                    except AttributeError:
                        pass
            
            status = "Bestanden" if score >= passing_grade else "Durchgefallen"
            report.append(f"{c_id:<12} | {score:<6} | {status:<15}")
            total_score += score
            count += 1
            
        report.append("-" * 55)
        avg = (total_score / count) if count > 0 else 0.0
        report.append(f"Gesamtanzahl Kurse: {count}")
        report.append(f"Notendurchschnitt:  {avg:.2f}")
        report.append("=" * 55)
        return "\n".join(report)

    def generate_course_report(self, course_id: str) -> str:
        course = self.gradebook.get_course(course_id)
        if not course:
            return f"Kurs mit ID {course_id} wurde nicht gefunden."
            
        # Noten direkt aus der Datenbank für diesen Kurs abrufen
        course_grades = []
        store = self.gradebook.store
        if hasattr(store, 'get_connection'):
            try:
                with store.get_connection() as conn:
                    cursor = conn.execute("SELECT * FROM grades WHERE course_id = ?", (course_id,))
                    course_grades = cursor.fetchall()
            except Exception:
                pass

        c_name = "Unbekannt"
        try:
            c_name = course['name']
        except (KeyError, TypeError):
            try:
                c_name = course.name
            except AttributeError:
                pass

        passing_grade = 50.0
        try:
            passing_grade = float(course['passing_grade'])
        except (KeyError, TypeError, ValueError):
            try:
                passing_grade = float(course.passing_grade)
            except AttributeError:
                pass

        report = []
        report.append("=" * 55)
        report.append(f"KURS-BERICHT: {c_name} ({course_id})")
        report.append("=" * 55)
        
        if not course_grades:
            report.append("Keine Noten für diesen Kurs erfasst.")
        else:
            scores = []
            for g in course_grades:
                try:
                    scores.append(float(g['score']))
                except (KeyError, TypeError, ValueError, IndexError):
                    try:
                        scores.append(float(g.score))
                    except AttributeError:
                        pass
            
            # Variablen sauber definieren
            class_avg = (sum(scores) / len(scores)) if scores else 0.0
            passed_count = sum(1 for s in scores if s >= passing_grade)
            pass_rate = (passed_count / len(scores) * 100) if scores else 0.0
            
            report.append(f"Anzahl Teilnehmer:   {len(scores)}")
            report.append(f"Klassendurchschnitt: {class_avg:.2f}")
            report.append(f"Bestehensquote:      {pass_rate:.1f}% ({passed_count} von {len(scores)} bestanden)")
            report.append("-" * 55)
            report.append("Leistungen der Studenten:")
            
            for g in course_grades:
                try:
                    score = float(g['score'])
                except (KeyError, TypeError, ValueError, IndexError):
                    try:
                        score = float(g.score)
                    except AttributeError:
                        score = 0.0
                
                try:
                    s_id = g['student_id']
                except (KeyError, TypeError, IndexError):
                    try:
                        s_id = g.student_id
                    except AttributeError:
                        s_id = 'Unbekannt'
                
                student_obj = self.gradebook.get_student(s_id)
                s_name = "Student"
                if student_obj:
                    try:
                        s_name = f"{student_obj['first_name']} {student_obj['last_name']}"
                    except (KeyError, TypeError):
                        try:
                            s_name = f"{student_obj.first_name} {student_obj.last_name}"
                        except AttributeError:
                            pass
                
                status = "Bestanden" if score >= passing_grade else "Durchgefallen"
                report.append(f"  • {s_id} ({s_name}): {score} ({status})")
                
        report.append("=" * 55)
        return "\n".join(report)

    def generate_summary_report(self) -> str:
        store = self.gradebook.store
        student_count = 0
        course_count = 0
        total_grades = 0
        global_avg = 0.0
        
        if hasattr(store, 'get_connection'):
            try:
                with store.get_connection() as conn:
                    # Anzahl Studenten ermitteln
                    res_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()
                    student_count = res_students[0] if res_students else 0
                    
                    # Anzahl Kurse ermitteln
                    res_courses = conn.execute("SELECT COUNT(*) FROM courses").fetchone()
                    course_count = res_courses[0] if res_courses else 0
                    
                    # Noten-Statistik gesamt ermitteln
                    res_grades = conn.execute("SELECT COUNT(score), AVG(score) FROM grades").fetchone()
                    if res_grades:
                        total_grades = res_grades[0] or 0
                        global_avg = res_grades[1] or 0.0
            except Exception:
                pass

        report = []
        report.append("=" * 55)
        report.append("GESAMT-REPORT")
        report.append("=" * 55)
        report.append(f"Studenten Gesamt: {student_count}")
        report.append(f"Kurse Gesamt:    {course_count}")
        report.append(f"Erfasste Noten gesamt: {total_grades}")
        report.append(f"Notenschnitt:  {global_avg:.2f}")
        report.append("=" * 55)
        return "\n".join(report)