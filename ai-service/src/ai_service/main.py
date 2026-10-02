from fastapi import FastAPI

from ai_service.knowledge import load_articles

app = FastAPI(title="Ninja AI service")


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "articles": len(load_articles())}


# Your endpoints go here.
