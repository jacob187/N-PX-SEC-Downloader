from edgar import get_filings, set_identity
from datetime import datetime, timedelta
import os
import gzip
import time
import httpx
import asyncio
import ssl


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
    year = start_date.year if isinstance(start_date, datetime) else start_date.year
    end_date = datetime(year, 12, 31).date()

    progress_file = "npx_download_progress.txt"
    error_log_file = "npx_download_errors.txt"

    # Create files if they don't exist
    if not os.path.exists(progress_file):
        open(progress_file, "w").close()
    if not os.path.exists(error_log_file):
        open(error_log_file, "w").close()

    total_filings_processed = 0

    current_date = start_date.date() if isinstance(start_date, datetime) else start_date

    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            last_processed = f.read().strip()
            if last_processed:
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
                filings_list = list(filings)
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
                        except (
                            gzip.BadGzipFile,
                            httpx.HTTPError,
                            asyncio.TimeoutError,
                            ssl.SSLError,
                        ) as e:
                            error_msg = (
                                f"{date_str},{filing.cik},{filing.company},{str(e)}"
                            )
                            print(f"Error downloading filing: {error_msg}")
                            # Log error to file
                            with open(error_log_file, "a") as f:
                                f.write(f"{error_msg}\n")
                            time.sleep(5)  # Longer delay after error
                            continue
                        except Exception as e:
                            error_msg = (
                                f"{date_str},{filing.cik},{filing.company},{str(e)}"
                            )
                            print(f"Error downloading filing: {error_msg}")
                            # Log error to file
                            with open(error_log_file, "a") as f:
                                f.write(f"{error_msg}\n")
                            continue
                    except Exception as e:
                        error_msg = f"{date_str},{filing.cik},{filing.company},Processing error: {str(e)}"
                        print(f"Error processing filing: {error_msg}")
                        with open(error_log_file, "a") as f:
                            f.write(f"{error_msg}\n")
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
            error_msg = f"{date_str},NA,NA,Date processing error: {str(e)}"
            print(f"Error processing date: {error_msg}")
            with open(error_log_file, "a") as f:
                f.write(f"{error_msg}\n")
            continue

        print(f"Total filings processed so far: {total_filings_processed}")
        current_date += timedelta(days=1)

    print(f"\nFinal total of filings processed: {total_filings_processed}")


if __name__ == "__main__":
    # This is required for the SEC as the request header
    set_identity("Your Name your@email.com")
    start_date = datetime(
        2024, 1, 1
    )  # Example, change the first parameter to the desired year
    download_npx_filings_from_date(start_date=start_date, path="./files")
