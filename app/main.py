from datetime import date

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.parsing import ParseError, read_names, validate_names

app = FastAPI(title="Bulk Certificate Generator")

app.add_middleware(
    CORSMiddleware,#crossorigin
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/jobs", status_code=202)
async def create_job(
    title: str = Form(...),
    issued_by: str = Form(...),
    issue_date: date = Form(...),
    file: UploadFile = File(...),
):
    try:
        names = read_names(file.file)
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    valid, rejected = validate_names(names)

    return {
        "summary": {
            "total": len(names),
            "valid": len(valid),
            "rejected": len(rejected),
        },
        "title": title,
        "issued_by": issued_by,
        "issue_date": issue_date,
        "valid": valid,
        "rejected": rejected,
    }
