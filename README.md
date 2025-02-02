# Download SEC N-PX Filings

This repo contains `npxdownloader.py` which allows you to download all SEC N-PX filings for a given year. It leverages the exhaustive [edgartools](https://github.com/dgunning/edgartools/) library. Refer to the comments in the main function to run the `download_npx_filings_from_date`.

## Installation

- Ensure Python 3.9+ is installed
- Install the dependencies:

  `pip install -r requirements.txt`

- Create files to track download date progress and errors.

  `touch npx_download_errors.txt npx_download_progress.txt`

- Adjust SEC header identifier `set_identity()`, and change the function call in the main function for desired outcome.
- If you want to save the files in the same directory as this project, create a files directory as it is in the `.gitignore`
