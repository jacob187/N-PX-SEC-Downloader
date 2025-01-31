from edgar import get_filings, set_identity
from datetime import datetime, timedelta
import os


def download_npx_filings_year(year: int, path: str) -> None:
    """Download all N-PX filings in a year

    Args:
        year (int): Int of year
        path (str): The directory to download the file
    """
    filings = get_filings(year, form="N-PX")
    for filing in filings:
        filing.attachments.download(path)


def download_npx_filings_from_date(start_date, path) -> None:
    """
    Downloads NPX filings starting from a specific date through end of 2024

    Args:
        start_date: The date to start processing from
        path: The base path where files should be downloaded
    """
    end_date = datetime(2024, 12, 31).date()
    progress_file = "npx_download_progress.txt"

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

    while current_date <= end_date:
        print(f"Processing date: {current_date}")
        date_str = current_date.strftime("%Y-%m-%d")

        # Create directory for current date
        date_dir = os.path.join(path, date_str)
        os.makedirs(date_dir, exist_ok=True)

        filings_found = False
        filings = get_filings(filing_date=date_str, form="N-PX")
        if filings is not None:
            for filing in filings:
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
                    except gzip.BadGzipFile:
                        print(
                            f"Error downloading filing for {filing.company} (CIK: {filing.cik}): Bad gzip file"
                        )
                        continue
                    except Exception as e:
                        print(
                            f"Error downloading filing for {filing.company} (CIK: {filing.cik}): {str(e)}"
                        )
                        continue
                except Exception as e:
                    print(
                        f"Error processing filing {filing.company}, {filing.cik}: {str(e)}"
                    )
                    continue
        else:
            print(f"No filings found for {current_date}")

        # Delete the date directory if no filings were added
        if not filings_found and os.path.exists(date_dir):
            try:
                os.rmdir(date_dir)
                print(f"Removed empty directory for {date_str}")
            except OSError:
                pass

        # Record completion of this date
        with open(progress_file, "w") as f:
            f.write(current_date.strftime("%Y-%m-%d"))

        current_date += timedelta(days=1)


def download_npx_filings_quarter(path: str) -> None:
    filings = get_filings(quarter=1, form="N-PX")
    for filing in filings:
        filing.attachments.download(path)


if __name__ == "__main__":
    set_identity("Your Name your@email.com")
    start_date = datetime(2024, 1, 1)  # Example
    download_npx_filings_from_date(start_date=start_date, path="./files")
