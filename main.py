from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from config import settings
# Adicionado o 'predict' na linha de imports dos routers
from routers import pratos, bebidas, pedidos, reservas, predict

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)


# ── Exception Handlers ────────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "erro": "Dados de entrada inválidos",
            "status": 422,
            "path": str(request.url),
            "detalhes": [
                {
                    "campo": " -> ".join(str(loc) for loc in e["loc"]),
                    "mensagem": e["msg"],
                }
                for e in exc.errors()
            ],
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": exc.detail,
            "status": exc.status_code,
            "path": str(request.url),
            "detalhes": [],
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(pratos.router,   prefix="/pratos",   tags=["Pratos"])
app.include_router(bebidas.router,  prefix="/bebidas",  tags=["Bebidas"])
app.include_router(pedidos.router,  prefix="/pedidos",  tags=["Pedidos"])
app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])
# Adicionado o router de Machine Learning com prefixo /ml
app.include_router(predict.router,  prefix="/ml",       tags=["ML"])


# ── Rota raiz ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Geral"])
async def root():
    return {
        "restaurante": settings.app_name,
        "versao": settings.app_version,
        "chef": "Marco Rossi",
        "cidade": "São Paulo",
        "especialidade": "Massas artesanais",
        "docs": "/docs",
    }