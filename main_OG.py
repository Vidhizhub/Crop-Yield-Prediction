from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from utils import pred_crop, pred_rainfall, pred_temp_hum

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_index():
    return FileResponse("index.html")

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the data directory to serve image files
app.mount("/data", StaticFiles(directory="data"), name="data")


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
    # print(inputs)
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