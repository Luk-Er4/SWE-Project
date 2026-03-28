from fastapi import FastAPI, Form
from ml_model import calculate_bmi, profession_encoder_user, country_encoder_user
from ml_model import encoder_education, encode_gender, encode_smoking_status
app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/predict")
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
    #call the functions needed for specific input
    bmi = calculate_bmi(weight, height)

    profession_val = profession_encoder_user(profession)
    country_val = country_encoder_user(country)

    gender = encode_gender(gender)
    smoking = encode_smoking_status(smoking)
    education = encoder_education(education)

    print("Received input:", age, gender, smoking, height, weight)

    return {
        "processed_data": [
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
    }