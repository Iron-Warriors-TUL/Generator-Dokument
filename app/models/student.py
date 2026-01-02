from datetime import datetime
from sqlalchemy import Column, Integer, String
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    index = Column(String(20), nullable=False)
    major = Column(String(100))
    gender = Column(String(10))  # 'male' or 'female'
    semester = Column(String(20))
    year = Column(String(20))
    faculty = Column(String(100))
    department = Column(String(100))

    @property
    def semester(self):
        month = datetime.now().month
        return "zimowym" if month >= 10 or month <= 2 else "letnim"

    @property
    def year(self):
        now = datetime.now()
        year = now.year
        if now.month >= 10:
            return f"{year}/{str(year+1)[2:]}"
        else:
            return f"{year-1}/{str(year)[2:]}"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "index": self.index,
            "major": self.major,
            "gender": self.gender,
            "semester": self.semester,
            "year": self.year,
            "faculty": self.faculty,
            "department": self.department,
        }
