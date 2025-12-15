from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

DB_PATH = "../sqlite.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import app.models

    Base.metadata.create_all(bind=engine)
