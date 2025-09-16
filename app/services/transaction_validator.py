import pandas as pd
import io
from datetime import datetime
from fastapi import UploadFile

from .file_handler import load_file, FileTooLargeError

class ValidationError(Exception):
    """Custom exception to raise during file validation, for better categorisation"""
    pass

REQUIRED_HEADERS = [
    "transaction_id", 
    "user_id", 
    "product_id", 
    "timestamp",
    "transaction_amount"
]

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S" # We always expect this form for the timestamp value
 
async def validate_file(file: UploadFile) -> None:
    """
    Verifies the file, uploaded by the user, meets the schema requirements

    Args:
        file: The file the user wishes to upload
    """
    try:
        # Read the file into memory and decode the content into a CSV format
        content_bytes = await load_file(file)

        # Convert bytes to string and create file-like object for pandas
        content_str = content_bytes.decode('utf-8')
        content_io = io.StringIO(content_str)
        
        # Read CSV with clear schema header columns to verify against
        dataframe = pd.read_csv(content_io, 
            usecols=REQUIRED_HEADERS,
            dtype={
                'transaction_id': 'str',
                'user_id': 'str', 
                'product_id': 'str',
                'timestamp': 'str',
                'transaction_amount': 'str'
            })

        if dataframe.empty:
            raise ValidationError("CSV is empty.")
        
        # Validate all rows in the file
        _validate_dataframe(dataframe)
            
    # Custom error handling for better catgeorisation
    except FileTooLargeError:
        raise ValidationError("File uploaded exceeds 95mb limit")
    except UnicodeDecodeError:
        raise ValidationError("File must be UTF-8 encoded")
    except pd.errors.ParserError as e:
        raise ValidationError(f"CSV error occurred during parsing: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Invalid CSV format: {str(e)}")

def _validate_dataframe(df: pd.DataFrame) -> None:
    """
    Fast validation of timestamp format and transaction amount using vectorised operations

    Args:
        df: A pd.DataFrame to validate
    """
    
    # Validate all timestamps in rows
    validate_timestamps = pd.to_datetime(df['timestamp'], format=TIMESTAMP_FORMAT, errors='coerce')
    # Validate all transaction_amount in rows
    amount_series = pd.to_numeric(df['transaction_amount'], errors='coerce')
    # Errors are set to coerce so that it gracefully handles errors, we can post-process with line number easily this way


    # Use the pd frame to build a mask of invalid values, and apply to the original dataframe to fetch the errors only

    invalid_timestamps_indexes = df[validate_timestamps.isnull()].index # Get indexes of the array with invalid timestamps
    if len(invalid_timestamps_indexes) > 0:
        first_error = invalid_timestamps_indexes[0] # We only need the first error which will get sent back to the user
        error_val = df.at[first_error, 'timestamp'] # Extract the particular error raised
        raise ValidationError(f"Invalid timestamp found on line {first_error}: {error_val}")
    
    invalid_amount_indexes = df[amount_series.isnull()].index # Get index of the array with invalid transaction amounts
    if len(invalid_amount_indexes) > 0:
        first_error = invalid_amount_indexes[0] 
        error_val = df.at[first_error, 'transaction_amount']
        raise ValidationError(f"Invailid transaction amount found on line {first_error}: {error_val}")