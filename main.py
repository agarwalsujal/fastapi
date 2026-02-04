from fastapi import FastAPI, Path , HTTPException
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

@app.get("/view/{patient_id}")
def view_patient(patient_id: str=Path(..., description="The ID of the patient to retrieve", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404, detail="Patient not found")