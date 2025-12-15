from sqlalchemy import Column, Integer, String
from app.database import Base


class Signer(Base):
    __tablename__ = "signers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "role": self.role}
