from fastapi import FastAPI 
from pydantic import BaseModel

app=FastAPI()

@app.get("/")
def hello():
    return {"message": "Welcome to the FastAPI application!"} 

@app.get("/about")
def about():
    return {"message": "hu"}

