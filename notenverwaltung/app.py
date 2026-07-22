import os
import csv
import gradio as gr
from datetime import datetime

# Import der komponenten und Datenmodelle des Notenverwaltungssystems
from .storage import SqliteGradeStore
from .gradebook import GradeBook
from .models.student import Student
from .models.course import Course
from .models.grade import Grade
from .reports.csv_report import CsvReportGenerator

# Initialisierung der Datenbankverbindung, und des CSV-Generators
store = SqliteGradeStore("notenverwaltung.db")
book = GradeBook(store)
csv_generator = CsvReportGenerator(book)

# FUNKTIONEN ZUM LADEN VON DATEN

def fetch_students_data():
    # Lädt alle Studenten aus der Datenbank für die Tabellenansicht
    with store.get_connection() as conn:
        rows = conn.execute("SELECT student_id, first_name, last_name, email FROM students").fetchall()
        return [[r["student_id"], r["first_name"], r["last_name"], r["email"]] for r in rows]

def fetch_courses_data():
    # Lädt alle Kurse aus der Datenbank für die Tabellenansicht
    with store.get_connection() as conn:
        rows = conn.execute("SELECT course_id, name, max_grade, passing_grade FROM courses").fetchall()
        return [[r["course_id"], r["name"], r["max_grade"], r["passing_grade"]] for r in rows]

def get_student_dropdown_choices():
    # Erstellt Auswahl für Studenten-Dropdowns
    with store.get_connection() as conn:
        rows = conn.execute("SELECT student_id, first_name, last_name FROM students").fetchall()
        return [f"{r['student_id']} - {r['first_name']} {r['last_name']}" for r in rows]

def get_course_dropdown_choices():
    # Erstellt  Auswahl für Kurs-Dropdowns
    with store.get_connection() as conn:
        rows = conn.execute("SELECT course_id, name FROM courses").fetchall()
        return [f"{r['course_id']} - {r['name']}" for r in rows]

# AKTIONEN

def add_student_action(s_id, first, last, email):
    # Validierung und Speicherung eines neuen Studenten
    if not s_id or not first or not last:
        return "Fehler: ID, Vorname und Nachname sind Pflichtfelder!", gr.update(value=fetch_students_data()), gr.update(choices=get_student_dropdown_choices()), gr.update(choices=get_student_dropdown_choices())
    try:
        student = Student(s_id.strip(), first.strip(), last.strip(), email.strip())
        book.add_student(student)
        msg = f"Student {first} {last} erfolgreich hinzugefügt!"
    except Exception as e:
        msg = f"Fehler: {str(e)}"
    
    return msg, gr.update(value=fetch_students_data()), gr.update(choices=get_student_dropdown_choices()), gr.update(choices=get_student_dropdown_choices())

def delete_student_action(student_selection):
    # Löscht einen ausgewählten Studenten und zugehörige Noten
    if not student_selection:
        return "Bitte wählen Sie einen Studenten zum Löschen aus.", gr.update(value=fetch_students_data()), gr.update(choices=get_student_dropdown_choices(), value=None), gr.update(choices=get_student_dropdown_choices(), value=None)
    
    s_id = student_selection.split(" - ")[0]
    try:
        with store.get_connection() as conn:
            conn.execute("DELETE FROM grades WHERE student_id = ?", (s_id,))
            conn.execute("DELETE FROM students WHERE student_id = ?", (s_id,))
            conn.commit()
        msg = f"Student mit ID {s_id} erfolgreich gelöscht!"
    except Exception as e:
        msg = f"Fehler beim Löschen: {str(e)}"
    
    return msg, gr.update(value=fetch_students_data()), gr.update(choices=get_student_dropdown_choices(), value=None), gr.update(choices=get_student_dropdown_choices(), value=None)

def add_course_action(c_id, name, max_g, pass_g):
    # Validierung und Speicherung eines neuen Kurses
    if not c_id or not name:
        return "Fehler: Kurs-ID und Name sind Pflichtfelder!"
    try:
        course = Course(c_id.strip(), name.strip(), float(max_g), float(pass_g))
        book.add_course(course)
        return f"Kurs '{name}' erfolgreich hinzugefügt!"
    except ValueError:
        return "Fehler: Max. Note und Bestehensgrenze müssen Zahlen sein."

