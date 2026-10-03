import os
import pymysql

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Navigation POC Backend",
    version="1.0.0"
)

# POC only.
# Since frontend and backend are behind the same LB/domain,
# CORS is not actually required for normal browser requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_connection():
    return pymysql.connect(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        unix_socket=os.environ["INSTANCE_UNIX_SOCKET"],
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )


@app.get("/")
def root():
    return {
        "application": "Navigation POC",
        "service": "backend",
        "status": "running"
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "backend"
    }


@app.get("/api/config-test")
def config_test():
    return {
        "db_name_configured": bool(os.getenv("DB_NAME")),
        "db_user_configured": bool(os.getenv("DB_USER")),
        "db_password_configured": bool(os.getenv("DB_PASSWORD")),
        "cloud_sql_socket_configured": bool(
            os.getenv("INSTANCE_UNIX_SOCKET")
        )
    }


@app.get("/api/db-test")
def db_test():

    connection = None

    try:
        connection = db_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS result")
            result = cursor.fetchone()

        return {
            "status": "connected",
            "database": os.getenv("DB_NAME"),
            "query_result": result["result"]
        }

    except Exception as e:

        return {
            "status": "failed",
            "error": str(e)
        }

    finally:

        if connection:
            connection.close()