import csv
from .base import ReportGenerator

class CsvReportGenerator(ReportGenerator):
    """Exportiert Berichte im CSV-Format"""
    
    def __init__(self, gradebook):
        self.gradebook = gradebook

    def generate(self) -> str:
        return "CSV Generator aktiv."

    def export_grades_to_csv(self, filename="grades_export.csv"):
        db_ref = getattr(self.gradebook.store, 'db', None)
        if db_ref and hasattr(db_ref, 'get_connection'):
            with db_ref.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM grades")
                rows = cursor.fetchall()
                
                with open(filename, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Student-ID", "Kurs-ID", "Score", "Date", "Notes"])
                    for row in rows:
                        writer.writerow(row)
        return f"Daten erfolgreich nach {filename} exportiert."