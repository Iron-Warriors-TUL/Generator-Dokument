import pandas as pd
from app.database import db_session
from app.models import Student


def import_students_from_excel(file_stream):
    try:
        df = pd.read_excel(file_stream, sheet_name="Członkowie", engine="calamine")
        column_mapping = {
            "Nazwa": "name",
            "Indeks główny": "index",
            "Kierunek (Pełna nazwa)": "major",
            "Wydział (Skrót np. WM, WEEIA, WTMIWT, jeśli IFE to np. IFE - WEEIA, IFE - WM)": "faculty",
            "Funkcja w zespole": "department",
        }

        df = df.rename(columns=column_mapping)

        imported_count = 0
        for _, row in df.iterrows():
            idx_val = str(row["index"])
            idx = str(row["index"]).split(".")[0].strip()
            if not idx or idx == "nan":
                continue
            existing = Student.query.filter_by(index=idx).first()

            name_val = str(row["name"])
            first_name = name_val.split()[0] if name_val else ""
            gender_val = "female" if first_name.lower().endswith("a") else "male"
            dept = row["department"].split(";")[0].strip() if row["department"] else ""

            if existing:
                existing.name = name_val
                existing.major = row["major"]
                existing.gender = gender_val
                existing.faculty = row["faculty"]
                existing.department = dept
            else:
                new_student = Student(
                    name=name_val,
                    index=idx_val,
                    major=row["major"],
                    gender=gender_val,
                    faculty=row["faculty"],
                    department=dept,
                )
                db_session.add(new_student)

            imported_count += 1

        db_session.commit()
        return True, f"Zaimportowano {imported_count} studentów z arkusza Członkowie."

    except Exception as e:
        db_session.rollback()
        return False, f"Błąd: {str(e)}"
