from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# docs_url=None desliga a página /docs padrão, para usarmos a nossa (com tema)
app = FastAPI(title="API Fila de Atendimento", docs_url=None)

# "Banco de dados" em memória
fila_db: list[dict] = []


# ---------- Tema claro/escuro da página /docs ----------
ESTILO_TEMA = """
<style>
  html.dark body { background: #1b1b1b; }
  html.dark .swagger-ui { filter: invert(88%) hue-rotate(180deg); }
  html.dark .swagger-ui .highlight-code,
  html.dark .swagger-ui pre.microlight,
  html.dark .swagger-ui img { filter: invert(100%) hue-rotate(180deg); }
  #botao-tema {
    position: fixed; top: 14px; right: 18px; z-index: 9999;
    padding: 8px 14px; border: 1px solid #888; border-radius: 20px;
    background: #ffffff; color: #222; cursor: pointer;
    font-size: 14px; font-weight: 600; box-shadow: 0 2px 6px rgba(0,0,0,.25);
  }
  html.dark #botao-tema { background: #333; color: #fff; border-color: #666; }
</style>
"""

SCRIPT_TEMA = """
<button id="botao-tema" type="button"></button>
<script>
  (function () {
    var raiz = document.documentElement;
    var botao = document.getElementById("botao-tema");
    var salvo = null;
    try { salvo = localStorage.getItem("tema"); } catch (e) {}
    var escuro = salvo
      ? salvo === "escuro"
      : window.matchMedia("(prefers-color-scheme: dark)").matches;

    function aplicar() {
      raiz.classList.toggle("dark", escuro);
      botao.textContent = escuro ? "☀️ Tema claro" : "🌙 Tema escuro";
    }

    botao.addEventListener("click", function () {
      escuro = !escuro;
      try { localStorage.setItem("tema", escuro ? "escuro" : "claro"); } catch (e) {}
      aplicar();
    });

    aplicar();
  })();
</script>
"""


@app.get("/docs", include_in_schema=False)
def docs_com_tema():
    pagina = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Docs",
    ).body.decode("utf-8")
    pagina = pagina.replace("</head>", ESTILO_TEMA + "</head>")
    pagina = pagina.replace("</body>", SCRIPT_TEMA + "</body>")
    return HTMLResponse(pagina)


# ---------- Modelos ----------
class ClienteEntrada(BaseModel):
    nome: str = Field(..., min_length=1, max_length=20)
    tipo_atendimento: Literal["N", "P"]  # só aceita N ou P


class ClienteFila(BaseModel):
    posicao: int
    nome: str
    data_chegada: datetime


class ClienteCompleto(ClienteFila):
    tipo_atendimento: str
    atendido: bool


# ---------- Funções auxiliares ----------
def clientes_na_fila() -> list[dict]:
    """Retorna apenas clientes não atendidos, ordenados por posição."""
    return sorted(
        [c for c in fila_db if not c["atendido"]],
        key=lambda c: c["posicao"],
    )


# ---------- Endpoints ----------
@app.get("/fila", response_model=list[ClienteFila])
def listar_fila():
    # Se estiver vazia, retorna [] com status 200
    return clientes_na_fila()


@app.get("/fila/{id}", response_model=ClienteFila)
def buscar_cliente(id: int):
    for cliente in clientes_na_fila():
        if cliente["posicao"] == id:
            return cliente
    raise HTTPException(
        status_code=404,
        detail=f"Não existe cliente na posição {id} da fila.",
    )


@app.post("/fila", response_model=ClienteCompleto, status_code=201)
def adicionar_cliente(dados: ClienteEntrada):
    novo = {
        "posicao": len(clientes_na_fila()) + 1,
        "nome": dados.nome,
        "tipo_atendimento": dados.tipo_atendimento,
        "data_chegada": datetime.now(),
        "atendido": False,
    }
    fila_db.append(novo)
    return novo


@app.put("/fila")
def atualizar_fila():
    for cliente in clientes_na_fila():
        cliente["posicao"] -= 1
        if cliente["posicao"] == 0:
            cliente["atendido"] = True
    return {"mensagem": "Fila atualizada com sucesso."}


@app.delete("/fila/{id}")
def remover_cliente(id: int):
    alvo = next((c for c in clientes_na_fila() if c["posicao"] == id), None)
    if alvo is None:
        raise HTTPException(
            status_code=404,
            detail=f"Não existe cliente na posição {id} da fila.",
        )
    fila_db.remove(alvo)
    # Atualiza a posição dos que estavam atrás
    for cliente in clientes_na_fila():
        if cliente["posicao"] > id:
            cliente["posicao"] -= 1
    return {"mensagem": f"Cliente da posição {id} removido."}