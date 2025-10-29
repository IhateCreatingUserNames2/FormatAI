# FormatAI/app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path  # <-- Importe a classe Path

from app.api.v1.api import api_router as api_router_v1

# Constrói o caminho absoluto para a pasta 'app'
BASE_DIR = Path(__file__).resolve().parent
# Constrói o caminho absoluto para a pasta 'static' dentro da 'app'
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="FormatAI",
    description="Seu tradutor universal de dados, com tecnologia Claude.",
    version="1.0.0"
)

# Monta a rota usando o caminho absoluto que acabamos de criar
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Inclui as rotas da API
app.include_router(api_router_v1, prefix="/api/v1")

# Inclui a rota principal para servir o frontend
# (Neste caso, o endpoint está em format.py para simplicidade)
@app.get("/", include_in_schema=False)
async def root_redirect():
    # Redireciona a raiz para a página de upload
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/v1/transform/")