from fastapi import FastAPI, HTTPException, status
from sqlmodel import text
from app import settings
from app.core.config import logger_config
from app.api.deps import DBSessionDep

logger = logger_config(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    servers=[
        {
            "url": "https://authorization-watt-demand-clinics.trycloudflare.com",
            "description": "Local development server"
        },
    ]
)


@app.post("/execute_sql")
def execute_sql_query(query: str, db: DBSessionDep):
    """
    Execute a raw SQL query and return the results including column names.
    """
    try:
        logger.info(f"Executing raw SQL query: {query}")

        results = db.exec(text(query))

        column_names = list(results.keys())
        data = [dict(zip(column_names, row)) for row in results.fetchall()]

        logger.info(f"Query results: columns={column_names}, data={data}")

        return {"columns": column_names, "data": data}

    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error executing query: {str(e)}"
        )


@app.get("/database_schema")
def get_database_schema(db: DBSessionDep):
    """
    Get the database schema including total tables, columns in each table, and column details.
    """
    try:
        logger.info("Fetching database schema information.")

        # Get total number of tables
        total_tables_query = """
        SELECT COUNT(*)
        FROM pg_catalog.pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
        """
        total_tables_result = db.exec(text(total_tables_query)).fetchone()
        total_tables = total_tables_result[0]

        # Get columns count, column names, and column types for each table
        columns_per_table_query = """
        SELECT t.tablename, a.attname AS column_name, pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type
        FROM pg_catalog.pg_tables t
        JOIN pg_catalog.pg_attribute a ON t.tablename = a.attrelid::regclass::text
        WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
          AND a.attnum > 0 AND NOT a.attisdropped
        ORDER BY t.tablename, a.attnum;
        """
        columns_per_table_result = db.exec(
            text(columns_per_table_query)).fetchall()

        # Organize the result into a structured format
        schema_info = {
            "total_tables": total_tables,
            "tables": {}
        }

        for row in columns_per_table_result:
            table_name = row.tablename
            if table_name not in schema_info["tables"]:
                schema_info["tables"][table_name] = {
                    "columns": []
                }
            schema_info["tables"][table_name]["columns"].append({
                "column_name": row.column_name,
                "data_type": row.data_type
            })

        logger.info(f"Database schema information: {schema_info}")
        return schema_info

    except Exception as e:
        logger.error(f"Error fetching database schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching database schema: {str(e)}"
        )
# @app.get("/database_schema", response_model=dict)
# def get_database_schema(db: DBSessionDep):
#     """
#     Get the database schema including total tables and columns in each table.
#     """
#     try:
#         logger.info("Fetching database schema information.")

#         # Get total number of tables
#         total_tables_query = """
#         SELECT COUNT(*)
#         FROM pg_catalog.pg_tables
#         WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
#         """
#         total_tables_result = db.exec(text(total_tables_query)).fetchone()
#         total_tables = total_tables_result[0]

#         # Get columns count for each table
#         columns_per_table_query = """
#         SELECT t.tablename, COUNT(a.attname) AS column_count
#         FROM pg_catalog.pg_tables t
#         JOIN pg_catalog.pg_attribute a ON t.tablename = a.attrelid::regclass::text
#         WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
#           AND a.attnum > 0 AND NOT a.attisdropped
#         GROUP BY t.tablename;
#         """
#         columns_per_table_result = db.exec(text(columns_per_table_query)).fetchall()

#         # Format the response
#         schema_info = {
#             "total_tables": total_tables,
#             "tables": [
#                 {"table_name": row.tablename, "column_count": row.column_count}
#                 for row in columns_per_table_result
#             ]
#         }

#         logger.info(f"Database schema information: {schema_info}")
#         return schema_info

#     except Exception as e:
#         logger.error(f"Error fetching database schema: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Error fetching database schema: {str(e)}"
#         )

# @app.get("/database_schema")
# def get_database_schema(db: DBSessionDep):
#     """
#     Get the database schema including total tables and columns in each table.
#     """
#     try:
#         logger.info("Fetching database schema information.")

#         # Get total number of tables
#         total_tables_query = """
#         SELECT COUNT(*)
#         FROM information_schema.tables
#         WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema');
#         """
#         total_tables_result = db.exec(text(total_tables_query)).fetchone()
#         total_tables = total_tables_result[0]

#         # Get columns count for each table
#         columns_per_table_query = """
#         SELECT table_name, COUNT(column_name) AS column_count
#         FROM information_schema.columns
#         WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
#         GROUP BY table_name;
#         """
#         columns_per_table_result = db.exec(
#             text(columns_per_table_query)).fetchall()

#         # Format the response
#         schema_info = {
#             "total_tables": total_tables,
#             "tables": [
#                 {"table_name": row.table_name, "column_count": row.column_count}
#                 for row in columns_per_table_result
#             ]
#         }

#         logger.info(f"Database schema information: {schema_info}")
#         return schema_info

#     except Exception as e:
#         logger.error(f"Error fetching database schema: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Error fetching database schema: {str(e)}"
#         )
