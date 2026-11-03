import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv(Path(__file__).with_name(".env"))


def get_db():
    try:
        conexion = pymysql.connect(
            host=os.environ["DB_HOST"],
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            connect_timeout=5,
        )
    except pymysql.MySQLError:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con la base de datos.",
        )

    try:
        yield conexion
    finally:
        conexion.rollback()
        conexion.close()