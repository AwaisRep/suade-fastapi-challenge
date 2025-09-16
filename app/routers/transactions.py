from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from typing import Annotated, Optional

from ..services.transaction_validator import validate_file
from ..services.transaction_summary import get_summary
from ..services.file_handler import save_file

router = APIRouter()

@router.post('/upload')
async def upload(file: Annotated[UploadFile, File()]):
    """
    Allows the upload of a valid CSV file containing some transaction data

    Args:
        file: The file must be of type .csv
    
    Returns:
        dict: Success message with the file path
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files can be uploaded."
        )
    
    try:
        await validate_file(file) # Attempt to validate the file
        file.file.seek(0) # Set the seek pointer back to 0 to reset progress
        saved_file = await save_file(file) # Save the file
        return {"message": f"File uploaded successfully at {saved_file}"}
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )

@router.get('/summary/{user_id}')
async def summary(
        user_id: str,
        date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
    ):

    """ 
    Fetch the summary statistics from the uploaded CSV file for a particular user,
    optionally filtered by date range

    Args:
        user_id: The user ID to fetch statistics for
        date_from: Optional start date for filtering
        date_to: Optional end date for filtering
    
    Returns:
    dict: Summary of statics in the form of max, min and average transaction amounts
    """

    try:
        summary = await get_summary(user_id, date_from, date_to)
        return {"data": summary}
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )