import psycopg2
import streamlit as st


def get_connection():
    try:
        conn = psycopg2.connect(
            st.secrets["db"]["url"],
            sslmode="require",
            connect_timeout=10,
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None


def run_query(sql: str, params=None):
    conn = get_connection()
    if conn is None:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    except Exception as e:
        st.error(f"Error en la consulta: {e}")
        return []
    finally:
        conn.close()


def run_mutation(sql: str, params=None):
    conn = get_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error al ejecutar la operación: {e}")
        return False
    finally:
        conn.close()