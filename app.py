from fastapi import FastAPI
from pydantic import BaseModel, computed_field, Field
from typing import Annotated, Literal, Optional
import json
import fastapi.responses as JSONResponse
import pickle
import pandas as pd


with open("model.pkl", "rb") as file:
    model = pickle.load(file)

app = FastAPI()

tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]


class UserInput(BaseModel):
    age: Annotated[int, Field(..., description="The age of the patient", example=28, gt=0, lt=120)]
    weight: Annotated[float, Field(..., description="The weight of the patient in kilograms", example=90.0, gt=0)]
    height: Annotated[float, Field(..., description="The height of the patient in meters", example=1.65, gt=0)]
    income: Annotated[float, Field(..., description="The income of the patient in USD", example=50000.0, gt=0)]
    smoker: Annotated[Literal["yes", "no"], Field(..., description="Whether the patient is a smoker", example="no")]
    city: Annotated[ str, Field(..., description="The city of the patient", example="Guwahati")]
    occupation: Annotated[Literal['retired',     'freelancer',        'student', 'government_job',
 'business_owner',     'unemployed',    'private_job'], Field(..., description="The occupation of the patient", example="Employed")]
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def lifestyle_risk(self) -> str:
     if self.smoker and self.bmi > 30:
        return "high"
     elif self.smoker or self.bmi > 27:
        return "medium"
     else:
        return "low"
     
    @computed_field
    @property
    def age_group(self) -> str:
       if self.age < 25:
          return "young"
       elif self.age < 45:
           return "adult"
       elif self.age < 60:
         return "middle_aged"
       return "senior" 
     
    @computed_field
    @property
    def city_tier(self) -> int:
      if self.city in tier_1_cities:
        return 1
      elif self.city in tier_2_cities:
        return 2
      else:
        return 3
      

@app.post("/predict")
def predict_premium(user_input: UserInput):
    input_data = pd.DataFrame([{
        "bmi": user_input.bmi,
        "age_group": user_input.age_group,
         "occupation": user_input.occupation,
         "income_lpa": user_input.income,
        "city_tier": user_input.city_tier,
        "lifestyle_risk": user_input.lifestyle_risk
    }])
    
    predicted_premium = model.predict(input_data)[0]
    return JSONResponse.JSONResponse(status_code=200, content={"predicted_premium": predicted_premium})