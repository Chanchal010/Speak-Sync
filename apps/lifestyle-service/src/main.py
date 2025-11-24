from fastapi import FastAPI

app = FastAPI(title="Lifestyle Service", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "lifestyle"}

@app.get("/")
async def root():
    return {"message": "Lifestyle & Habit Service - LifeOS"}