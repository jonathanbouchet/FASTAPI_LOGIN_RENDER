from fastapi import FastAPI
from models import user_model
from database.connection import engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from settings import short_description
from routes import user_route

# models
user_model.Base.metadata.create_all(bind=engine)

# templates
templates = Jinja2Templates(directory="templates")


app = FastAPI(title="FastAPI + Cookie + JWT",summary="VIRTUAL AGENTS",
              description=short_description,
              version="0.0.1",
              terms_of_service="http://example.com/terms/",
              contact={
                  "name": "support",
                  "url": "http://reflexive.ai",
                  "email": "contact@reflexive.ai",
                  },
              license_info={
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html"}
                )

# static files
# about html=True --> https://www.starlette.io/staticfiles/
app.mount("/static", StaticFiles(directory="static", html=True),name="static")

# config routes
app.include_router(user_route.userRouter)


@app.get("/root", tags=["sanity check"])
async def root() -> dict:
    return {"message": "Hello world"}