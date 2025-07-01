# desafio_api/routers/history.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict
from desafio_api.data.database import collection_arquivos
from pymongo import DESCENDING

history_router = APIRouter(tags=["Histórico"])

@history_router.get("/historico/", response_model=Dict)
async def buscar_historico(
    nome_arquivo: Optional[str] = Query(None, description="Nome do arquivo para busca"),
    data_referencia: Optional[str] = Query(None, description="Data de referência (formato: AAAA-MM-DD)"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """
    Busca o histórico de uploads de arquivos.
    
    Parâmetros:
    - nome_arquivo: Filtra por nome do arquivo
    - data_referencia: Filtra por data de upload
    - page: Número da página
    - page_size: Quantidade de itens por página
    
    Retorna:
    - Lista paginada dos uploads realizados
    - Informações sobre status do processamento
    - Data do upload
    - Quantidade de registros processados
    """
    try:
        # Construção da query
        query = {}
        if nome_arquivo:
            query["nome_arquivo"] = nome_arquivo
        if data_referencia:
            # Busca uploads realizados na data especificada
            query["data_upload"] = {"$regex": f"^{data_referencia}"}

        # Campos a serem retornados
        projection = {
            "_id": 0,
            "nome_arquivo": 1,
            "data_upload": 1,
            "quantidade_registros": 1,
            "status": 1,
            "erro": 1
        }

        # Se ambos os parâmetros foram fornecidos, retorna apenas um registro
        if nome_arquivo and data_referencia:
            result = collection_arquivos.find_one(query, projection)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhum registro encontrado para os critérios fornecidos."
                )
            return result

        # Caso contrário, retorna resultados paginados
        skip = (page - 1) * page_size
        total = collection_arquivos.count_documents(query)
        
        cursor = collection_arquivos.find(
            query,
            projection
        ).sort("data_upload", DESCENDING).skip(skip).limit(page_size)

        results = list(cursor)

        if not results and page == 1:
            raise HTTPException(
                status_code=404,
                detail="Nenhum registro encontrado."
            )

        return {
            "total_resultados": total,
            "pagina_atual": page,
            "total_paginas": (total + page_size - 1) // page_size,
            "resultados": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )
