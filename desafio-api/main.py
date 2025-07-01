# main.py
from fastapi import FastAPI

# Cria a aplicação principal
app = FastAPI(title="Desafio Oliveira Trust")


from desafio_api.routers import upload, history, search

# Inclui as rotas dos diferentes módulos
app.include_router(upload.upload_router)
app.include_router(history.history_router)
app.include_router(search.search_router)

# Para executar a API, use o comando:
# uvicorn desafio_api.main:app --reload