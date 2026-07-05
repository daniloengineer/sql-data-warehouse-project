from airflow import DAG
from airflow.sdk import task 
from datetime import datetime
import pandas as pd
from hooks.postgres_hook import CustomPostgresHook

# Configuration for our different sources
SOURCES = {
    "crm_cust_info": "datasets/source_crm/cust_info.csv",
    "crm_prd_info": "datasets/source_crm/prd_info.csv",
    "crm_sales_details": "datasets/source_crm/sales_details.csv",
    "erp_loc_a101": "datasets/source_erp/LOC_A101.csv",
    "erp_cust_az12": "datasets/source_erp/CUST_AZ12.csv", 
    "erp_px_cat_g1v2": "datasets/source_erp/PX_CAT_G1V2.csv",
}

with DAG(
    dag_id="etl_csv_to_bronze", 
    start_date=datetime(2026, 5, 13), 
    schedule=None,
    catchup=False
):

    @task
    def load_csv_to_postgres(table_name, file_path):
        """Generic task to load a CSV into a specific Postgres table."""
        # 1. Path inside the Airflow container
        full_path = f"/opt/airflow/{file_path}"
        
        # 2. Read CSV with Pandas
        print(f"Reading file: {full_path}")
        df = pd.read_csv(full_path)
        
        # 3. Connect to Postgres
        hook = CustomPostgresHook(postgres_conn_id='postgres_dw')
        engine = hook.get_sqlalchemy_engine()
        
        # 4. Load to Bronze Schema
        df.to_sql(
            name=table_name,
            con=engine,
            schema='bronze',
            if_exists='replace', 
            index=False
        )
        return f"Successfully loaded {len(df)} rows into bronze.{table_name}"

    # FIX: Use .override to give each task a unique name in the UI
    for table, path in SOURCES.items():
        load_csv_to_postgres.override(task_id=f"load_{table}")(
            table_name=table, 
            file_path=path
        )