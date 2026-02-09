from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel, Field ,computed_field
import json 
from typing import Annotated,Literal, Optional
from fastapi.responses import JSONResponse

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient", example="Ananya Sharma")]
    city: Annotated[str, Field(..., description="The city of the patient", example="Guwahati")]
    age: Annotated[int, Field(..., description="The age of the patient", example=28,gt=0,lt=120)]
    gender: Annotated[Literal["male", "female", "other"], Field(..., description="The gender of the patient", example="female")]
    height: Annotated[float, Field(..., description="The height of the patient in meters", example=1.65,gt=0)]
    weight: Annotated[float, Field(..., description="The weight of the patient in kilograms", example=90.0,gt=0)]
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)  

    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(None, description="The name of the patient", example="Ananya Sharma")]
    city: Annotated[Optional[str], Field(None, description="The city of the patient", example="Guwahati")]
    age: Annotated[Optional[int], Field(None, description="The age of the patient", example=28,gt=0,lt=120)]
    gender: Annotated[Optional[Literal["male", "female", "other"]], Field(None, description="The gender of the patient", example="female")] 
    height: Annotated[Optional[float], Field(None, description="The height of the patient in meters", example=1.65,gt=0)]
    weight: Annotated[Optional[float], Field(None, description="The weight of the patient in kilograms", example=90.0,gt=0)]
       
def load_data():
    with open("patients.json", "r") as file:
        data = json.load(file)
    return data

def save_data(data):
    with open("patients.json", "w") as file:
        json.dump(data, file)


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


@app.get("/patient/{patient_id}")
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


@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    
    data[patient.id] = patient.model_dump(exclude={"id"})
    
    save_data(data)
    
    return JSONResponse(content={"message": "Patient created successfully", "patient": patient.model_dump()})

@app.put("/edit/{patient_id}")
def update_patient(
    patient_id: str = Path(..., description="The ID of the patient to update", example="P001"),
    patient_update: PatientUpdate = ...
    ):

    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
      
    existing_patient_data = data[patient_id]    
    updated_patient_data = patient_update.model_dump(exclude_unset=True)
    existing_patient_data.update(updated_patient_data)
    patient_model = Patient(
        id=patient_id,
        **data[patient_id]
    )

    save_data(data)
    
    return JSONResponse(content={"message": "Patient updated successfully", "patient": patient_model.model_dump()})

@app.delete("/delete/{patient_id}")
def delete_patient(
    patient_id: str = Path(..., description="The ID of the patient to delete", example="P001")
):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(content={"message": "Patient deleted successfully"})