from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine("postgresql://postgres:secret@192.168.251.111:5432/masl_tmp", echo=True)
Base = declarative_base(bind=engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
