import requests
import re
from datetime import datetime
import csv
import os

def parse_date(date_str, year):
    date_str = date_str.replace("-1,", ".")
    date_obj = datetime.strptime(f"{year}.{date_str}", "%Y.%m.%d")
    return date_obj.strftime("%d.%m.%Y")

def extract_data(js_data):
    pattern = re.compile(r"type: 'line', name:'\d{4}[\S\s]*}];")
    match = pattern.search(js_data)
    if not match:
        return {}

    line_data = re.split("},{", match.group(0))
    results = {}
    for entry in line_data:
        year_match = re.search(r"name:'(\d{4})", entry)
        if not year_match:
            continue

        year = year_match.group(1)
        dates = re.finditer(r"Date\.UTC\(1972,(.+?)\)", entry)
        values = re.finditer(r"[\s,](\d+?\.?\d+?)[],]", entry)

        for date, value in zip(dates, values):
            date_str = parse_date(date.group(1), year)
            # Replace dot with comma for decimal separator
            formatted_value = value.group(1).replace(".", ",")
            if year not in results:
                results[year] = []
            results[year].append([date_str, formatted_value])

    return results

def write_to_csv(year, data):
    filename = f"{year}_tecson.csv"
    filename = os.path.join(os.path.dirname(__file__), filename)
    file_exists = os.path.isfile(filename)

    # Read existing data if file exists
    existing_data = []
    if file_exists:
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter="\t")
            existing_data = [row for row in reader]

    # Compare existing data with new data
    if existing_data[1::] != data:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow(["Date", "Value"])  # Write header
            writer.writerows(data)
        print(f"Updated {filename}")
    else:
        print(f"No changes detected for {filename}. Skipping update.")

def main():
    url = 'https://www.tecson.de/system/modules/pepesale_chart/html/chart_config_desktop_1.js'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        return

    js_data = response.text
    results = extract_data(js_data)

    for year, data in results.items():
        write_to_csv(year, data)

if __name__ == "__main__":
    main()