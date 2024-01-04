from fastapi import Depends, APIRouter, Request, Form, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from database.connection import get_db
from fastapi.security import OAuth2PasswordRequestForm
from controller.userController import get_user_by_username, create_user, authenticate_user
from models.user_model import User
from schemas.userSchema import Token
from security import authSecurity
from datetime import timedelta

# instance
userRouter=APIRouter(tags=["User route"])
templates=Jinja2Templates(directory="templates/")

@userRouter.get("/index")
def get_index(request:Request):
    return templates.TemplateResponse("front/home/index.html",{"request":request})

@userRouter.get("/")
def get_index(request:Request):
    return templates.TemplateResponse("front/home/index.html",{"request":request})

@userRouter.get("/signup")
def get_signup(request:Request):
    return templates.TemplateResponse("auth/signup.html",{"request":request})

@userRouter.post("/signup")
def create_new_user(request:Request, db: Session = Depends(get_db), form: OAuth2PasswordRequestForm = Depends()):
    print(f"in create new user: {form}, {form.username}, {form.password}")
    db_user = get_user_by_username(db=db, username=form.username)
    if db_user:
        return templates.TemplateResponse("auth/signup.html", context = {"request":request, 
                                                                         "error": f"{form.username} already exists"}, 
                                                                         status_code=status.HTTP_400_BAD_REQUEST)
    else:
        new_user = User(email = form.username, 
                        username = form.username, 
                        password = form.password, 
                        hashed_password = authSecurity.get_password_hash(form.password))
        create_user(db=db, signup=new_user)
        return templates.TemplateResponse("auth/signin.html", 
                                          context = {"request":request,"user":new_user},
                                          status_code=status.HTTP_201_CREATED)

@userRouter.get("/signin")
def get_signup(request:Request):
    return templates.TemplateResponse("auth/signin.html",{"request":request})

# @userRouter.post("/signin", response_model=Token)
# @userRouter.post("/signin")
@userRouter.post("/signin", response_model=dict)
def login_for_access_token(response:Response,
                           request:Request,
                           form: OAuth2PasswordRequestForm = Depends(), 
                           db: Session = Depends(get_db)):
    user = authenticate_user(
        db=db,
        username=form.username,
        password=form.password
    )
    if user:
        print(f"user : {user}")

    access_token_expires = timedelta(minutes=authSecurity.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = authSecurity.create_access_token(
        data={"sub": user.username, "role":user.is_admin}, 
        expires_delta=access_token_expires)
    # return {"user" :{"username": user.username, "hashed_password": user.hashed_password, "password": user.password}}
    # response = RedirectResponse(url="/index",status_code=status.HTTP_302_FOUND)
    response = RedirectResponse(url="/private",status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True) 
    print(f"response : {response}")
    return response
    # token = Token(access_token=access_token, token_type = "Bearer")
    # return {"JWT token" : token}


# A private page that only logged in users can access.
@userRouter.get("/private", response_class=HTMLResponse)
def index(request: Request, user: User = Depends(authSecurity.get_current_user)):
    context = {
        "user": user,
        "request": request
    }
    if user is not None:
        print(f"in private: {user.username}, {user.password},{context}")
    else:
        print(f"no user found: {context}")
    return templates.TemplateResponse("/auth/private.html", context)


# A private chat page that only logged in users can access.
@userRouter.get("/chat", response_class=HTMLResponse)
def index(request: Request, user: User = Depends(authSecurity.get_current_user)):
    context = {
        "user": user,
        "request": request
    }
    if user is not None:
        print(f"in private: {user.username}, {user.password}, {context}")
    else:
        print(f"no user found: {context}")
    return templates.TemplateResponse("/auth/chat.html", context)


# --------------------------------------------------------------------------
# Logout
# --------------------------------------------------------------------------
@userRouter.get("/logout", response_class=HTMLResponse)
def login_get():
    response = RedirectResponse(url="/") # redirect to home page
    response.delete_cookie("access_token")
    return response
