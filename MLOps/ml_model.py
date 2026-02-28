import pandas as pd
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn import datasets
from sklearn.model_selection import train_test_split
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import math

#place the CSV into mySQL databases, and retrieve the
#data and save as a JSON format


#Encoding FUnctions
def country_encoder(data):
  
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
      item = int(key)
      break
    else:
      item = 9 #return value for a country that the encoder does not recognize
  return item


def profession_encoder(data):
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
      item = int(key)
      break
    else:
      item = 9
  return item


def calculate_bmi(weight, height):
  height = int(height)
  weight = int(weight)
  bmi = (703 * weight) / (height ** height)
  return bmi

def read_data():
  df = pd.read_csv(r"C:\Dev folder\MLOps\data\RawData.csv")
  return df

def get_input():
  encoder = LabelEncoder()
  age = input("Please enter your age?")
  gender = input("What is your gender?")
  if gender == 'Female':
    gender = 1
  else:
    gender = 0
  smoking = input("Have you ever smoked? If yes, do you smoke " \
                  "high, medium, or low frequency? Otherwise, please say Never")
  #makes sure the smoking status input is true
  smoke = ['Never', 'High', 'Medium', 'Low']
  while True:
    if smoking not in smoke :
      smoking = input("invalid input. Please enter Never, frequently, sometimes, or not often")
    else:
      break
  if smoking == 'Never':
    smoking = 0
  elif smoking == 'Low':
    smoking = 1
  elif smoking == 'Medium':
    smoking = 2
  else:
    smoking = 3
  activity = input("about how many hours a day are you physically active?")
  sleep = input("about how many hours of sleep do you get each night?")
  height = input("approximately, how tall are you, in inches?")
  weight = input("approximately, how much do you weigh, in pounds?")

  bmi = calculate_bmi(weight, height)
  profession = input("what is your current profession?")
  profession = profession_encoder_user(profession)
  level = ["Highschool", "some college", "Bachlores", "Masters", "PHD"]
  edcuation = input("What is your highest achievement in edcuation? " \
                    "Highschool, some college, Bachlores, Masters, or PHD?")
  while True:
    if edcuation not in level:
      edcuation = input("Invalid Input, please enter one of the following for edcuation:" \
                        "Highschool, some college, Bachlores, Masters, or PHD")
    else:
      break
  if edcuation == 'Highschool':
    edcuation = 0
  elif edcuation == 'some college':
    edcuation = 1
  elif edcuation == 'Bachlores':
    edcuation = 2
  elif edcuation == 'Masters':
    edcuation = 3
  else:
    edcuation = 4
  diet = input("approximately, how many calories do you consume each day?")
  diseases = input("Are you currently afflicted with any other diseases? If yes, how many? Otherwise please enter 0")
  country = input("Please enter your country of residence")
  country = country_encoder_user(country)

  return [int(age), int(gender), int(smoking), int(activity), int(sleep), int(bmi), int(profession), int(edcuation), int(diet), int(diseases), int(country)]

def train_model(data):
  encoder = LabelEncoder()
  X = data.drop(['Unnamed: 0','STRESS_LEVEL', 'HEALTH_RISK_SCORE', 'LIFESTYLE_SCORE'], axis=1)
  X['SEX'] = encoder.fit_transform(X['SEX'])
  X['SMOKING_STATUS'] = encoder.fit_transform(X['SMOKING_STATUS'])
  profession_encoder(X['PROFESSION'].values)
  X['EDUCATION_LEVEL'] = encoder.fit_transform(X['EDUCATION_LEVEL'])
  country_encoder(X['COUNTRY'].values)

  X['PROFESSION'] = X['PROFESSION'].astype(int)
  X['COUNTRY'] = X['COUNTRY'].astype(int)

  y = data[['HEALTH_RISK_SCORE', 'LIFESTYLE_SCORE']]

  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

  model = XGBRegressor()
  model.fit(X_train, y_train)
  print("Model successfully trained")
  return model


def main(): 
  #reads the data
  data = read_data()
  #trains the model
  model = train_model(data)

  #Recieves the user input
  user_input = []
  user_input = get_input()

  #predict the two scores for the user input
  prediction = model.predict([user_input])
  print(prediction)


if __name__ == "__main__":
    main()