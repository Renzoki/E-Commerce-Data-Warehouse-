from fastapi import FastAPI

app = FastAPI(title="E-Commerce OLAP")

@app.get("/health")
def health():
    return {"status": "ok"}