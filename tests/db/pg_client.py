import os

import psycopg2
from psycopg2 import connection


def connect() -> connection:
    conn = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        database="postgres",
        user="postgres",
        password="postgres",
    )
    return conn
