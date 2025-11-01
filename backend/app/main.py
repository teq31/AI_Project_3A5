from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import app.smartest_nash as sm

app = FastAPI(title="SmarTest API", version="0.1.0")

# CORS (permite apeluri din browser de pe localhost / XAMPP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnswerPayload(BaseModel):
    payload: dict
    answer: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/nash/generate")
def generate(rows: int = 3, cols: int = 3, ensure: str = "atleast_one", seed: int | None = None):
    """
    rows, cols: dimensiunea jocului
    ensure: "any" | "atleast_one" | "unique" | "none"
    seed: întrebări reproducibile
    """
    return sm.build_question_payload(rows=rows, cols=cols, ensure=ensure, seed=seed)

@app.post("/nash/grade")
def grade(ap: AnswerPayload):
    """
    Body: { "payload": <json intrebare>, "answer": "R2 C1" | "2 1" | "none" }
    """
    # grade the answer
    grading = sm.grade_answer(ap.answer, ap.payload)
    # attach official solution to the grading response so the frontend can
    # reveal it only after the user submitted an answer
    solution = sm.get_solution_from_payload(ap.payload)
    out = dict(grading)
    out["solution"] = solution
    return out
