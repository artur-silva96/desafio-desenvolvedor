
# desafio_api/database.py
from pymongo import MongoClient

# Conecta ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["desafio_db_simples"]

# Expõe as coleções para serem importadas em outros arquivos
collection_arquivos = db["arquivos"]
collection_dados = db["dados_instrumentos"]
