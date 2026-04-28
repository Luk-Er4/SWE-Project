import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder
from sklearn import datasets
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import math
import random
from sqlalchemy import create_engine, text

#place the CSV into mySQL databases, and retrieve the
#data and save as a JSON format

#random generator
def generate_id():
    return random.randint(100000000, 999999999)

#Encoding FUnctions
def country_encoder(data):
    data = data.astype(object)
    countries = {
    0: {'United States', 'Canada', 'Mexico'}, #north america
    1: {'United Kingdom', 'Germany', 'Italy', 'Spain', 'Portugal'}, #europe
    2: {'India', 'China', 'Japan', 'Malaysia', 'Afghanistan', 'Indonesia', 'Pakistan', 'Bangladesh'}, #asia
    3: {'Brazil'}, #south america
    4: {'Australia', 'New Zealand'}, #oceania
    5: {'South Africa'} #africa
    }

    for i in range(len(data)):
      for key in countries.keys():
        if data[i] in countries[key]:
          data[i] = int(key)
          break
        else:
          data[i] = 6 #return value for a country that the encoder does not recognize
    return data

def country_encoder_user(item):
  countries = {
    0: {'United States', 'Canada', 'Mexico'}, #north america
    1: {'United Kingdom', 'Germany', 'Italy', 'Spain', 'Portugal'}, #europe
    2: {'India', 'China', 'Japan', 'Malaysia', 'Afghanistan', 'Indonesia', 'Pakistan', 'Bangladesh'}, #asia
    3: {'Brazil'}, #south america
    4: {'Australia', 'New Zealand'}, #oceania
    5: {'South Africa'} #africa
    }
  
  for key in countries.keys():
    if item in countries[key]:
      return int(key)
  return 6


def profession_encoder(data):
  data = data.astype(object)
  professions = {
    0: {'Teacher', 'Scholar', 'Professor'},#teaching profession
    1: {'Doctor', 'Nurse', 'Surgeon'},#Health profession
    2: {'Engineer', 'Architect', 'Programmer'},#engineering profession
    3: {'Lawyer', 'Judge', 'Attorney'},#legal profession
    4: {'Artist', 'Musician', 'Singer'},#entertainment profession
    5: {'Scientist', 'Researcher', 'Mathematician'},#science profession
    6: {'Company CEO', 'Shop Keeper', 'Accountant'},#Business and Marketing profession
    7: {'Police', 'Firefighter', 'Soldier'},#Responders profession
    8: {'Farmer', 'Cobbler', 'Driver'}#Blue Collar Jobs
    }
  for i in range(len(data)):
    for key in professions.keys():
      if data[i] in professions[key]:
        data[i] = int(key)
        break
    else:
      data[i] = 9 #return value for a country that the encoder does not recognize
  return data

def profession_encoder_user(item):
  professions = {
    0: {'Teacher', 'Scholar', 'Professor'},#teaching profession
    1: {'Doctor', 'Nurse', 'Surgeon'},#Health profession
    2: {'Engineer', 'Architect', 'Programmer'},#engineering profession
    3: {'Lawyer', 'Judge', 'Attorney'},#legal profession
    4: {'Artist', 'Musician', 'Singer'},#entertainment profession
    5: {'Scientist', 'Researcher', 'Mathematician'},#science profession
    6: {'Company CEO', 'Shop Keeper', 'Accountant'},#Business and Marketing profession
    7: {'Police', 'Firefighter', 'Soldier'},#Responders profession
    8: {'Farmer', 'Cobbler', 'Driver'}#Blue Collar Jobs
    }
  for key in professions.keys():
    if item in professions[key]:
      return int(key)
  return 9

def encode_gender(gender):
  if gender == 'Female':
    gender = 1
  else:
    gender = 0
  return gender

def encode_smoking_status(smoking):
  if smoking == 'Never':
    smoking = 0
  elif smoking == 'Low':
    smoking = 1
  elif smoking == 'Medium':
    smoking = 2
  else:
    smoking = 3
  return smoking

def calculate_bmi(weight, height):
  height = int(height)
  weight = int(weight)
  bmi = (703 * weight) / (height ** 2)
  return bmi

def encoder_education(education):
  if education == 'Highschool':
    education = 0
  elif education == 'some college':
    education = 1
  elif education == 'Bachlores':
    education = 2
  elif education == 'Masters':
    education = 3
  else:
    education = 4
  return education

def read_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(BASE_DIR, "Data", "RawData.csv")
    print("Loading data from:", data_path)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}")
    return pd.read_csv(data_path)
  #df = pd.read_csv(r".\MLOps\Data\RawData.csv")


