from airflow.providers.common.sql.hooks.sql import DbApiHook
import psycopg2

class CustomPostgresHook(DbApiHook):
    """
    Custom Hook for PostgreSQL using psycopg2.
    Inheriting from DbApiHook provides standard SQL execution methods.
    """
    conn_name_attr = 'postgres_conn_id'
    default_conn_name = 'postgres_default'
    conn_type = 'postgres'
    hook_name = 'Postgres'

    def __init__(self, postgres_conn_id=default_conn_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id

    def get_conn(self):
        """
        Establishes the raw psycopg2 connection.
        Used for low-level SQL execution.
        """
        conn = self.get_connection(self.postgres_conn_id)

        # UPDATED: Use 5432 as default for internal Docker networking
        port = conn.port if conn.port else 5433

        return psycopg2.connect(
            host=conn.host,
            port=port,
            database=conn.schema,
            user=conn.login,
            password=conn.password
        )

    def get_sqlalchemy_engine(self, engine_kwargs=None):
        """
        Returns the SQLAlchemy engine required for Pandas to_sql.
        """
        conn = self.get_connection(self.postgres_conn_id)
        port = conn.port if conn.port else 5433
        
        # Format: postgresql+psycopg2://user:password@host:port/dbname
        uri = (
            f"postgresql+psycopg2://{conn.login}:{conn.password}@"
            f"{conn.host}:{port}/{conn.schema}"
        )
        
        from sqlalchemy import create_engine
        return create_engine(uri, **(engine_kwargs or {}))