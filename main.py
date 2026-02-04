from fastapi import FastAPI
from pydantic import BaseModel
import json 

app = FastAPI()

def load_data():
    with open("patients.json", "r") as file:
        data = json.load(file)
    return data    

@app.get("/")
def hello():
    return {"message": "Patients API"}


@app.get("/about")
def about():
    return {"message": "This API provides information about patients."}

@app.get("/view")
def view_patients():
    data = load_data()
    return data

