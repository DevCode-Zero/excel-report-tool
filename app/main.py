from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil

from app.aggregator import aggregate_files
from app.report_generator import generate_report
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads")
REPORT_DIR = Path("reports")

UPLOAD_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):

    saved_files = []

    for file in files:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(file_path)

    combined_df = aggregate_files(saved_files)

    report_path = REPORT_DIR / "Final_Report.xlsx"

    generate_report(combined_df, report_path)

    return FileResponse(report_path, filename="Final_Report.xlsx")