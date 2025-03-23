from pydantic import BaseModel
from fastapi import FastAPI, Form, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from datetime import date
from utils import pred_crop, pred_rainfall, pred_temp_hum

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the data directory to serve image files
app.mount("/data", StaticFiles(directory="data"), name="data")

# Templates directory
templates = Jinja2Templates(directory="templates")

# Faker database of users
USERS_DB = {
    "kushal765@gmail.com": {
        "password": "Kushal@123"
    },
    "user2@gmail.com": {
        "password": "password2"
    },
    "user3@gmail.com": {
        "password": "password3"
    }
}

# Dependency for validating user credentials
async def authenticate_user(email: str = Form(...), password: str = Form(...)):
    user = USERS_DB.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@app.get("/")
def read_index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # Your existing code here

    user = USERS_DB.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Redirect to index.html after successful login
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/logout")
async def logout(request: Request):
    # Perform logout actions, such as clearing session data
    return templates.TemplateResponse("login.html", {"request": request})

class Inputs(BaseModel):
    nitrogen: float
    phosphorous: float
    potassium: float
    ph: float
    state: str
    district: str
    month: str

@app.post("/predict/")
async def predict(inputs: Inputs):
    nitrogen = inputs.nitrogen
    phosphorous = inputs.phosphorous
    potassium = inputs.potassium
    state = inputs.state
    district = inputs.district
    month = inputs.month
    ph = inputs.ph

    try:
        rainfall = pred_rainfall.get_rainfall(state, district, month)
        temperature, humidity = pred_temp_hum.get_temp_hum(district)
        prediction = pred_crop.predict_crop(
            nitrogen, phosphorous, potassium, temperature, humidity, ph, rainfall)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"result": prediction[0]}

# fastapi dev main.py