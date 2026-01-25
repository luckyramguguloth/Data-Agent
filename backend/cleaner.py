import polars as pl

class DataCleaner:
    def clean_data(self, df: pl.DataFrame):
        """
        Performs basic cleaning:
        1. Standardize column names (snake_case)
        2. Handle missing values (fill numeric with 0, string with "Unknown")
        3. Drop duplicates
        """
        # 1. Clean Column Names (remove spaces, lowercase)
        clean_cols = [c.lower().replace(" ", "_").replace("-", "_") for c in df.columns]
        df = df.rename(dict(zip(df.columns, clean_cols)))

        # 2. Handle Nulls (Simple Strategy)
        # In a real app, this would be configurable via UI
        df = df.fill_null(strategy="forward")  # Forward fill as a safe default

        # 3. Deduplicate
        df = df.unique()

        return df