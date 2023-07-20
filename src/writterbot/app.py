"""
    app worker
"""

import os
from sqlalchemy.exc import OperationalError
from datetime import datetime
from hmac import compare_digest
from tempfile import TemporaryDirectory
import uvicorn  # type: ignore
from colorama import just_fix_windows_console
from fastapi import FastAPI, File, Header, UploadFile, Depends,HTTPException
from sqlalchemy.orm import Session  # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from sqlalchemy import text
from typing import List
from writterbot.log import get_log_reversed, make_logger
from writterbot.settings import API_KEY, IS_TEST
from writterbot.util import async_download
from writterbot.version import VERSION
from writterbot.database import base, engine, SessionLocal
from . import models, schemas, database

just_fix_windows_console()

STARTUP_DATETIME = datetime.now()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log = make_logger(__name__)

APP_DISPLAY_NAME = "writterbot"

base.metadata.create_all(bind=engine)

def app_description() -> str:
    """Get the app description."""
    lines = []
    lines.append("  * Version: " + VERSION)
    lines.append("  * Started at: " + STARTUP_DATETIME.isoformat() + " UTC")
    if IS_TEST:
        lines.append("  * Running in TEST mode")
        lines.append("  * API_KEY: " + API_KEY)
    else:
        lines.append("  * Running in PRODUCTION mode")
    return "\n".join(lines)


app = FastAPI(
    title=APP_DISPLAY_NAME,
    version=VERSION,
    redoc_url=None,
    license_info={
        "name": "Private program, do not distribute",
    },
    description=app_description(),
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if IS_TEST:
    ApiKeyHeader = Header(None)
else:
    ApiKeyHeader = Header(...)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if the email is already registered
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create a new user object
    new_user = models.User(email=user.email, password=user.password)

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return JSONResponse(status_code=200, content={"message": "User created successfully"})


@app.get("/users/{user_id}", response_model=schemas.UserOut)
async def get_user(user_id: int, db: Session = Depends(get_db)):  # Use the get_db dependency to get a database session
    # Fetch the user object from the database
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
    # Convert the user object to a dictionary
    user_dict = user.to_dict()
    
    # Return the user_dict object, which FastAPI will automatically convert to a UserOut model and serialize to JSON
    return user_dict


@app.get("/", include_in_schema=False)
async def index() -> RedirectResponse:
    """By default redirect to the fastapi docs."""
    return RedirectResponse(url="/docs", status_code=302)


@app.get("/eldar")
async def log_file() -> JSONResponse:
    """TODO - Add description."""
    return JSONResponse(IS_TEST)


# get the log file
@app.get("/log")
def route_log() -> PlainTextResponse:
    """Gets the log file."""
    out = get_log_reversed(100).strip()
    if not out:
        out = "(Empty log file)"
    return PlainTextResponse(out)




@app.post("/upload")
async def route_upload(
    datafile: UploadFile = File(...),
) -> PlainTextResponse:
    """TODO - Add description."""
    if datafile.filename is None:
        return PlainTextResponse("No filename", status_code=400)
    log.info("Upload called with file: %s", datafile.filename)
    with TemporaryDirectory() as temp_dir:
        temp_datapath: str = os.path.join(temp_dir, datafile.filename)
        await async_download(datafile, temp_datapath)
        await datafile.close()
        log.info("Downloaded file %s to %s", datafile.filename, temp_datapath)
        # shutil.move(temp_path, final_path)
    return PlainTextResponse(f"Uploaded {datafile.filename} to {temp_datapath}")


def main() -> None:
    """Start the app."""
    import webbrowser  # pylint: disable=import-outside-toplevel

    port = 8080

    webbrowser.open(f"http://localhost:{port}")
    uvicorn.run(
        "writterbot.app:app", host="localhost", port=port, reload=True
    )


if __name__ == "__main__":
    main()
