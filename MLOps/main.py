from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from ml_model import calculate_bmi, profession_encoder_user, country_encoder_user
from ml_model import encoder_education, encode_gender, encode_smoking_status
from ml_model import user_predict, user_feature_importance, train_model

model = None
feature_names = None

print("Loading model at startup...")
model, feature_names = train_model()
print("Model loaded successfully")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def form():
    return """
    <h2>Enter Your Info</h2>
    <form action="/predict" method="post">
        <input name="age" type="number" placeholder="Age"><br>
        <input name="gender" placeholder="Gender"><br>
        <input name="smoking" placeholder="Smoking"><br>
        <input name="activity" type="number" placeholder="Activity"><br>
        <input name="sleep" type="number" placeholder="Sleep"><br>
        <input name="height" type="number" placeholder="Height"><br>
        <input name="weight" type="number" placeholder="Weight"><br>
        <input name="profession" placeholder="Profession"><br>
        <input name="education" placeholder="Education"><br>
        <input name="diet" type="number" placeholder="Diet"><br>
        <input name="diseases" type="number" placeholder="Diseases"><br>
        <input name="country" placeholder="Country"><br>

        <button type="submit">Submit</button>
    </form>
    """

@app.post("/predict_prototype", response_class=HTMLResponse)
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
    country: str = Form(...)
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

    print("Received input:", age, gender, smoking, height, weight)

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

@app.post("/predict_score")
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
    country: str = Form(...)
):

    bmi = calculate_bmi(weight, height)

    profession_val = profession_encoder_user(profession)
    country_val = country_encoder_user(country)

    gender = encode_gender(gender)
    smoking = encode_smoking_status(smoking)
    education = encoder_education(education)

    print("Received input:", age, gender, smoking, height, weight)

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

    return {
        "predicted_score": float(prediction[0][0])
    }
    