import os
import urllib.parse
import certifi
from sqlalchemy import create_engine, text
import pymysql
import psycopg2
import snowflake.connector
from databricks import sql as dbsql
import streamlit as st

def get_connection_string(config):
    """
    Generates a database connection string based on the configuration.
    """
    db_type = config.get('TYPE', '')
    user = config.get('USER', '')
    password = urllib.parse.quote_plus(config.get('PASSWORD', ''))
    host = config.get('HOST', '')
    port = config.get('PORT', '')
    database = config.get('DATABASE', '')
    
    if "MySQL" in db_type:
        return (
            f"mysql+pymysql://{user}:{password}@"
            f"{host}:{port}/{database}"
            f"?ssl_ca={certifi.where()}&ssl_verify_cert=true&ssl_verify_identity=true"
        )
    elif "PostgreSQL" in db_type:
        return (
            f"postgresql+psycopg2://{user}:{password}@"
            f"{host}:{port}/{database}"
        )
    elif "SQL Server" in db_type:
        return (
            f"mssql+pymssql://{user}:{password}@"
            f"{host}:{port}/{database}"
        )
    elif "Snowflake" in db_type:
        schema = config.get('SCHEMA', 'PUBLIC')
        warehouse = config.get('WAREHOUSE', '')
        role = config.get('ROLE', '')
        return (
            f"snowflake://{user}:{password}"
            f"@{host}/{database}/{schema}"
            f"?warehouse={warehouse}&role={role}"
        )
    elif "Databricks" in db_type:
        http_path = config.get('HTTP_PATH', '')
        catalog = config.get('CATALOG', 'hive_metastore')
        return (
            f"databricks://token:{password}"
            f"@{host}:443/{database}"
            f"?http_path={http_path}&catalog={catalog}&schema={database}"
        )
    elif "SQLite" in db_type:
        return f"sqlite:///{database}"
    
    raise ValueError(f"Unsupported database type: {db_type}")

def test_connection(config):
    """
    Tests the database connection and returns a tuple (success, database_list).
    """
    db_type = config.get('TYPE', '')
    
    try:
        if "MySQL" in db_type:
            # Use pymysql directly for testing to avoid some sqlalchemy overhead/issues during test
            connection = pymysql.connect(
                host=config['HOST'],
                user=config['USER'],
                password=config['PASSWORD'],
                port=int(config['PORT']),
                ssl={'ca': certifi.where()}
            )
            with connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                dbs = [db[0] for db in cursor.fetchall() 
                       if db[0] not in ('sys', 'mysql', 'performance_schema', 'information_schema', 'METRICS_SCHEMA')]
            connection.close()
            return True, dbs

        elif "PostgreSQL" in db_type:
            # Construct a temp connection string to 'postgres' db to list others
            temp_config = config.copy()
            temp_config['DATABASE'] = 'postgres'
            conn_str = get_connection_string(temp_config)
            engine = create_engine(conn_str)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
                dbs = [row[0] for row in result if row[0] not in ('postgres', 'cloudsqladmin')]
            return True, dbs

        elif "SQL Server" in db_type:
            # Connect to 'master' to list DBs
            temp_config = config.copy()
            temp_config['DATABASE'] = 'master'
            conn_str = get_connection_string(temp_config)
            engine = create_engine(conn_str)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM master.dbo.sysdatabases"))
                dbs = [row[0] for row in result if row[0] not in ('master', 'tempdb', 'model', 'msdb')]
            return True, dbs

        elif "Snowflake" in db_type:
            ctx = snowflake.connector.connect(
                user=config['USER'],
                password=config['PASSWORD'],
                account=config['HOST'],
                warehouse=config.get('WAREHOUSE'),
                role=config.get('ROLE')
            )
            cs = ctx.cursor()
            cs.execute("SHOW DATABASES")
            dbs = [row[1] for row in cs.fetchall()]
            cs.close()
            ctx.close()
            return True, dbs

        elif "Databricks" in db_type:
            with dbsql.connect(
                server_hostname=config['HOST'],
                http_path=config['HTTP_PATH'],
                access_token=config['PASSWORD'],
                catalog=config.get('CATALOG', 'hive_metastore')
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW SCHEMAS")
                    dbs = [row[0] for row in cursor.fetchall()]
            return True, dbs

        elif "SQLite" in db_type:
            db_path = config['DATABASE'].strip().replace('sqlite:///', '').replace('sqlite://', '')
            db_path = os.path.expanduser(db_path)
            db_path = os.path.abspath(db_path)
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found at: {db_path}")
            
            # Test connection
            engine = create_engine(f"sqlite:///{db_path}")
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return True, [db_path]

    except Exception as e:
        return False, [str(e)]

    return False, []

def get_snowflake_schemas(config, database):
    """Fetch schemas for a given Snowflake database"""
    try:
        ctx = snowflake.connector.connect(
            user=config['USER'],
            password=config['PASSWORD'],
            account=config['HOST'],
            warehouse=config.get('WAREHOUSE'),
            role=config.get('ROLE'),
            database=database
        )
        cs = ctx.cursor()
        cs.execute(f"SHOW SCHEMAS IN DATABASE {database}")
        schemas = [row[1] for row in cs.fetchall() if row[1] != 'INFORMATION_SCHEMA']
        cs.close()
        ctx.close()
        return schemas
    except Exception as e:
        st.error(f"Error fetching schemas: {e}")
        return []
