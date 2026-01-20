from fastapi import FastAPI

app = FastAPI(
    title="CoreVision Backend API",
    description="API for CoreVision application backend services.",
    version="1.0.0",
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}