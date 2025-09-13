import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import io, zipfile

# Direct page with CSV listings
BASE_URL = "https://mempool-dumpster.flashbots.net/ethereum/mainnet/2025-09/index.html"

def fetch_csv():
    # Step 1: Open index page
    resp = requests.get(BASE_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Step 2: Get all <a> links ending in ".csv.zip"
    csv_files = [a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".csv.zip")]

    if not csv_files:
        raise Exception("No CSV files found!")

    # Step 3: Pick the 2nd last CSV (or last if fewer than 3)
    target_csv = csv_files[-1] if len(csv_files) >= 3 else csv_files[-1]
    csv_url = urljoin(BASE_URL, target_csv)
    print(f"Downloading: {csv_url}")

    # Step 4: Download and unzip directly into pandas
    r = requests.get(csv_url)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    csv_name = z.namelist()[0]   # assume only 1 CSV inside
    df = pd.read_csv(z.open(csv_name))

    # Step 5: Save CSV locally
    local_filename = csv_name  # you can also rename it here if you want
    df.to_csv(local_filename, index=False)
    print(f"CSV saved locally as {local_filename}")

    return df, csv_url


if __name__ == "__main__":
    df, url = fetch_csv()
    print(f"CSV loaded from {url}")
    print(df.head())
