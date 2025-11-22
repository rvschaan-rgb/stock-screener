"""
PROJECT: Index of Company Tickers
PURPOSE: To download a complete list of company tickers
DATE: 11/22/2025
AUTHOR: Ralph Schaan

=============================
ORDER OF OPERATIONS (CHEAT SHEET)
=============================

[1] WHAT IS THE INPUT?
    company lists from SEC.gov (.json) file

[4] RULES / LOGIC?
    1. Download the .json file.
    2. Save the .json file to data folder

[5] WHAT LIBRARIES DO I NEED?
    requests - to make HTTP requests
    os - miscellaneous operating system interfaces
    json - encode and decode the JSON format

"""
# =======================================
#  IMPORTS
# =======================================

import requests
import os
import json

# =========================
# Helper Functions
# =========================

# SEC data URL
URL = "https://www.sec.gov/files/company_tickers.json"

# SEC requires a User-Agent
HEADERS = {
    "User-Agent": "Company_Tickers_Request/1.0 (contact: r.v.schaan@gmail.com)"
}

# Where to save the file
DESTINATION_FOLDER = r"C:\Users\rvsch\OneDrive\Desktop\coding_projects\stock_market\data"
FILENAME = "company_tickers.json"


def download_json_file(url, destination_folder, filename):

    file_path = os.path.join(destination_folder, filename)

    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()

        # Save the content to the file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Success: '{filename}' downloaded to:\n{file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")

# =======================================
#  MAIN FUNCTIONS
# =======================================

# Run the function

def main():

    download_json_file(URL, DESTINATION_FOLDER, FILENAME)

if __name__ == "__main__":
    main()