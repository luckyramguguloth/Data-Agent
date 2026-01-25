import duckdb
import polars as pl

class SQLEngine:
    def __init__(self):
        self.conn = duckdb.connect(database=':memory:')

    def register_table(self, table_name: str, df: pl.DataFrame):
        """
        Registers a Polars DataFrame as a DuckDB table.
        """
        # DuckDB can query Polars directly
        self.conn.register(table_name, df)

    def run_query(self, query: str):
        """
        Executes a SQL query and returns the result as a list of dicts.
        """
        try:
            # Limit to 100 rows for safety in UI
            if "limit" not in query.lower():
                query += " LIMIT 100"
                
            result = self.conn.execute(query).fetch_df()
            return result.to_dict(orient='records'), None
        except Exception as e:
            return None, str(e)