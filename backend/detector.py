import magic

def detect_file_type(file_path):
    """
    Implements the detection logic from Section 5.1 of the docs.
    """
    mime = magic.from_file(file_path, mime=True)
    
    if 'csv' in mime or file_path.endswith('.csv'):
        return 'csv'
    elif 'spreadsheet' in mime or file_path.endswith('.xlsx'):
        return 'excel'
    elif 'json' in mime or file_path.endswith('.json'):
        return 'json'
    elif 'parquet' in mime or file_path.endswith('.parquet'):
        return 'parquet'
    return 'unknown'