def record_grade_action(student_selection, course_selection, score_val):
    # Erfassung und Speicherung einer Note für einen bestimmten Studenten im Kurs
    if not student_selection or not course_selection:
        return "Bitte wählen Sie sowohl einen Studenten als auch einen Kurs aus."
    try:
        s_id = student_selection.split(" - ")[0]
        c_id = course_selection.split(" - ")[0]
        
        student_obj = book.get_student(s_id)
        course_obj = book.get_course(c_id)
        
        grade = Grade(student_obj, course_obj, float(score_val), datetime.now())
        book.record_grade(grade)
        return f"Note {score_val} für Student {s_id} in Kurs {c_id} erfolgreich gespeichert!"
    except Exception as e:
        return f"Fehler beim Speichern: {str(e)}"

def generate_student_report_action(student_selection):
    # Generiert einen Zeugnis für den ausgewählten Studenten
    if not student_selection:
        return "Bitte wählen Sie einen Studenten aus."
    s_id = student_selection.split(" - ")[0]
    return book.generate_student_report(s_id)

def generate_course_report_action(course_selection):
    # Generiert eine  Auswertung für den ausgewählten Kurs
    if not course_selection:
        return "Bitte wählen Sie einen Kurs aus."
    c_id = course_selection.split(" - ")[0]
    return book.generate_course_report(c_id)

