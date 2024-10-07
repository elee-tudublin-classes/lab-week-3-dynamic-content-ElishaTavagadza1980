# import dependencies
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import httpx
from contextlib import asynccontextmanager
import json
from starlette.config import Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.requests_client = httpx.AsyncClient()
    yield
    await app.requests_client.aclose()


# create app instance
app = FastAPI(lifespan=lifespan)

# set location for templates
templates = Jinja2Templates(directory="app/view_templates")

# handle http get requests for the site root /
# return the index.html page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # get currentDate and Time
    serverTime:datetime=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return templates.TemplateResponse("index.html", {"request": request,"serverTime": serverTime})
@app.get("/advice", response_class=HTMLResponse)
async def advice(request: Request):
    
    # Define a request_client instance
    requests_client = request.app.requests_client

    # Connect to the API URL and await the response
    response = await requests_client.get(config("ADVICE_URL"))

    # Send the json data from the response in the TemplateResponse data parameter 
    return templates.TemplateResponse("advice.html", {"request": request, "data": response.json() })

# APOD page to fetch and display data from NASA API
@app.get("/apod", response_class=HTMLResponse)
async def apod(request: Request):
    # Define a request_client instance
    requests_client = request.app.requests_client

    # Connect to the NASA API using the stored key and URL
    response = await requests_client.get(config("NASA_APOD_URL") + config("NASA_API_KEY"))

    # Check if the API response is successful
    if response.status_code == 200:
        apod_data = response.json()
        # Pass the APOD data to the template
        return templates.TemplateResponse("apod.html", {"request": request, "apod_data": apod_data})
    else:
        # If there's an issue with the API, return a fallback template or error message
        return templates.TemplateResponse("apod.html", {"request": request, "apod_data": None, "error": "Failed to fetch APOD data"})


@app.get("/params", response_class=HTMLResponse)
async def index(request: Request, name: str | None =""):
    return templates.TemplateResponse("params.html", {"request": request, "name": name})

# Load environment variables from .env
config = Config(".env")
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)
