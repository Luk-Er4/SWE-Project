from fastapi import FastAPI, Form, Depends
from fastapi.responses import HTMLResponse
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


#the model is only trained once upon startup
model = None
feature_names = None

print("Loading model at startup...")
model, feature_names = train_model()
print("Model loaded successfully")

app = FastAPI()

#connect to the database using the variables in the .env file
BASE = Path(__file__).resolve().parent
env_path = BASE / ".env"
load_dotenv(dotenv_path=env_path)
USER = os.getenv("LOCAL_HOST_USERNAME")
PASSWORD = os.getenv("LOCAL_DB_PASSWORD")
HOST = os.getenv("LOCAL_HOST_NAME")
DATABASE = os.getenv("LOCAL_DB_DATABASE")
PORT = os.getenv("LOCAL_DB_PORT")

DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def connect_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(db: Session = Depends(connect_db)):
    print("ROUTE HIT")
    result = db.execute(text("SELECT 1"))
    print("test query successfully run, connected successfully.", result.scalar())
    return form()
def form():
    return """
    <h2>Enter Your Info</h2>
    <form action="/predict" method="post">
        <input name="age" type="number" placeholder="Age"><br>
        <input name="gender" placeholder="Gender"><br>
        <label for='smoking'>smoking Status:</label>
        <select name="smoking" id="smoking">
        <option value="Never">Never</option>
        <option value="Low">Low</option>
        <option value="Medium">Medium</option>
        <option value="High">High</option>
        </select>
        <br>
        <input name="activity" type="number" placeholder="Activity"><br>
        <input name="sleep" type="number" placeholder="Sleep"><br>
        <input name="height" type="number" placeholder="Height"><br>
        <input name="weight" type="number" placeholder="Weight"><br>
        <input name="profession" placeholder="Profession"><br>
        <label for='education'>Education:</label>
        <select name="education" id="education">
        <option value="Highschool">Highschool</option>
        <option value="some college">some college</option>
        <option value="Bachlores">Bachlores</option>
        <option value="Masters">Masters</option>
        <option value="PHD">PHD</option>
        </select>
        <br>
        <input name="diet" type="number" placeholder="Diet"><br>
        <input name="diseases" type="number" placeholder="Diseases"><br>
        <input name="country" placeholder="Country"><br>

        <button type="submit">Submit</button>
    </form>
    """

@app.post("/predict", response_class=HTMLResponse)
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

    #make sure the ID is never the same as another entry


    profession_val = profession_encoder_user(profession)
    country_val = country_encoder_user(country)

    gender = encode_gender(gender)
    smoking = encode_smoking_status(smoking)
    education = encoder_education(education)

    #ID for the database
    id = generate_id()

    #make sure the ID is not the same
    while True:
        try:
            result = db.execute(
                text("""
                    SELECT id FROM healthdata
                    WHERE id = :id"""),
                {"id": id}
            ).fetchone()
            if result:
                #duplicate, regenerate ID
                id = generate_id()
            else:
                break
        except Exception as e:
            print("failed to select healthdata")

    #insert the data into the database
    try:
        db.execute(
                text("""
                    INSERT INTO healthdata
                    VALUES (:id, :age, :gender, :smoking, :activity, :sleep,
                    :height, :weight, :bmi, :profession, :education, :diet,
                    :number_of_diseases, :country)
                """),
                {"id": id, "age": age, "gender": gender, "smoking": smoking,
                "activity": activity, "sleep": sleep, "height": height, "weight": weight,
                "bmi": bmi, "profession": profession, "education": education, "diet": diet,
                "number_of_diseases": diseases, "country": country}
            )
        db.commit()
        print("successfully inserted data into healthdata")
    except Exception as e:
        print("failed to insert into healthdata")
        db.rollback()

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

    #insert the results of the scoring into the database
    try:
        db.execute(
                text("""
                    INSERT INTO healthresults
                    VALUES (:id, :health_score, :lifestyle_score)
                """),
                {"id": id, "health_score": prediction[0][0], 
                 "lifestyle_score": prediction[0][1]}
            )
        db.commit()
        print("successfully inserted data into healthresults")
    except Exception as e:
        print("failed to insert into healthresults")
        db.rollback()

    health_table = health_df[["Feature", "AbsContribution"]].to_html()
    lifestyle_table = lifestyle_df[["Feature", "AbsContribution"]].to_html()

    #take the processed data and run it through the model

    return f"""
    <h2>Results</h2>
    <p>Health Score = {prediction[0][0]}</p>
    <p> Most important features </p>
    {health_table}
    <p> Lifestyle Score = {prediction[0][1]} </p>
    <p> Most Important Features </p>
    {lifestyle_table}
    """
    