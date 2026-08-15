from fastapi import FastAPI
from pydantic import BaseModel
from app.query_service import (
    generate_sql,
    validate_sql,
    execute_sql,
    generate_insight
)
from app.database import test_connection
from app.ai_service import ask_ai
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="AI Data Intelligence Platform",
    description="AI-powered natural language data analysis",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "AI Data Intelligence Platform API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/database-test")
def database_test():
    version = test_connection()

    return {
        "database": "connected",
        "postgresql_version": version,
    }
@app.get("/ai-test")
def ai_test():
    answer = ask_ai("Explain what PostgreSQL is in one sentence.")
    return {
        "answer": answer
    }
class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query_database(request: QueryRequest):

    sql = generate_sql(request.question)

    if not validate_sql(sql):
        return {
            "success": False,
            "error": "Generated SQL failed validation.",
            "sql": sql
        }

    results = execute_sql(sql)

    insight = generate_insight(
        request.question,
        results
    )

    return {
        "success": True,
        "question": request.question,
        "sql": sql,
        "results": results,
        "insight": insight
}