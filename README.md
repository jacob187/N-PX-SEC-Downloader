# Download SEC N-PX Filings

This repo contains `npxdownloader.py` which allows you to download all SEC N-PX filings for a given year. It leverages the exhaustive [edgartools](https://github.com/dgunning/edgartools/) library. Refer to the comments in the main function to run the `download_npx_filings_from_date`.

## Installation

- Ensure Python 3.11+ is installed.
- Install the dependencies:

  `pip install -r requirements.txt`

- Create a .env file and add your SEC header identifier to the varaible `SEC_HEADER` and the download to the variable `NPX_DOWNLOAD_PATH`. See .env.example.
- If you want to save the files in the same directory as this project, create a files directory as it is in the `.gitignore`.
