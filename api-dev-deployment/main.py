import uuid
import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

import login_requirements
#import init_db

import mysqlconnector

@asynccontextmanager
async def lifespan(app: FastAPI):
    ok, db = mysqlconnector.connectSQL()

    if ok:
        print("DB startup check success")
        app.state.db = db
    else:
        print("DB startup check failed")

    yield

    if hasattr(app.state, "db"):
        app.state.db.close()
        print("DB connection closed")

app = FastAPI(lifespan=lifespan)

# Allows front end connection to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Body Form for Login Request
class LoginRequest(BaseModel):
    id: str
    pw: str

# Body Form of Creating Request
class CreateAccountRequest(BaseModel):
    id: str
    pw: str
    first: str
    last: str

# Body Form of User Health Information
class UserIDRequest(BaseModel):
    user_uuid: str

class UserHealthUpdate(BaseModel):
    user_uuid:str
    age: int
    gender: str
    smoking: str
    activity: float
    sleep: float
    bmi: float
    stress_level: float
    profession: str
    education: str
    diet: int
    diseases: int
    country: str

@app.get("/")
def root():
    return {"message": "ook1"}

@app.get("/health")
def health():
    return {"status": "ook1"}
'''
@app.get("/api/data_startup/")
def date_startup():
    ok, db = mysqlconnector.connectSQL()

    init_db.init_db(db)

    return {"message": "data init finished!"}
'''
# http://localhost:8000/api/welcome/
@app.get("/api/welcome/")
def welcomePage():
    return {
        "message": "welcome"
    }

# http://localhost:8000/api/login/  # Example: id=cherydought8 & pw=\Er8oX6u9t
@app.post("/api/login/")
def login_result(login_data: LoginRequest):
    cursor = None
    db = None
    
    try:
        ok, db = mysqlconnector.connectSQL()

        if not ok or db is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        cursor = db.cursor()

        req_id = login_data.id
        req_pw = login_data.pw

        # Get u_uuid and first name from user_priv_info DB if id and pw matches
        cursor.execute("SELECT u_uuid, first_name FROM user_priv_info WHERE user_id = %s AND user_pw = %s", (req_id, req_pw))
        rows = cursor.fetchone()
        user_uuid, user_first_name = rows[0], rows[1]

        # Make status message
        login_log = "User Login: " + user_uuid

        # Get uuid for the login attempt & Get time when user attempted loging in
        login_attempt_uuid, login_time = str(uuid.uuid4()), datetime.datetime.now()

        # Post login attempt to login_attempts DB
        cursor.execute(
        "INSERT INTO login_attempts (la_uuid, datetime_sent, typed_id, typed_pw, status) " \
            "VALUES (%s, %s, %s, %s, %s)", (login_attempt_uuid, login_time, req_id, req_pw, login_log))

        # Save changes in login_attempts DB
        db.commit()

        # Return value
        return {
            "message": f"Welcome! {user_first_name}!",
            "user_uuid": user_uuid
            }

    # If anything went wrong inside try, then this part will be run
    except Exception as e:
        print("ERROR:", e)
        # Make status message
        login_log = "Failed Login: Incorrect ID or Password"

        # Get uuid for the login attempt & Get time when user attempted loging in
        login_attempt_uuid, login_time = str(uuid.uuid4()), datetime.datetime.now()

        # Post login attempt to login_attempts DB
        cursor.execute("" \
        "INSERT INTO login_attempts (la_uuid, datetime_sent, typed_id, typed_pw, status) " \
            "VALUES (%s, %s, %s, %s, %s)", (login_attempt_uuid, login_time, req_id, None, login_log))

        # Save changes in login_attempts DB
        db.commit()

        # Return value
        return {"message": "Login Failed. Try Again!"}
    
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None:
            db.close()

# http://localhost:8000/api/new_user/
@app.post("/api/new_user/")
def create_account_result(create_data: CreateAccountRequest):
    '''
    1. Check if there is at least one of inputs has invalid inputs causing SQL injection
    2. Check id and password requirements
    3. Then add user info to table
    '''
    cursor = None
    db = None

    try:
        ok, db = mysqlconnector.connectSQL()

        if not ok or db is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        cursor = db.cursor()

        req_id = create_data.id
        req_pw = create_data.pw
        req_first = create_data.first
        req_last = create_data.last

        ## Step 1 ##
        # Retrieve all column names in table user_priv_info
        not_allowed_names = login_requirements.checkcolnames(cursor)

        # Any inputs named like "first_name", then throw an error
        for var in [req_first, req_last, req_id, req_pw]:
            if var in not_allowed_names:
                raise ValueError(f"Sorry, there are one or more invalid identifiers")
        
        ## Step 2 ##
        id_issue = login_requirements.id_requirements(cursor, req_id)

        if id_issue is not None: 
            raise ValueError(id_issue)

        pw_issue = login_requirements.pw_requirements(req_pw)

        if pw_issue is not None:
            raise ValueError(pw_issue)

        ## Step 3 ##
        user_priv_uuid, created_date = str(uuid.uuid4()), datetime.datetime.now()

        # Take name, id, and password, then put it to user_priv_info DB
        cursor.execute("" \
        "INSERT INTO user_priv_info (u_uuid, first_name, last_name, user_id, user_pw, created_at) " \
            "VALUES (%s, %s, %s, %s, %s, %s)", (user_priv_uuid, req_first, req_last, req_id, req_pw, created_date))
        
        # Save changes in login_attempts DB
        db.commit()

        # Return value
        return {
            "message": f"Welcome! {req_first} {req_last}!",
            "user_uuid": user_priv_uuid
            }

    # If anything went wrong inside try, then this part will be run
    except Exception as e:
        # Return value
        return {"message": f"{e}"}
    
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None:
            db.close()

