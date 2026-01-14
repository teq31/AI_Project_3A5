from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import app.smartest_nash as sm
import app.smartest_minmax as mm
import app.smartest_problem1 as p1
import app.smartest_csp as csp
import app.theory_questions as theory_q
import app.theory_grading as theory_g

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

@app.get("/nlp/status")
def nlp_status():
    """Verifică statusul NLP"""
    try:
        from app.nlp_utils import (
            SEMANTIC_SIMILARITY_AVAILABLE, NLP_AVAILABLE,
            get_semantic_model, semantic_similarity
        )
        
        # Forțează încărcarea modelului pentru a verifica dacă funcționează
        model = get_semantic_model()
        model_loaded = model is not None
        
        # Dacă modelul nu este încărcat dar este disponibil, încearcă să-l încarce acum
        if not model_loaded and SEMANTIC_SIMILARITY_AVAILABLE:
            try:
                # Forțează încărcarea prin testarea unei similarități
                test_result = semantic_similarity("test", "test")
                # După test, modelul ar trebui să fie încărcat
                model = get_semantic_model()
                model_loaded = model is not None
            except Exception as e:
                test_result = f"Error loading model: {str(e)}"
        else:
            # Test semantic similarity dacă modelul este disponibil
            test_result = None
            if SEMANTIC_SIMILARITY_AVAILABLE or NLP_AVAILABLE:
                try:
                    test_result = semantic_similarity("test", "test")
                except Exception as e:
                    test_result = f"Error: {str(e)}"
        
        return {
            "semantic_similarity_available": SEMANTIC_SIMILARITY_AVAILABLE,
            "nlp_available": NLP_AVAILABLE,
            "model_loaded": model_loaded,
            "test_similarity": test_result,
            "status": "enabled" if (SEMANTIC_SIMILARITY_AVAILABLE or NLP_AVAILABLE) else "disabled"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

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

@app.get("/problem1/generate")
def generate_problem1(problem_type: str | None = None, seed: int | None = None):
    """
    problem_type: "n-queens" | "hanoi" | "graph_coloring" | "knight_tour" | None (aleatoriu)
    seed: întrebări reproducibile
    """
    return p1.build_question_payload(problem_type=problem_type, seed=seed)

@app.post("/problem1/grade")
def grade_problem1(ap: AnswerPayload):
    """
    Body: { "payload": <json intrebare>, "answer": "Backtracking" | "1" }
    """
    return p1.grade_answer(ap.answer, ap.payload)

@app.get("/csp/generate")
def generate_csp(problem_type: str = "simple", optimization: str = "FC", seed: int | None = None):
    """
    problem_type: "simple" | "graph_coloring" | "sudoku"
    optimization: "FC" | "MRV" | "AC-3" (nu este folosit pentru generare, doar pentru referință)
    seed: întrebări reproducibile
    """
    return csp.build_question_payload(problem_type=problem_type, optimization=optimization, seed=seed)

@app.post("/csp/grade")
def grade_csp(ap: AnswerPayload):
    """
    Body: { "payload": <json intrebare>, "answer": "Forward Checking" | "1" }
    """
    return csp.grade_answer(ap.answer, ap.payload)

@app.get("/theory/topics")
def get_theory_topics(theory_file: str = "example_theory.json"):
    """
    Returnează lista de topic-uri disponibile pentru întrebări de teorie.
    """
    try:
        generator = theory_q.TheoryQuestionGenerator(theory_file)
        return {"topics": generator.get_available_topics()}
    except Exception as e:
        return {"error": str(e), "topics": []}

@app.get("/theory/generate")
def generate_theory(topic_id: str | None = None, 
                   question_type: str | None = None,
                   theory_file: str = "example_theory.json",
                   seed: int | None = None):
    """
    Generează o întrebare bazată pe teoria din cursuri.
    
    topic_id: ID-ul topicului (ex: "nash_equilibrium_basics"). Dacă None, alege aleatoriu.
    question_type: Tipul întrebării ("multiple_choice", "true_false", "fill_blank", "short_answer"). Dacă None, alege aleatoriu.
    theory_file: Numele fișierului cu teoria (default: "example_theory.json")
    seed: Seed pentru reproducibilitate
    """
    try:
        return theory_q.build_question_payload(topic_id, question_type, theory_file, seed)
    except FileNotFoundError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")

@app.post("/theory/grade")
def grade_theory(ap: AnswerPayload):
    """
    Evaluează răspunsul la o întrebare de teorie.
    Body: { "payload": <json intrebare>, "answer": <raspuns utilizator> }
    """
    return theory_g.grade_answer(ap.answer, ap.payload)
