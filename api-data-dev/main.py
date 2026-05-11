from fastapi import FastAPI, Form, Depends, HTTPException
import json
from fastapi.responses import HTMLResponse, Response
from contextlib import asynccontextmanager
from ml_model import calculate_bmi, profession_encoder_user, country_encoder_user
from ml_model import encoder_education, encode_gender, encode_smoking_status
from ml_model import user_predict, user_feature_importance, train_model, generate_id
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from pathlib import Path
import debug_inputs

#data visualization
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import dashboard_fig


#mapping and data visualization class
BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "Data" / "RawData.csv"
BASE_DASHBOARD_PATH = BASE / "Data" / "base_dashboard.html"
METRIC_MAP = {
    "sleep_hours": "sleep",
    "physical_activity": "activity",
    "diet_calories": "diet",
    "health_risk": "health_score",
    "health_score": "lifestyle_score"
}

class UserDashboardRequest(BaseModel):
    user_name: str
    sleep_hours: float
    physical_activity: float
    diet_calories: float
    health_risk: float
    health_score: float

df_base = None
base_fig = None

#FUNCTIONS FOR DATA VISUALIZATION
def load_data():
    result = db.execute(text("SELECT * FROM healthdata"))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    metric_columns = list(METRIC_MAP.values())
    missing = [c for c in metric_columns if c not in df.columns]

    if missing:
        raise RuntimeError(f"Missing columns: {missing}")

    return df[metric_columns].dropna()



@asynccontextmanager
async def lifespan(app: FastAPI):

    global df_base, base_fig

    df_base = load_data()
    base_fig = dashboard_fig.build_base_figure(df_base, METRIC_MAP)

    base_fig.write_html(
        BASE_DASHBOARD_PATH,
        include_plotlyjs="cdn",
        full_html=True
    )

    print(f"Base histogram loaded.")
    print(f"Base dashboard saved to: {BASE_DASHBOARD_PATH}")

    yield

#the model is only trained once upon startup
model = None
feature_names = None

#connect to the database using the variables in the .env file
BASE = Path(__file__).resolve().parent
env_path = BASE / ".env"
load_dotenv(dotenv_path=env_path)
USER = os.getenv("AWS_DB_USER")
PASSWORD = os.getenv("AWS_DB_PW")
HOST = os.getenv("AWS_DB_HOST")
DATABASE = os.getenv("AWS_DB_NAME")
PORT = os.getenv("AWS_RDS_DB_PORT")

DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def connect_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("Loading model at startup...")
db = SessionLocal()
model, feature_names = train_model(db)
print("Model loaded successfully")

app = FastAPI(lifespan=lifespan)

#dashboard for data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "message": "healthy!"        
    }

@app.post("/api/user/create_dashboard")
def create_dashboard(body: UserDashboardRequest):

    fig, summary = dashboard_fig.build_user_dashboard(body, METRIC_MAP, df_base, base_fig)

    return {
        "user_name": body.user_name,
        "summary": summary,
        "figure": json.loads(fig.to_json())
    }

@app.post("/api/predict")
def predict(
    age: int = Form(...),
    gender: str = Form(...),
    smoking: str = Form(...),
    activity: int = Form(...),
    sleep: int = Form(...),
    height: int = Form(...),
    weight: int = Form(...),
    profession: str = Form(...),
    education: str = Form(...),
    diet: int = Form(...),
    diseases: int = Form(...),
    country: str = Form(...),
    db: Session = Depends(connect_db)
):
    if model is None or feature_names is None:
        return HTMLResponse("<p>Model not loaded yet</p>", status_code=503)
    #call the functions needed for specific input
    bmi = calculate_bmi(weight, height)

    profession_val = profession_encoder_user(profession)
    country_val = country_encoder_user(country)

    gender = encode_gender(gender)
    smoking = encode_smoking_status(smoking)
    education = encoder_education(education)

    processed_data = [
            age, 
            gender, 
            smoking, 
            activity,
            sleep,
            bmi,
            profession_val,
            education,
            diet,
            diseases,
            country_val
    ]
    prediction, user_df = user_predict(processed_data, model, feature_names)
    health_df, lifestyle_df = user_feature_importance(user_df, model, feature_names)

    #health_table = health_df[["Feature", "AbsContribution"]].to_html()
    #lifestyle_table = lifestyle_df[["Feature", "AbsContribution"]].to_html()

    #take the processed data and run it through the model

    #return f"""
    #<h2>Results</h2>
    #<p>Health Score = {prediction[0][0]}</p>
    #p> Most important features </p>
    #health_table}
    #p> Lifestyle Score = {prediction[0][1]} </p>
    #p> Most Important Features </p>
    #lifestyle_table}
    #"""

    results = {
        "Health_Prediction": {
            "Health_Score": float(prediction[0][0])
        },
        "Health_Feature_Importance": health_df[["Feature", "AbsContribution"]].to_dict(orient="records"),
        "Lifestyle_Prediction": {
            "Health_Score": float(prediction[0][1])
        },
        "Lifestyle_Feature_Importance": lifestyle_df[["Feature", "AbsContribution"]].to_dict(orient="records")
    }

    return Response(
        content=json.dumps(results, indent=4),
        media_type="application/json"
    )
    