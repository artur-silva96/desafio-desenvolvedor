# desafio_api/utils/file_handler.py
import pandas as pd
from io import BytesIO, StringIO
from fastapi import HTTPException
from typing import Literal, Dict, List, Any
import logging

def normalize_column_name(col: str) -> str:
    """
    Normaliza o nome da coluna removendo espaços extras, caracteres especiais e deixando tudo em maiúsculo
    """
    return col.strip().upper().replace(' ', '')

def processa_arquivo(contents: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Processa o arquivo CSV ou Excel e retorna uma lista de dicionários com os dados.
    """
    try:
        if filename.endswith('.csv'):
            # Lê o arquivo como texto
            text_content = contents.decode('latin1')  # Usa latin1 que é mais comum para arquivos brasileiros
            
            # Divide em linhas
            lines = text_content.split('\n')
            
            # Remove a primeira linha (status) e linhas vazias
            data_lines = [line for line in lines[1:] if line.strip()]
            
            # Cria um novo CSV apenas com os dados
            csv_content = '\n'.join(data_lines)
            
            # Lê com pandas
            df = pd.read_csv(
                StringIO(csv_content),
                sep=';',  # Separador padrão do arquivo
                encoding='latin1'
            )
            
        elif filename.endswith(('.xls', '.xlsx')):
            # Para Excel, pula a primeira linha
            df = pd.read_excel(BytesIO(contents), skiprows=[0])
        else:
            raise HTTPException(
                status_code=400,
                detail="Formato de arquivo não suportado. Use CSV ou Excel."
            )
        
        # Seleciona apenas as colunas necessárias
        colunas_necessarias = ['RptDt', 'TckrSymb', 'MktNm', 'SctyCtgyNm', 'ISIN', 'CrpnNm']
        
        # Verifica se todas as colunas necessárias estão presentes
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        if colunas_faltantes:
            raise HTTPException(
                status_code=400,
                detail=f"Colunas obrigatórias faltando no arquivo: {', '.join(colunas_faltantes)}"
            )
        
        # Seleciona apenas as colunas que precisamos
        df = df[colunas_necessarias]
        
        # Converte para dicionário
        return df.to_dict(orient="records")  # type: ignore
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Erro ao ler o arquivo. Verifique se o arquivo está no formato correto."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar o arquivo: {str(e)}"
        )
