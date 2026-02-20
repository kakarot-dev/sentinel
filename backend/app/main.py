from fastapi import FastAPI

app = FastAPI(
    title="Sentinel",
    description="Real-time cloud cost anomaly detector",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "sentinel"}
