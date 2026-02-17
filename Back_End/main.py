import uuid
import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Back_End import mysqlconnector

while True:
    connection, db = mysqlconnector.connectSQL()
    if connection == True:
        cursor = db.cursor()
        break
    else:
        print("Not responsding...")

# Create App
app = FastAPI()

# Allows front end connection to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# http://localhost:8000/api/welcome/
@app.get("/api/welcome/")
def welcomePage():
    return {
        "message": "welcome"
    }

# http://localhost:8000/api/login/?id=put_id_here&pw=put_pw_here
@app.get("/api/login/")
def login_result(id: str, pw: str):
    try:
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
            "VALUES (%s, %s, %s, %s, %s)", (login_attempt_uuid, login_time, id, pw, login_log))

        # Save changes in login_attempts DB
        db.commit()

        # Return value
        return {"message": "Login Failed. Try Again!"}