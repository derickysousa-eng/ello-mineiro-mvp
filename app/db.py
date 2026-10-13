"""
Módulo de conexão com o Banco de Dados MySQL usando SQL Puro (PyMySQL).
Todas as credenciais são obtidas exclusivamente via variáveis de ambiente (.env).
"""

import os
import ssl
from typing import Generator
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ello_mineiro")
DB_SSL = os.getenv("DB_SSL", "false").lower() in ("true", "1", "yes")


def get_raw_connection() -> pymysql.Connection:
    """
    Cria e retorna uma conexão direta com o MySQL.
    Configura DictCursor para retorno de dicionários nas consultas.
    Aplica SSL quando configurado (necessário para nuvem/TiDB).
    """
    ssl_context = None
    if DB_SSL:
        # TiDB Cloud e provedores gerenciados exigem SSL/TLS ativo
        ssl_context = ssl.create_default_context()

    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,  # Controle transacional explícito (commit / rollback manual)
        ssl=ssl_context
    )


def get_db() -> Generator[pymysql.Connection, None, None]:
    """
    Dependência do FastAPI para injeção de conexão segura com controle transacional.
    Garante fechamento e rollback automático em caso de exceções.
    """
    conn = get_raw_connection()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
