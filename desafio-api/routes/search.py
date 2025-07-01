# desafio_api/routers/search.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict
from desafio_api.data.database import collection_dados
from pymongo import DESCENDING

search_router = APIRouter(tags=["Busca"])

@search_router.get("/buscar/", response_model=Dict)
async def buscar_conteudo(
    TckrSymb: Optional[str] = Query(None, description="Símbolo do Ticker (ex: AMZO34)"),
    RptDt: Optional[str] = Query(None, description="Data do relatório (formato: AAAA-MM-DD)"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """
    Busca informações de ativos com os seguintes critérios:
    
    - Se TckrSymb e RptDt são fornecidos: Retorna o registro específico
    - Se nenhum parâmetro é fornecido: Retorna resultados paginados
    - Se apenas um parâmetro é fornecido: Retorna resultados filtrados e paginados
    
    Retorna um objeto com os campos:
    - RptDt: Data do relatório
    - TckrSymb: Símbolo do ticker
    - MktNm: Nome do mercado
    - SctyCtgyNm: Categoria do ativo
    - ISIN: Código ISIN
    - CrpnNm: Nome da empresa
    """
    try:
        # Construção da query
        query = {}
        if TckrSymb:
            query["TckrSymb"] = TckrSymb
        if RptDt:
            query["RptDt"] = RptDt

        # Campos a serem retornados
        projection = {
            "_id": 0,
            "RptDt": 1,
            "TckrSymb": 1,
            "MktNm": 1,
            "SctyCtgyNm": 1,
            "ISIN": 1,
            "CrpnNm": 1
        }

        # Se ambos os parâmetros foram fornecidos, retorna apenas um registro
        if TckrSymb and RptDt:
            result = collection_dados.find_one(query, projection)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhum resultado encontrado para os critérios fornecidos."
                )
            return result

        # Caso contrário, retorna resultados paginados
        skip = (page - 1) * page_size
        total = collection_dados.count_documents(query)
        
        cursor = collection_dados.find(
            query,
            projection
        ).sort("RptDt", DESCENDING).skip(skip).limit(page_size)

        results = list(cursor)

        if not results and page == 1:
            raise HTTPException(
                status_code=404,
                detail="Nenhum resultado encontrado."
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
            detail=f"Erro ao realizar a busca: {str(e)}"
        )