# ============================================================
# run.py — executa a API do Estúdio de Tatuagem
# Descrição: ponto de entrada para iniciar o servidor FastAPI.
# Como rodar: python run.py
# ============================================================

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