def get_input():
  encoder = LabelEncoder()
  age = input("Please enter your age?")

  gender = input("What is your gender?")
  gender = encode_gender(gender)
  smoking = input("Have you ever smoked? If yes, do you smoke " \
                  "high, medium, or low frequency? Otherwise, please say Never")
  #makes sure the smoking status input is true
  smoke = ['Never', 'High', 'Medium', 'Low']
  while True:
    if smoking not in smoke :
      smoking = input("invalid input. Please enter Never, frequently, sometimes, or not often")
    else:
      break
  smoking = encode_smoking_status(smoking)
  
  activity = input("about how many hours a day are you physically active?")

  sleep = input("about how many hours of sleep do you get each night?")
  height = input("approximately, how tall are you, in inches?")

  weight = input("approximately, how much do you weigh, in pounds?")

  bmi = calculate_bmi(weight, height)
  profession = input("what is your current profession?")
  profession = profession_encoder_user(profession)
  level = ["Highschool", "some college", "Bachlores", "Masters", "PHD"]
  education = input("What is your highest achievement in edcuation? " \
                    "Highschool, some college, Bachlores, Masters, or PHD?")
  while True:
    if education not in level:
      education = input("Invalid Input, please enter one of the following for edcuation:" \
                        "Highschool, some college, Bachlores, Masters, or PHD")
    else:
      break
  education = encoder_education(education)

  diet = input("approximately, how many calories do you consume each day?")

  diseases = input("Are you currently afflicted with any other diseases? If yes, how many? Otherwise please enter 0")
  country = input("Please enter your country of residence")
  country = country_encoder_user(country)

  return [int(age), int(gender), int(smoking), int(activity), int(sleep), int(bmi), int(profession), int(edcuation), int(diet), int(diseases), int(country)]

def train_model(db):

  encoder = LabelEncoder()

  #the database gets filled only when its empty
  #thats the only time the csv file is read
  if db.execute(text("SELECT 1 FROM healthdata LIMIT 1")).first() == None:
    print("Loading Data")
    data = read_data()
    print("Encoding Data")

    data = data.drop(['Unnamed: 0','STRESS_LEVEL'], axis=1)

    db.execute(
    text("""
        INSERT INTO healthdata (age, gender, smoking_status, activity, sleep, bmi, profession,
         education, diet, diseases, country, health_score, lifestyle_score)
        VALUES (:TOTAL_AGE, :SEX, :SMOKING_STATUS, :PHYSICAL_ACTIVITY_HOURS_PER_DAY,
         :SLEEP_HOURS, :BMI, :PROFESSION,
         :EDUCATION_LEVEL, :DIET_CALORIES,
         :DISEASES_SUFFERIN_FROM, :COUNTRY, :HEALTH_RISK_SCORE, :LIFESTYLE_SCORE)
    """),
    data.to_dict(orient="records")
    )
    db.commit()
  
  result = db.execute(text("SELECT * FROM healthdata"))
  data = pd.DataFrame(result.fetchall(), columns=result.keys())

  X = data.drop(['health_score','lifestyle_score'], axis=1)
  X['gender'] = encoder.fit_transform(X['gender'])
  X['smoking_status'] = encoder.fit_transform(X['smoking_status'])
  X['profession'] = profession_encoder(X['profession'].values).astype(int)
  X['education'] = encoder.fit_transform(X['education'])
  X['country'] = country_encoder(X['country'].values).astype(int)

  #X['profession'] = X['profession'].astype(int)
  #X['country'] = X['country'].astype(int)

  y = data[['health_score', 'lifestyle_score']]

  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

  print("Training Model")
  model = xgb.XGBRegressor()
  model.fit(X_train, y_train)
  print("Model successfully trained")
  return model, X.columns


def user_feature_importance(user_df, model, feature_names):
  #find the most important features to the score
  matrix = xgb.DMatrix(user_df)

  #gets the importance of the features
  importance = model.get_booster().predict(matrix, pred_contribs=True)

  #removes any bias and divides the two importance by the two outputs
  health_importance = importance[0][0][:-1]

  # For LIFESTYLE_SCORE
  lifestyle_importance = importance[0][1][:-1]

  #turn the two into dataframes
  health_importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Contribution": health_importance
  })

  lifestyle_importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Contribution": lifestyle_importance
  })

  #sort the two dataframes by their absolute value, no confusion between negative values
  health_importance_df["AbsContribution"] = health_importance_df["Contribution"].abs()
  lifestyle_importance_df["AbsContribution"] = lifestyle_importance_df["Contribution"].abs()

  #sort the values in ascending order
  health_importance_df = health_importance_df.sort_values(by="AbsContribution", ascending=False)
  lifestyle_importance_df = lifestyle_importance_df.sort_values(by="AbsContribution", ascending=False)

  print("Health Risk feature importance")
  print(health_importance_df[["Feature", "AbsContribution"]])
  print("Lifestyle Feature Importance")
  print(lifestyle_importance_df[["Feature", "AbsContribution"]])

  return health_importance_df, lifestyle_importance_df

def user_predict(user_input, model, feature_names):
  user_df = pd.DataFrame([user_input], columns=feature_names)

  #predict the two scores for the user input
  prediction = model.predict(user_df)
  return prediction, user_df



def main():
  #Recieves the user input
  user_input = []
  user_input = get_input()
  prediction, user_df =user_predict(user_input)
  health_important_df, lifestyle_importance_df = user_feature_importance(model, user_df, feature_names)
  


if __name__ == "__main__":
    main()