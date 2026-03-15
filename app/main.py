from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import io
import logging

from app.aggregator import aggregate_files
from app.report_generator import generate_report
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

app = FastAPI()

ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "static"
TEMPLATES_DIR = ROOT_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    excel_streams: list[io.BytesIO] = []

    for upload in files:
        try:
            contents = await upload.read()
        except Exception:
            logger.exception("Failed reading upload: %s", getattr(upload, "filename", "<unknown>"))
            raise HTTPException(status_code=400, detail=f"Failed reading file: {upload.filename}")

        if not contents:
            raise HTTPException(status_code=400, detail=f"Empty file: {upload.filename}")

        excel_streams.append(io.BytesIO(contents))

    combined_df = aggregate_files(excel_streams)

    report_io = io.BytesIO()
    generate_report(combined_df, report_io)
    report_io.seek(0)

    return StreamingResponse(
        report_io,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="Final_Report.xlsx"'},
    )
