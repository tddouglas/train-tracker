from datetime import datetime, timezone
import sys
import requests as r
from bs4 import BeautifulSoup
from IPython.display import display
import pandas as pd

# Change imported DB connection to modify which DB I write to
# from db_connector_local import upsert_train_entry
from db_connector_supabase import upsert_train_entry


# Use Amtrak API to get train data - https://github.com/piemadd/Piero-Amtrak-API-Docs
def get_amtrak_update():
    pass


# Function to extract data from rows
def extract_train_info(soup):
    trains = []
    rows = soup.find_all('tr', class_='amtrak-header-row')
    for row in rows:
        time = row.find('td').get_text().strip()
        train_number = row.find('span', class_='train-number').get_text().strip()
        train_name = row.find('span', class_='train-name').get_text().strip()
        destination_row = row.find_next_sibling('tr', class_='amtrak-destination')
        destination = destination_row.find('span', class_='pill-destination').get_text().strip()
        status = destination_row.find('span', class_='pill-status').get_text().strip()
        track = destination_row.find('td', class_='track-cell').get_text().strip() if destination_row.find('td',
                                                                                                           class_='track-cell') else 'N/A'

        trains.append({
            'time': time,
            'train_number': train_number,
            'train_name': train_name,
            'destination': destination,
            'status': status,
            'track': track
        })

    return trains


def get_nyc_trains():
    url = 'https://moynihantrainhall.nyc/transportation/#amtrak'
    headers = {
        'User-Agent': 'curl/8.7.1',
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        res = r.post(url, headers=headers, timeout=15)
    except r.exceptions.ReadTimeout:
        raise r.exceptions.ReadTimeout(
            "Request timed out")  # Re-throwing request for monitoring purposes to see how frequently it happens. Ideally will gracefully handle these failures once they are less frequent.
        # print("⚠️ Request timed out. Skipping this run...")

    if res.status_code == 200:
        res_soup = BeautifulSoup(res.text, 'html.parser')
        # print(res_soup)

        departures_html = res_soup.find(id='amtrak-departures-target')
        departures_info = extract_train_info(departures_html)

        arrivals_html = res_soup.find(id='amtrak-arrivals-target')
        arrivals_info = extract_train_info(arrivals_html)

        last_update = res_soup.select_one('.last-update-amtrak').text

        # print(departures_info, arrivals_info, last_update)

        df_departures = pd.DataFrame(departures_info)
        df_arrivals = pd.DataFrame(arrivals_info)
        # pd.set_option('display.max_columns', None)  # Show all columns
        # pd.set_option('display.width', 1000)  # Increase display width to prevent wrapping
        # pd.set_option('display.colheader_justify', 'left')  # Optional: Align headers for better readability
        # print(f"Departures - {last_update}:")
        # display(df_departures)
        #
        # print(f"\nArrivals - {last_update}:")
        # display(df_arrivals)

        for train in departures_info:
            upsert_train_entry(train, 'trains_departures')
        for train in arrivals_info:
            upsert_train_entry(train, 'trains_arrivals')
    else:
        print(f"Request failed with status code: {res.status_code}")


if __name__ == "__main__":
    # Get current UTC hour
    current_hour = datetime.now(timezone.utc).hour
    # print(f"Current hour: {current_hour}")

    # Skip execution between 2 AM - 5 AM ET (time in UTC)
    if 7 <= current_hour <= 10:
        print("Skipping execution: Between 2 AM - 5 AM ET")
        sys.exit(0)  # Exit script safely

    # Your main script logic here
    # print("Running script normally...")
    get_nyc_trains()
