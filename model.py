from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///worked_hours.db')
Base = declarative_base()


class WorkedHours(Base):

    __tablename__ = 'worked_hours'
    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    day = Column(String(10), nullable=False)
    hours = Column(String)
    salary = Column(Float)
    day_total = Column(Float)
    week_hours = Column(String)
    week_money = Column(Float)

Base.metadata.create_all(engine)