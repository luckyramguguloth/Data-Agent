import polars as pl
import io

class DataLoader:
    def __init__(self, security_manager=None):
        self.security = security_manager

    def load_file(self, file_path, file_type):
        """
        Loads encrypted file into a Polars DataFrame based on detected type.
        """
        try:
            # Decrypt Key Integration
            if self.security:
                file_content = self.security.decrypt_file_to_memory(file_path)
                source = io.BytesIO(file_content)
            else:
                source = file_path # Fallback for plain files

            if file_type == 'csv':
                return pl.read_csv(source, try_parse_dates=True, ignore_errors=True)
            elif file_type == 'excel':
                return pl.read_excel(source)
            elif file_type == 'json':
                return pl.read_json(source)
            elif file_type == 'parquet':
                return pl.read_parquet(source)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            print(f"Error loading file: {e}")
            return None