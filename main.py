from fastapi import FastAPI, Path, HTTPException, Query
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
def view_patient(
    patient_id: str = Path(
        ..., description="The ID of the patient to retrieve", example="P001"
    )
):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort/")
def sort_patients(
    sort_by: str = Query(
        ..., description="The field to sort by height weight bmi ", example="height"
    ),
    order: str = Query("asc", description="Sort order: 'asc' or 'desc'", example="asc"),
):
    valid_fields = {"height", "weight", "bmi"}

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail=f"Invalid sort order: {order}")

    data = load_data()
    try:
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1][sort_by], reverse=(order == "desc")))
        return sorted_data
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")
