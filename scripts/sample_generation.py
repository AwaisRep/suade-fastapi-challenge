import csv
import random
from pathlib import Path
from faker import Faker

PROJECT_ROOT = Path(__file__).resolve().parent.parent # Root path of the current sample file
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "test-data" # The route of the sample test data directory
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

TRANSACTIONS = 1000000
HEADERS = ["transaction_id", "user_id", "product_id", "timestamp", "transaction_amount"]

# Initialize Faker
fake = Faker()

# Pre-generate reusable data pools for major performance boost (files were taking too long to generate)
UUID_POOL = [fake.uuid4() for _ in range(10000)]
TIMESTAMP_POOL = [fake.date_time_between(start_date="-1y", end_date="now") for _ in range(5000)]

def generate_sample():
    """Main function to generate sample data for tests"""

    valid_file = TEST_DATA_DIR / "valid_sample.csv"
    large_file = TEST_DATA_DIR / "large_sample.csv"
    invalid_file = TEST_DATA_DIR / "invalid_sample.csv"

    # Only generate the data of the files that do not exist in the test directory
    if not valid_file.exists():
        _generate_valid_sample(TRANSACTIONS, valid_file)

    if not large_file.exists():
        _generate_valid_sample(1_500_000, large_file)
    
    if not invalid_file.exists():
        _generate_invalid_sample(100_000, invalid_file)


def _generate_valid_sample(rows: int, file_name: str):
    """
    Generate valid sample data

    Args:
        rows: The number of random transactions to generate
        file_name: The particular sample data we are generating - either a valid or large sample
    """
    # Open the CSV file for writing
    with Path(file_name).open(mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()

        # Generate dummy data in batches for massive performance improvement
        batch_size = 10000
        for batch_start in range(0, rows, batch_size):
            batch_data = []
            current_batch_size = min(batch_size, rows - batch_start)
            
            for _ in range(current_batch_size):
                batch_data.append({
                    "transaction_id": random.choice(UUID_POOL),
                    "user_id": fake.random_int(min=1, max=1000),
                    "product_id": fake.random_int(min=1, max=500),
                    "timestamp": random.choice(TIMESTAMP_POOL),
                    "transaction_amount": round(random.uniform(5.0, 500.0), 2),
                })
            
            writer.writerows(batch_data)


def _generate_invalid_sample(rows: int, file_name: str):
    """
    Generates a sample with some invalid data

    Args:
        rows: The number of random transactions to generate
        file_name: The path of the invalid sample to be written to
    """
    # Open the CSV file for writing
    with Path(file_name).open(mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()

        # Generate dummy data in batches
        batch_size = 10000
        corruption_letters = "abcdefghijklmnopqrstuvwxyz"
        
        for batch_start in range(0, rows, batch_size):
            batch_data = []
            current_batch_size = min(batch_size, rows - batch_start)
            
            for i in range(current_batch_size):
                global_i = batch_start + i

                row = {
                    "transaction_id": random.choice(UUID_POOL),
                    "user_id": fake.random_int(min=1, max=1000),
                    "product_id": fake.random_int(min=1, max=500),
                    "timestamp": random.choice(TIMESTAMP_POOL),
                    "transaction_amount": round(random.uniform(5.0, 500.0), 2),
                }

                # On every 100,000th row we add some invalid data
                if global_i % 100_000 == 0:
                    ts_str = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S") # Convert to string first as we cannot modify a datetime object
                    row["timestamp"] = ts_str[:3] + random.choice(corruption_letters) + ts_str[3:] # At position 3 we will insert some random letter in the timestamp

                    amount = str(row["transaction_amount"])
                    row["transaction_amount"] = amount[:5] + random.choice("abcdefgh") + amount[5:] # At position 5 we will insert some random letter in the transaction amount
                
                batch_data.append(row)
            
            writer.writerows(batch_data)


if __name__ == "__main__":
    generate_sample() # Execute the script with the main guard if needed directly for demonstrative purposes