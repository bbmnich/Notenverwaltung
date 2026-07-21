from storage import GradeStore

class GradeBook:
    """Verwaltet Noten, Studenten und Kurse über ein Speicher-Interface."""
    
    def __init__(self, store: GradeStore):
        self.store = store

    def add_student(self, student):
        self.store.add_student(student)

    def get_student(self, student_id):
        return self.store.get_student(student_id)

    def add_course(self, course):
        self.store.add_course(course)

    def get_course(self, course_id):
        return self.store.get_course(course_id)

    def record_grade(self, grade):
        self.store.record_grade(grade)

    def get_student_grades(self, student_id):
        return self.store.get_student_grades(student_id)

    def get_student_statistics_python(self, student_id):
        """Berechnet Anzahl und Durchschnitt der Noten für einen Studenten."""
        grades = self.get_student_grades(student_id)
        if not grades:
            return 0, 0.0
        count = len(grades)
        total_score = sum(g.score if hasattr(g, 'score') else g['score'] for g in grades)
        average = total_score / count
        return count, average

    # ==========================================
    # STUDENT REPORT
    # ==========================================
    def generate_student_report(self, student_id: str) -> str:
        """Erstellt einen Notenbericht für einen Studenten.Beinhaltet alle Noten, den Durchschnitt und den Bestanden/Nicht-Bestanden-Status pro Kurs."""
        student = self.get_student(student_id)
        if not student:
            return f"Student mit ID {student_id} wurde nicht gefunden."
            
        grades = self.get_student_grades(student_id)
        count, average = self.get_student_statistics_python(student_id)
        
        # Name des Studenten auslesen
        if hasattr(student, 'first_name'):
            name_str = f"{student.first_name} {student.last_name}"
        else:
            try:
                name_str = f"{student['first_name']} {student['last_name']}"
            except (KeyError, TypeError):
                name_str = "Unbekannter Student"

        report = []
        report.append("=" * 55)
        report.append("STUDENTEN-BERICHT (ZEUGNIS)")
        report.append("=" * 55)
        report.append(f"Student: {name_str} (ID: {student_id})")
        report.append("-" * 55)
        
        if not grades:
            report.append("Keine Noten für diesen Studenten eingetragen.")
        else:
            report.append(f"{'Kurs-ID':<12} | {'Note':<6} | {'Status':<15}")
            report.append("-" * 55)
            for g in grades:
                if hasattr(g, 'score'):
                    score = g.score
                else:
                    try:
                        score = g['score']
                    except (KeyError, TypeError):
                        score = 0.0
                
                # Kurs und Bestehensgrenze ermitteln
                if hasattr(g, 'course') and hasattr(g.course, 'course_id'):
                    c_id = g.course.course_id
                    passing_grade = getattr(g.course, 'passing_grade', 50.0)
                else:
                    try:
                        c_id = g['course_id']
                    except (KeyError, TypeError):
                        c_id = 'Unbekannt'
                    passing_grade = 50.0 
                
                status = "Bestanden" if score >= passing_grade else "Nicht bestanden"
                report.append(f"{str(c_id):<12} | {score:<6.1f} | {status:<15}")
                
        report.append("-" * 55)
        report.append(f"Gesamtanzahl Kurse: {count}")
        report.append(f"Notendurchschnitt:  {average:.2f}")
        report.append("=" * 55)
        
        return "\n".join(report)

    # ==========================================
    # COURSE REPORT
    # ==========================================
    def generate_course_report(self, course_id: str) -> str:
        """Erstellt einen Bericht für einen Kurs.Beinhaltet alle Studentenleistungen, den Klassendurchschnitt sowie die Bestehensquote."""
        course = self.get_course(course_id)
        if not course:
            return f"Kurs mit ID {course_id} wurde nicht gefunden."
            
        # Noten direkt aus der Datenbank für diesen Kurs abrufen
        course_grades = []
        db_ref = getattr(self.store, 'db', None)
        if db_ref and hasattr(db_ref, 'get_connection'):
            try:
                with db_ref.get_connection() as conn:
                    cursor = conn.execute("SELECT * FROM grades WHERE course_id = ?", (course_id,))
                    course_grades = cursor.fetchall()
            except Exception:
                pass

        # Kursname und Bestehensgrenze auslesen
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
            except (AttributeError, ValueError, TypeError):
                pass

        report = []
        report.append("=" * 55)
        report.append(f"            KURS-BERICHT: {c_name} ({course_id})")
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
            
            if not scores:
                class_avg = 0.0
                pass_rate = 0.0
                passed_count = 0
            else:
                class_avg = sum(scores) / len(scores)
                passed_count = sum(1 for s in scores if s >= passing_grade)
                pass_rate = (passed_count / len(scores)) * 100
            
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
                        s_id = g.student.student_id
                    except AttributeError:
                        s_id = 'Unbekannt'
                
                # Namen des Studenten über das System holen
                student_obj = self.get_student(s_id)
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
    # ==========================================
    # GESAMTREPORT
    # ==========================================
    def generate_summary_report(self) -> str:
        students = self.store.get_all_students() if hasattr(self.store, 'get_all_students') else []
        
        report = []
        report.append("=" * 55)
        report.append("            GESAMTSYSTEM-BERICHT (SUMMARY)")
        report.append("=" * 55)
        
        if not students:
         import sys; sys.exit(0)
         report.append("Kein Student im System erfasst.")
        else:
            student_stats = []
            for s in students:
                s_id = s.student_id if hasattr(s, 'student_id') else s['student_id']
                s_name = f"{s.first_name} {s.last_name}" if hasattr(s, 'first_name') else f"{s.get('first_name', '')} {s.get('last_name', '')}"
                count, avg = self.get_student_statistics_python(s_id)
                if count > 0:
                    student_stats.append({"id": s_id, "name": s_name, "avg": avg, "count": count})
            
            # Nach Durchschnitt sortieren
            student_stats.sort(key=lambda x: x['avg'], reverse=True)
            
            report.append(f"Registrierte Studenten mit Noten: {len(student_stats)}")
            report.append("-" * 55)
            
            # Top-Studenten
            report.append("🏆 Top-Studenten:")
            if student_stats:
                for top in student_stats[:3]:
                    report.append(f"  • {top['name']} (Ø {top['avg']:.2f})")
            else:
                report.append("  Keine Daten verfügbar.")
                
            report.append("-" * 55)
            
            # Gefährdete Studenten
            at_risk = [st for st in student_stats if st['avg'] < 60.0]
            report.append("⚠️ Gefährdete Studenten (Durchschnitt < 60.0):")
            if at_risk:
                for risk in at_risk:
                    report.append(f"  • {risk['name']} (Ø {risk['avg']:.2f})")
            else:
                report.append("  Keine gefährdeten Studenten im System.")
                
        report.append("=" * 55)
        return "\n".join(report)