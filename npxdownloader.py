from edgar import get_filings, set_identity
from datetime import datetime, timedelta
import os
import gzip
import time
import httpx
import asyncio


def download_npx_filings_year(year: int, path: str) -> None:
    filings = get_filings(year, form="N-PX")
    for filing in filings:
        filing.attachments.download(path)


def download_npx_filings_from_date(start_date, path):
    """
    Downloads NPX filings for the year specified in start_date

    Args:
        start_date: The date to start processing from
        path: The base path where files should be downloaded
    """
    # Get the year from start_date and set end_date to December 31st of that year
    year = start_date.year if isinstance(start_date, datetime) else start_date.year
    end_date = datetime(year, 12, 31).date()

    progress_file = "npx_download_progress.txt"
    total_filings_processed = 0

    # Convert start_date to date object if it's datetime
    current_date = start_date.date() if isinstance(start_date, datetime) else start_date

    # If progress file exists and has content, start from the last processed date + 1 day
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            last_processed = f.read().strip()
            if last_processed:  # Only process if file has content
                current_date = datetime.strptime(
                    last_processed, "%Y-%m-%d"
                ).date() + timedelta(days=1)
                print(f"Resuming from date: {current_date}")

    while current_date <= end_date:
        print(f"\nProcessing date: {current_date}")
        date_str = current_date.strftime("%Y-%m-%d")

        try:
            date_dir = os.path.join(path, date_str)
            os.makedirs(date_dir, exist_ok=True)

            filings_found = False
            filings = get_filings(filing_date=date_str, form="N-PX")
            if filings is not None:
                filings_list = list(filings)  # Convert generator to list to get count
                print(f"Found {len(filings_list)} filings for {date_str}")

                for filing in filings_list:
                    try:
                        filing_dir_name = f"{filing.cik}_{filing.company}"
                        filing_dir_name = "".join(
                            c for c in filing_dir_name if c.isalnum() or c in ["_", "-"]
                        )
                        filing_dir = os.path.join(date_dir, filing_dir_name)
                        os.makedirs(filing_dir, exist_ok=True)

                        try:
                            filing.attachments.download(filing_dir)
                            filings_found = True
                            total_filings_processed += 1
                            print(
                                f"Successfully downloaded filing for {filing.company} (CIK: {filing.cik})"
                            )
                        except gzip.BadGzipFile:
                            print(
                                f"Error downloading filing for {filing.company} (CIK: {filing.cik}): Bad gzip file"
                            )
                            continue
                        except httpx.HTTPError as e:
                            print(
                                f"HTTP Error downloading filing for {filing.company} (CIK: {filing.cik}): {str(e)}"
                            )
                            continue
                        except asyncio.TimeoutError:
                            print(
                                f"Timeout downloading filing for {filing.company} (CIK: {filing.cik})"
                            )
                            continue
                        except Exception as e:
                            print(
                                f"Error downloading filing for {filing.company} (CIK: {filing.cik}): {str(e)}"
                            )
                            continue
                    except Exception as e:
                        print(f"Error processing filing: {str(e)}")
                        continue
            else:
                print(f"No filings found for {current_date}")

            if not filings_found and os.path.exists(date_dir):
                try:
                    os.rmdir(date_dir)
                    print(f"Removed empty directory for {date_str}")
                except OSError:
                    pass

            # Record completion of this date
            with open(progress_file, "w") as f:
                f.write(current_date.strftime("%Y-%m-%d"))

        except Exception as e:
            print(f"Error processing date {current_date}: {str(e)}")
            continue

        print(f"Total filings processed so far: {total_filings_processed}")
        current_date += timedelta(days=1)

    print(f"\nFinal total of filings processed: {total_filings_processed}")


def download_npx_filings_quarter(path: str) -> None:
    filings = get_filings(quarter=1, form="N-PX")
    for filing in filings:
        filing.attachments.download(path)


def get_number_npx_filings(number_of_filings: int, year: int):
    filings = get_filings(filing_date="2024-01-01", form="N-PX")
    for i in range(0, number_of_filings):
        filing = filings[i]


if __name__ == "__main__":
    set_identity("Your Name your@email.com")
    start_date = datetime(2024, 1, 1)  # Example
    download_npx_filings_from_date(start_date=start_date, path="./files")
