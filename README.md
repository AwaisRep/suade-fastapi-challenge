# Suade Challenge

## Libraries Utilised

Alongside the core requirement of FastAPI, this submission uses pandas and pytest.

Using pandas allowed me to consistently process large datasets efficiently, scanning for any mismatches against the schema, asynchronously.  
I chose pytest because it lets me write clear and concise tests with minimal setup, while reusable fixtures helped avoid repeating code. Its strong integration with FastAPI made it an easy choice for me.


## Endpoints
1. /upload/  
Uploads a CSV file of transactions. The file must follow the schema: Transaction ID, User ID, Product ID, Timestamp, Transaction Amount.

2. /summary/  
Returns transaction summaries for a given user, with optional date range filters.


## Getting Started

Follow these steps to test and interact with the API

### Prerequisites

You need to have the following software installed on your machine and added to your PATH.

*   Python (v3.12.3 or later)

### Installation & Startup

1. **Clone or download this repository and enter the directory**

2. **Create a Python virtual environment**
    ```sh
    python -m venv .venv
    ```

3. **Activate the venv**
    ```sh
    .venv\Scripts\activate
    ```
    Please note the above command is for the Windows command line and may differ between applications and operating systems

4.  **Install Python packages**
    ```sh
    pip install -r requirements.txt
    ```

5. **Run the dev API server**
    ```sh
    uvicorn app.main:app --reload
    ```
    This will launch a dev fastapi server, usually running on the localhost port 8000.  
    But please take note of the specific port printed by the console.

    If you wish to specify your own port, then you may do so as such:
    ```sh
    uvicorn app.main:app --port <port> --reload
    ```


## Interacting with the API:

Now that the FastAPI server is running, you can interact with the available endpoints as follows:

**The API docs**

1. **Enter the dev docs page in your browser**  
    In your browser navigate to the URL: localhost:\<port>\/docs

2. **Click on the endpoint you wish to execute**  
    For upload: Click 'Try it out'. A dialog should appear for you to select your CSV file.  
    Once you have selected it, click 'Execute' and it will show the result of the fetch.

    For summary: Click 'Try it out'. Three input fields will appear, the first (user id) is required, the remaining are optional.  
    Once you have entered the desired data, click 'Execute' and it will show the result of the query.

**cURL commands**

1. If you have cURL installed, you can use it to test the endpoints without launching the docs page, by entering your command line/terminal.

    For uploading of data (set path to full path of the CSV file):  
    ```sh
    curl -X POST "http://localhost:8000/upload" -F "file=@<path>"
    ```

    For summary of data:
    ```sh
    curl -X GET "http://localhost:8000/summary/{user_id}"
    ```
    Optional Query Params to add to the end of the URL:
    ```sh
    ?date_from=YYYY-MM-DD
    ?date_to=YYYY-MM-DD
    ```

## Testing
A small test suite is included to verify core functionality of the API.  
The tests cover the following cases:

- **File upload validation**  
  - Successful upload of a valid CSV file  
  - Rejection of files with invalid schema or missing fields  
  - Rejection of large files that exceed the 95mb limit

- **Summary endpoint**  
  - Querying transaction summaries for a given user  
  - Graceful handling of summary queries with no uploaded files
  - Applying optional `date_from` and `date_to` filters and applying defensive handles

The test suite assumes an empty uploads/ directory. Please clear this folder before executing pytest.

To run the tests, make sure you are in the root folder of the program, then run:
```sh
pytest -v
```
Please be aware this command may take up to a minute before showing any result, as it dynamically generates the sample data, which are large files.

## Justification Notes

Upon reviewing the file upload validation logic, you will notice that the program currently validates only two fields in the schema: **timestamp** and **transaction_amount**.  

This decision was made because the first three fields can vary depending on the customer type. For example, IDs may follow different patterns, some numeric only, while others combine numbers and characters. As such, enforcing strict validation on these fields could introduce unnecessary complexity and limit flexibility for different customers.

However, **timestamp** and **transaction_amount** are values that can be validated consistently. Timestamps are expected to follow a parseable format (which pandas can interpret reliably), and transaction amounts must always represent numeric values that can be safely cast to floats.

Finally, I recognise that the current tests are not as extensive as production-level code. However, this was a deliberate choice to keep the system straightforward and avoid overcomplicating the setup at this stage.