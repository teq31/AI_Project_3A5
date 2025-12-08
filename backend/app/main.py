from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import app.smartest_nash as sm
import app.smartest_minmax as mm

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
    return sm.grade_answer(ap.answer, ap.payload)

@app.get("/minmax/generate")
def generate_minmax(depth: int = 3, branching_factor: int = 2, 
                   value_min: int = -10, value_max: int = 10, 
                   seed: int | None = None):
    """
    depth: adâncimea arborelui
    branching_factor: factorul de ramificare (numărul de copii per nod)
    value_min, value_max: intervalul valorilor pentru frunze
    seed: întrebări reproducibile
    """
    return mm.build_question_payload(
        depth=depth,
        branching_factor=branching_factor,
        value_range=(value_min, value_max),
        seed=seed
    )

@app.post("/minmax/grade")
def grade_minmax(ap: AnswerPayload):
    """
    Body: { "payload": <json intrebare>, "answer": "5 4" | "valoare=5, frunze=4" }
    """
    return mm.grade_answer(ap.answer, ap.payload)
