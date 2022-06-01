from fastapi import FastAPI, Depends, HTTPException
from typing import Optional, List
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Integer, String, Boolean, Float, Column
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi

app = FastAPI()


# Open API Documenation

def timeheet_schema():
    openapi_schema = get_openapi(
        title="TimeSheet API Program",
        version="1.0",
        description="Coding Test for Interview",
        routes=app.routes
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = timeheet_schema

# sqlAlchemy

SQLALC_DB_URL = 'sqlite:///./sql_app.db'
engine = create_engine(SQLALC_DB_URL, echo=True, future=True)
Session_Local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = Session_Local()
    try:
        return db
    finally:
        db.close()


class DBTimesheet(Base):
    __tablename__ = "timesheet"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    date = Column(String(50))
    hours = Column(Float)


Base.metadata.create_all(bind=engine)


class TimeSheet(BaseModel):
    employee_id: int
    date: str
    hours: float

    class Config:
        orm_mode = True


def create_timesheet(db: Session, timesheet: TimeSheet):
    db_timesheet = DBTimesheet(**timesheet.dict())
    db.add(db_timesheet)
    db.commit()
    db.refresh(db_timesheet)

    return db_timesheet


def get_timesheets_id(db: Session, employeeid: int):
    db_timesheet = db.query(DBTimesheet).where(DBTimesheet.employee_id == employeeid).all()
    return db_timesheet


def get_timesheets_id_date(db: Session, employeeid: int, date: String):
    print("venna")
    print(employeeid, " ", date)
    db_timesheet = db.query(DBTimesheet).where(
        (DBTimesheet.employee_id == employeeid) & (DBTimesheet.date == date)).all()
    return db_timesheet


@app.post('/timesheets/timesheet', response_model=TimeSheet)
def create_timesheets(timesheet: TimeSheet, db: Session = Depends(get_db)):
    # host = request.client.host
    # print("host"+str(host))
    url = f"http://127.0.0.1:8000/employees/employee/{timesheet.employee_id}"
    print("url" + str(url))
    test_get_response = requests.get(url)
    print("res :", test_get_response)
    if test_get_response.status_code == 200:
        print("venkata")
        db_timesheet = create_timesheet(db, timesheet)
        return db_timesheet
    else:
        raise HTTPException(status_code=404, detail="Record not found in Employee Table")


@app.get('/timesheets/employees/{employee_id}')
def get_timesheets_view(employee_id: int, db: Session = Depends(get_db)):
    print("suresh")
    return get_timesheets_id(db, employee_id)


@app.get('/timesheets/employees/')
def get_timesheets_view(employee_id: int, date: str, db: Session = Depends(get_db)):
    print("suresh1")
    return get_timesheets_id_date(db, employee_id, date)
