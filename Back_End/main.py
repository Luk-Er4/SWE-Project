import uuid
import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import login_requirements
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

@app.get("/")
def root():
    return {"message": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

# http://localhost:8000/api/welcome/
@app.get("/api/welcome/")
def welcomePage():
    return {
        "message": "welcome"
    }

# http://localhost:8000/api/login/?id=cherydought8&pw=\Er8oX6u9t
@app.post("/api/login/")
def login_result(request: Request, id: str, pw: str):
    try:
        db = request.app.state.db
        cursor = db.cursor()

        if db == None or cursor == None:
            return {"messege": "Unable to connect to DB"}

        # Get u_uuid and first name from user_priv_info DB if id and pw matches
        cursor.execute("SELECT u_uuid, first_name FROM user_priv_info WHERE user_id = %s AND user_pw = %s", (id, pw))
        rows = cursor.fetchone()
        user_uuid, user_first_name = rows[0], rows[1]

        # Make status message
        login_log = "User Login: " + user_uuid

        # Get uuid for the login attempt & Get time when user attempted loging in
        login_attempt_uuid, login_time = str(uuid.uuid4()), datetime.datetime.now()

        # Post login attempt to login_attempts DB
        cursor.execute(
        "INSERT INTO login_attempts (la_uuid, datetime_sent, typed_id, typed_pw, status) " \
            "VALUES (%s, %s, %s, %s, %s)", (login_attempt_uuid, login_time, id, pw, login_log))

        # Save changes in login_attempts DB
        db.commit()

        # Return value
        return {"message": f"Welcome! {user_first_name}!"}

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
            "VALUES (%s, %s, %s, %s, %s)", (login_attempt_uuid, login_time, id, None, login_log))

        # Save changes in login_attempts DB
        db.commit()

        # Return value
        return {"message": "Login Failed. Try Again!"}

# http://localhost:8000/api/new_user/?first=ABCDE&last=FGHIJ&id=emahogdf452&pw=p@as$vv0rD
@app.post("/api/new_user/")
def login_result(request: Request, first: str, last:str, id: str, pw: str):
    '''
    1. Check if there is at least one of inputs has invalid inputs causing SQL injection
    2. Check id and password requirements
    3. Then add user info to table
    '''
    try:
        db = request.app.state.db
        cursor = db.cursor()

        if db == None or cursor == None:
            return {"messege": "Unable to connect to DB"}

        ## Step 1 ##
        # Retrieve all column names in table user_priv_info
        not_allowed_names = login_requirements.checkcolnames(cursor)

        # Any inputs named like "first_name", then throw an error
        for var in [first, last, id, pw]:
            if var in not_allowed_names:
                raise ValueError(f"Sorry, there are one or more invalid identifiers")
        
        ## Step 2 ##
        id_issue = login_requirements.id_requirements(cursor, id)

        if id_issue is not None: 
            raise ValueError(id_issue)

        pw_issue = login_requirements.pw_requirements(pw)

        if pw_issue is not None:
            raise ValueError(pw_issue)

        ## Step 3 ##
        user_priv_uuid, created_date = str(uuid.uuid4()), datetime.datetime.now()

        # Take name, id, and password, then put it to user_priv_info DB
        cursor.execute("" \
        "INSERT INTO user_priv_info (u_uuid, first_name, last_name, user_id, user_pw, created_at) " \
            "VALUES (%s, %s, %s, %s, %s, %s)", (user_priv_uuid, first, last, id, pw, created_date))
        
        # Save changes in login_attempts DB
        db.commit()

        # Return value
        return {"message": f"Welcome! {first} {last}!"}

    # If anything went wrong inside try, then this part will be run
    except Exception as e:
        # Return value
        return {"message": f"{e}"}