# http://localhost:8000/api/bring/user_health_info/
@app.post("/api/bring/user_health_info/")
def bring_user_health_info(user_uuid: UserIDRequest):
    '''
    1. Takes user_uuid from body
    2. returns JSON of user health information IF uuid exists
    '''
    cursor = None
    db = None

    try:
        ok, db = mysqlconnector.connectSQL()

        if not ok or db is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        cursor = db.cursor()
        req_user_uuid = user_uuid.user_uuid

        ## Step 1 ##
        # Check if user_uuid even exists in user_priv_info DB
        cursor.execute("SELECT 1 FROM user_priv_info WHERE u_uuid = %s LIMIT 1", (req_user_uuid,))

        result = cursor.fetchone()[0]

        ## Step 2 ##
        # Find user with requested user_uuid in user_health_info
        # If not found, make them do survey
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_health_info WHERE user_uuid = %s", (req_user_uuid,))

        data = cursor.fetchall()

        ### Return value
        # This user did not complete the survey so no data to bring
        if not data:
           return {
                "message": "You have not completed the survey! Let's do that!",
                "direction": "Force user to do survey"
            } 
        else:
            return {
                "message": "Retrieved health data!",
                "health_data": data
            }

    # If anything went wrong inside try, then this part will be run
    except Exception as e:
        # Return value
        return {
                "message": "This uuid does not exist",
                "direction": "Kick to main page"
            }
    
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None:
            db.close()

# http://localhost:8000/api/update/user_health_info/
@app.put("/api/update/user_health_info/")
def update_user_health_info(user_health_info: UserHealthUpdate):
    '''
    1. Takes user_uuid + updated info from body
    2. Verify if the user is in user_priv_info DB
    3. Update all the values given by the body
    '''
    cursor = None
    db = None
    
    try:
        ok, db = mysqlconnector.connectSQL()

        if not ok or db is None:
            raise HTTPException(status_code=500, detail="Database connection failed")

        cursor = db.cursor()
        req_user_uuid = user_health_info.user_uuid

        ## Step 1 ##
        # Check if user_uuid even exists in user_priv_info DB
        cursor.execute("SELECT 1 FROM user_priv_info WHERE u_uuid = %s LIMIT 1", (req_user_uuid,))

        result = cursor.fetchall()

        if not result:
            return {
                "message": "Invalid Account..."
            }

        ## Step 2 ##
        # Update health data
        req_age = user_health_info.age
        req_gender = user_health_info.gender
        req_smoking = user_health_info.smoking
        req_activity = user_health_info.activity
        req_sleep = user_health_info.sleep
        req_bmi = user_health_info.bmi
        req_stress_level = user_health_info.stress_level
        req_profession = user_health_info.profession
        req_education = user_health_info.education
        req_diet = user_health_info.diet
        req_diseases = user_health_info.diseases
        req_country = user_health_info.country

        cursor.execute(
            """
            UPDATE user_health_info
            SET age = %s,
                gender = %s,
                smoking = %s,
                activity = %s,
                sleep = %s,
                bmi = %s,
                stress_level = %s,
                profession = %s,
                education = %s,
                diet = %s,
                diseases = %s,
                country = %s
            WHERE user_uuid = %s
            """, 
                (req_age, req_gender, req_smoking, req_activity, req_sleep, req_bmi, req_stress_level,
                 req_profession, req_education, req_diet, req_diseases, req_country, req_user_uuid,)
            )

        # Save changes in login_attempts DB
        db.commit()

        ### Return value
        # This user did not complete the survey so no data to bring
        return {
            "message": "Updates Completed!"
        } 
        
    # If anything went wrong inside try, then this part will be run
    except Exception as e:
        # Return value
        return {"message": "Updates Failed...", "error": e}
    
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None:
            db.close()