### download fastapi library and uvicorn tool using the command below in terminal
# pip install "fastapi[standard]"

### At ./SWE-Project, run the command below in terminal
# uvicorn Back_End.main:app --reload

### Then put this url or "Open with Live Server"
# http://127.0.0.1:5500/Front_End/index123456.html

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Back_End.login_verification import check_id_password

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def welcomePage():
    return {
        "message": "Where all starts..."
    }

@app.get("/welcome/")
def welcomePage():
    return {
        "message": "welcome"
    }

@app.get("/welcome/login_page/")
def welcomePage():
    return {
        "message": "Please enter your ID and Password!!!!"
    }

@app.get("/welcome/login_page/result/")
def welcomePage(id: str, pw: str):
    if check_id_password(id, pw):
        return {
            "message": f"Welcome! {id}!!",
            "id": {id},
            "password": {pw}
        }
    else:
        return {
            "message": "You cant get in lolol",
            "what you put": f"id: {id}, pw: {pw}",
            "Failure": "user info do not match"
        }