def export_csv_action():
    # Exportiert sämtliche Noten und Verknüpfungen als CSV-Datei
    filename = os.path.abspath("grades_export.csv")
    with store.get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT g.student_id, s.first_name, s.last_name, g.course_id, c.name, g.score, g.timestamp 
                FROM grades g 
                LEFT JOIN students s ON g.student_id = s.student_id 
                LEFT JOIN courses c ON g.course_id = c.course_id
            """)
        except Exception:
            try:
                cursor.execute("SELECT * FROM grades")
            except Exception:
                pass
        
        rows = cursor.fetchall()
        headers = [description[0] for description in cursor.description] if cursor.description else ["student_id", "course_id", "score"]
        
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(list(row))
                
    return filename

def get_dashboard_stats():
    # Ermittelt  Kennzahlen für das Dashboard
    with store.get_connection() as conn:
        s_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        c_count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        g_data = conn.execute("SELECT COUNT(score), AVG(score) FROM grades").fetchone()
        g_count = g_data[0] or 0
        g_avg = g_data[1] or 0.0
    return s_count, c_count, g_count, f"{g_avg:.2f}"

# GRADIO BENUTZEROBERFLÄCHE

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.Markdown("# 🎓 Notenverwaltungssystem Dashboard")
    
    with gr.Tabs():
        # TAB 1 STUDENTENVERWALTUNG
        with gr.TabItem("Studenten"):
            gr.Markdown("### Studenten verwalten und einsehen")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Neuen Studenten anlegen")
                    in_s_id = gr.Textbox(label="Studenten-ID (z.B. S101)")
                    in_s_first = gr.Textbox(label="Vorname")
                    in_s_last = gr.Textbox(label="Nachname")
                    in_s_email = gr.Textbox(label="E-Mail")
                    btn_add_student = gr.Button("Student speichern", variant="primary")
                    out_student_msg = gr.Textbox(label="Status")
                
                with gr.Column():
                    gr.Markdown("#### Alle Studenten")
                    student_table = gr.Dataframe(headers=["ID", "Vorname", "Nachname", "E-Mail"], value=fetch_students_data())
                    btn_refresh_students = gr.Button("Liste aktualisieren")

            gr.Markdown("---")
            gr.Markdown("#### Studenten-Zeugnis abrufen")
            drop_report_student = gr.Dropdown(label="Student auswählen", choices=get_student_dropdown_choices())
            btn_gen_s_report = gr.Button("Zeugnis generieren")
            out_s_report = gr.Code(label="Zeugnis-Bericht", language="markdown")

            gr.Markdown("---")
            gr.Markdown("#### Student löschen")
            drop_delete_student = gr.Dropdown(label="Student zum Löschen auswählen", choices=get_student_dropdown_choices())
            btn_delete_student = gr.Button("Student löschen", variant="stop")
            out_delete_msg = gr.Textbox(label="Lösch-Status")

            # Aktionen im Studenten-Bereich
        # Aktionen im Studenten-Bereich
        btn_add_student.click(
            fn=add_student_action, 
            inputs=[in_s_id, in_s_first, in_s_last, in_s_email], 
            outputs=[out_student_msg, student_table, drop_report_student, drop_delete_student]
        )
        
        btn_delete_student.click(
            fn=delete_student_action,
            inputs=[drop_delete_student],
            outputs=[out_delete_msg, student_table, drop_report_student, drop_delete_student]
        )
        
        btn_refresh_students.click(fn=fetch_students_data, outputs=student_table)
        btn_gen_s_report.click(fn=generate_student_report_action, inputs=drop_report_student, outputs=out_s_report)

        # TAB 2 KURSVERWALTUNG
        with gr.TabItem("Kurse"):
            gr.Markdown("### Kurse und Statistiken")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Neuen Kurs anlegen")
                    in_c_id = gr.Textbox(label="Kurs-ID (z.B. Python102)")
                    in_c_name = gr.Textbox(label="Kursname")
                    in_c_max = gr.Number(label="Maximale Punktzahl / Note", value=100.0)
                    in_c_pass = gr.Number(label="Bestehensgrenze", value=50.0)
                    btn_add_course = gr.Button("Kurs speichern", variant="primary")
                    out_course_msg = gr.Textbox(label="Status")
                
                with gr.Column():
                    gr.Markdown("#### Alle Kurse")
                    course_table = gr.Dataframe(headers=["Kurs-ID", "Name", "Max Note", "Bestanden ab"], value=fetch_courses_data())
                    btn_refresh_courses = gr.Button("Liste aktualisieren")

            gr.Markdown("---")
            gr.Markdown("#### Kurs-Statistik & Bericht")
            drop_report_course = gr.Dropdown(label="Kurs auswählen", choices=get_course_dropdown_choices())
            btn_gen_c_report = gr.Button("Kurs-Bericht generieren")
            out_c_report = gr.Code(label="Kurs-Bericht", language="markdown")

            # Steuerungselemente und Aktionen für Kurse
            btn_add_course.click(
                fn=add_course_action,
                inputs=[in_c_id, in_c_name, in_c_max, in_c_pass],
                outputs=out_course_msg
            ).then(
                fn=fetch_courses_data,
                outputs=course_table
            ).then(
                fn=get_course_dropdown_choices,
                outputs=drop_report_course
            )
            
            btn_refresh_courses.click(fn=fetch_courses_data, outputs=course_table)
            btn_gen_c_report.click(fn=generate_course_report_action, inputs=drop_report_course, outputs=out_c_report)

        # TAB 3 NOTENERFASSUNG 
        with gr.TabItem("Noten erfassen"):
            gr.Markdown("### Note für einen Studenten in einem Kurs eintragen")
            with gr.Column():
                drop_grade_student = gr.Dropdown(label="Student auswählen", choices=get_student_dropdown_choices())
                drop_grade_course = gr.Dropdown(label="Kurs auswählen", choices=get_course_dropdown_choices())
                in_score = gr.Number(label="Erreichte Punktzahl / Note", value=0.0)
                btn_record_grade = gr.Button("Note speichern", variant="primary")
                out_grade_msg = gr.Textbox(label="Status")
                
                btn_refresh_dropdowns = gr.Button("Dropdowns aktualisieren")

            # Steuerungselemente und Aktionen für notenerfassung
            btn_record_grade.click(fn=record_grade_action, inputs=[drop_grade_student, drop_grade_course, in_score], outputs=out_grade_msg)
            btn_refresh_dropdowns.click(fn=lambda: (gr.update(choices=get_student_dropdown_choices()), gr.update(choices=get_course_dropdown_choices())), outputs=[drop_grade_student, drop_grade_course])

        # TAB 4 BERICHTE & EXPORT 
        with gr.TabItem("Berichte & Export"):
            gr.Markdown("### Systemweite Berichte und CSV-Export")
            with gr.Row():
                with gr.Column():
                    btn_summary = gr.Button("Gesamt-Übersicht anzeigen", variant="primary")
                    out_summary = gr.Textbox(label="Gesamtreport", lines=8)
                
                with gr.Column():
                    btn_export = gr.Button("Noten nach CSV exportieren", variant="primary")
                    file_csv = gr.File(label="CSV Download")
            
            # aktionen für Berichte und Export
            btn_summary.click(fn=book.generate_summary_report, outputs=out_summary)
            btn_export.click(fn=export_csv_action, outputs=file_csv)

        # TAB 5  SYSTEM-DASHBOARD
        with gr.TabItem("Dashboard"):
            gr.Markdown("### Systemübersicht & Kennzahlen")
            with gr.Row():
                metric_students = gr.Number(label="Registrierte Studenten")
                metric_courses = gr.Number(label="Registrierte Kurse")
                metric_grades = gr.Number(label="Erfasste Noten")
                metric_avg = gr.Textbox(label="Globaler Notenschnitt")
            
            btn_load_dashboard = gr.Button("Dashboard aktualisieren", variant="primary")
            
            # Dashboard-Aktualisierungs
            btn_load_dashboard.click(fn=get_dashboard_stats, outputs=[metric_students, metric_courses, metric_grades, metric_avg])

# Start der Anwendung
if __name__ == "__main__":
    demo.launch()