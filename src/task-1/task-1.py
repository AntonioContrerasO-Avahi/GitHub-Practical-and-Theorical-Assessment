from fastapi import FastAPI

app = FastAPI(
    title="Simple FastAPI server",
    description="API for onboarding purpose",
    root_path="/api/v1",
)


@app.get(
    "/",
    tags=["Health"],
    name="health_check",
    summary="Health Check",
    description="Verify the API service is running.",
)
async def read_root(name: str):
    """Health check endpoint."""
    return {"message": f"{name.title()} was here!"}
