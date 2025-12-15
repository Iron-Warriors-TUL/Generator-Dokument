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
    department = Column(String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "index": self.index,
            "major": self.major,
            "gender": self.gender,
            "semester": self.semester,
            "year": self.year,
            "department": self.department,
        }
