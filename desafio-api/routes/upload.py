# desafio_api/routers/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from desafio_api.data.database import collection_arquivos, collection_dados
from desafio_api.utils.file_handler import processa_arquivo

upload_router = APIRouter(tags=["Upload"])

@upload_router.post("/upload/")
async def upload_arquivo(file: UploadFile = File(...)):
    """
    Endpoint para upload de arquivo CSV ou Excel.
    
    - Não permite enviar o mesmo arquivo duas vezes
    - Suporta arquivos CSV e Excel
    - Armazena os dados no MongoDB
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nenhum arquivo foi enviado."
        )

    # Verifica se o arquivo já foi enviado
    arquivo_existente = collection_arquivos.find_one({"nome_arquivo": file.filename})
    if arquivo_existente:
        raise HTTPException(
            status_code=400, 
            detail=f"O arquivo '{file.filename}' já foi enviado anteriormente."
        )

    # Verifica a extensão do arquivo
    extensoes_permitidas = ('.csv', '.xls', '.xlsx')
    if not any(file.filename.lower().endswith(ext) for ext in extensoes_permitidas):
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo não suportado. Use CSV ou Excel."
        )

    # Lê o conteúdo do arquivo
    contents = await file.read()
    
    try:
        # Processa o arquivo
        dados = processa_arquivo(contents, str(file.filename))
        
        if not dados:
            raise HTTPException(
                status_code=400,
                detail="O arquivo está vazio ou não contém dados válidos."
            )
        
        # Insere os dados no MongoDB
        collection_dados.insert_many(dados)
        
        # Registra o upload no histórico
        collection_arquivos.insert_one({
            "nome_arquivo": file.filename,
            "data_upload": datetime.now().isoformat(),
            "quantidade_registros": len(dados),
            "status": "processado"
        })
        
        return {
            "mensagem": "Upload realizado com sucesso!",
            "arquivo": file.filename,
            "registros_processados": len(dados)
        }
        
    except HTTPException as e:
        # Registra falha no histórico
        collection_arquivos.insert_one({
            "nome_arquivo": file.filename,
            "data_upload": datetime.now().isoformat(),
            "status": "erro",
            "erro": str(e.detail)
        })
        raise e
    except Exception as e:
        # Registra falha no histórico
        collection_arquivos.insert_one({
            "nome_arquivo": file.filename,
            "data_upload": datetime.now().isoformat(),
            "status": "erro",
            "erro": str(e)
        })
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar o arquivo: {str(e)}"
        )
