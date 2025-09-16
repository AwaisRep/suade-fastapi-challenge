import pandas as pd
import io
from datetime import datetime
from typing import TypedDict, Optional
from .file_handler import load_from_disk

from fastapi import Query

class SummaryError(Exception):
    """Custom exception for summary generation errors"""
    pass

class Summary(TypedDict):
    """Data structure for returning summary"""
    maximum: float
    minimum: float
    average: float

REQUIRED_HEADERS = [
    "transaction_id", 
    "user_id", 
    "product_id", 
    "timestamp",
    "transaction_amount"
]

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

def parse_date(date_str: str):
    """Simple helper function to parse date queries"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise SummaryError(f"Invalid date format: {date_str}")

async def load_transactions_data() -> pd.DataFrame:
    """
    Load transaction data from disk and prepare it for data extraction
    
    Returns:
        pd.DataFrame: Clean dataframe ready for analysis
    """
    try:
        # Load file content from disk
        content = await load_from_disk()
        
        # Convert string content to file-like object for pandas
        content_io = io.StringIO(content)
        
        # Read CSV with appropriate data types
        dataframe = pd.read_csv(
            content_io,
            usecols=REQUIRED_HEADERS,
            dtype={
                'transaction_id': 'str',
                'user_id': 'str', 
                'product_id': 'str',
                'transaction_amount': 'float64'
            },
            parse_dates=['timestamp'],
            date_format=TIMESTAMP_FORMAT
        )
        
        if dataframe.empty:
            raise SummaryError("No transaction data available")
        
        # Sort the dataframe by timestamp for better indexing
        dataframe = dataframe.sort_values('timestamp')
        
        return dataframe
    
    # Precise error handling for debugging purposes
    except FileNotFoundError:
        raise SummaryError("No transaction file found. Please upload a CSV file first.")
    except pd.errors.ParserError as e:
        raise SummaryError(f"Error parsing transaction data: {str(e)}")
    except Exception as e:
        raise SummaryError(f"Failed to load transaction data: {str(e)}")


async def get_summary(
        user_id: str, 
        date_from: Optional[str] = None, 
        date_to: Optional[str] = None
    ) -> Summary:
    """
    Return the summary statistics for a user
    
    Args:
        user_id: the id of the user that needs statistics
        date_from: optional start date for filtering
        date_to: optional end date for filtering

    Returns:
        Summary: the three statistics required
    """

    try:
        df = await load_transactions_data() # First attempt to load the csv file the user uploaded
        
        user_data = df[df['user_id'] == user_id]
        if user_data.empty:
            raise SummaryError(f"No transactions found for user {user_id}")

        # Try to parse the dates as real datetimes
        date_from_parsed = parse_date(date_from) if date_from else None
        date_to_parsed = parse_date(date_to) if date_to else None

        # Safely checks if both dates are given, if so we must make sure that from is before to chronologically
        if date_from is not None or date_to is not None:
            if date_from_parsed and date_to_parsed:
                if date_from_parsed > date_to_parsed:
                    raise SummaryError("date_from cannot be after date_to")
            user_data = _filter_by_timeframe(user_data, date_from, date_to)

        # dropna will help us to determine if any transactions exist for this user, if not then we raise an error
        amounts = user_data['transaction_amount'].dropna()
        if amounts.empty:
            raise SummaryError(f"No valid transaction amounts for user {user_id} in the given date range")

        return Summary(
            maximum = float(user_data['transaction_amount'].max()),
            minimum = float(user_data['transaction_amount'].min()),
            average = round(float(user_data['transaction_amount'].mean()), 2)
        )

    except Exception as e:
        raise SummaryError(f"Error in summary extraction: {e}")
    
def _filter_by_timeframe(df: pd.DataFrame, date_from: Optional[str], date_to: Optional[str]) -> pd.DataFrame:
    """
    Filter the dataframe by the dates entered by the user

    Args:
        df: the dataframe to be filtered
        date_from: optional start date to filter from
        date_to: optional end date to filter up to

    Returns:
        pd.DataFrame: a filtered dataframe
    """

    try:
        # Convert optional params to datetime pandas understands

        if date_from is not None:
            start_date = pd.to_datetime(date_from)
            df = df[df["timestamp"] >= date_from]
        
        if date_to is not None:
            end_date = pd.to_datetime(date_to)
            df = df[df["timestamp"] < date_to]

        # Creates a new dataframe by extracting the lines where the condition of the timestamp is between the two dates
        return df

    except Exception as e:
        raise SummaryError(f"Failed to filter by timestamp: {e}")