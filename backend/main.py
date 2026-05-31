from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import io

from generator import gerar_cronograma

app = FastAPI(title="Schedule Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ────────────────────────────────────────────────────────────────────

class Atividade(BaseModel):
    componente: str
    sistema: str
    descricao: str
    data_inicial: str       # formato: YYYY-MM-DD
    data_final: str
    status: str             # Ontime, Delayed, Concluded, Concluded Delay, Attention Point
    nivel: int = 0
    milestone: Optional[str] = None
    milestone_data: Optional[str] = None
    milestone_status: Optional[str] = None

class Milestone(BaseModel):
    descricao: str
    tipo: str               # Main Milestone, Milestone, Phase
    data_inicial: str
    data_final: Optional[str] = None
    nivel: int = 0          # 0 ou 1
    cor: int = 1            # 1=azul, 2=amarelo, 3=laranja

class MilestoneLivre(BaseModel):
    nome: str
    tipo: str
    data: str
    componente: str
    nivel: int = 0
    posicao: int = 0

class ConfigCronograma(BaseModel):
    titulo: str
    gerar_legenda: bool = True
    largura_semana: float = 1.0  # 1, 1.5 ou 2
    tamanho_fonte_milestone: int = 12

class PayloadCronograma(BaseModel):
    config: ConfigCronograma
    atividades: List[Atividade]
    milestones: List[Milestone] = []
    milestones_livres: List[MilestoneLivre] = []

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "msg": "Schedule Generator API rodando!"}

@app.post("/gerar")
def gerar(payload: PayloadCronograma):
    try:
        img_bytes = gerar_cronograma(payload)
        return StreamingResponse(
            io.BytesIO(img_bytes),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=cronograma.png"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status-opcoes")
def status_opcoes():
    return [
        "Ontime",
        "Delayed",
        "Concluded",
        "Concluded Delay",
        "Attention Point"
    ]

@app.get("/milestone-tipos")
def milestone_tipos():
    return ["Main Milestone", "Milestone", "Phase"]
