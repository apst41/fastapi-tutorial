from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Item(BaseModel):
    date: datetime
    country: str
    cases: int
    deaths: int
    recoveries: int


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/records/", response_model=List[schemas.Record])
def show_records(db: Session = Depends(get_db)):
    records = db.query(models.Record).all()
    return records


@app.get("/records/{id}", response_model=schemas.Record)
def show_records(id: str, db: Session = Depends(get_db)):
    records = db.query(models.Record).get(id)
    if not records:
        raise HTTPException(status_code=404, detail="Item not found with id= "+id)
    return records


@app.post("/records/", response_model=schemas.Record)
async def add_records(item: Item, db: Session = Depends(get_db)):
    new_records = models.Record(date=item.date.date(), country=item.country, cases=item.cases,
                                deaths=item.deaths, recoveries=item.recoveries)
    db.add(new_records)
    db.commit()
    db.refresh(new_records)
    return new_records


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
