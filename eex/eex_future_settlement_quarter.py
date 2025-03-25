import requests
import json
import csv
import pandas as pd
from datetime import datetime, timedelta

# Base URL and headers
url = 'https://webservice-eex.gvsi.com/query/json/getChain/gv.pricesymbol/gv.displaydate/gv.expirationdate/tradedatetimegmt/gv.eexdeliverystart/ontradeprice/close/onexchsingletradevolume/onexchtradevolumeeex/offexchtradevolumeeex/openinterest/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': '*/*',
    'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Origin': 'https://www.eex.com',
    'DNT': '1',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://www.eex.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'Priority': 'u=0',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}

# Define start and finish dates
start_date = datetime.strptime('04.01.2024', '%d.%m.%Y')
finish_date = datetime.strptime('26.02.2025', '%d.%m.%Y')

# Number of iterations (for example, 12 months)
iterations = 500

# List to store all results
all_results = []

# List to store reformatted data for CSV
csv_data = []

# Dictionary to store data for Excel
excel_data = {}

# Mapping for quarter translation
quarter_mapping = {
    'F': 'Q1',
    'J': 'Q2',
    'N': 'Q3',
    'V': 'Q4'
}

on_date = start_date                            # on_date == trading date
expiration_date = on_date - timedelta(days=1)   # expiration_date is needed for http request

for i in range(iterations):
    if on_date > finish_date:
        break
    
    # Format dates
    expiration_date_str = expiration_date.strftime('%Y/%m/%d')
    on_date_str = on_date.strftime('%Y/%m/%d')
    
    # Parameters
    params = {
        'optionroot': '"/E.G0BQ"',
        'expirationdate': expiration_date_str,
        'onDate': on_date_str
    }
    
    # Make the request
    response = requests.get(url, headers=headers, params=params)
    
    # Calculate new expiration date and onDate
    expiration_date = expiration_date + timedelta(days=1)
    on_date = expiration_date + timedelta(days=1)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        # Append the results to the list
        all_results.extend(data['results']['items'])
        
        # Process each item for CSV and Excel
        for item in data['results']['items']:
            # Reformat gv.pricesymbol
            pricesymbol = item['gv.pricesymbol']
            quarter_char = pricesymbol[-3]  # Get the quarter character (J, N, V, F)
            year = pricesymbol[-2:]  # Get the last two digits (year)
            quarter = quarter_mapping.get(quarter_char, 'Unknown')  # Map to quarter
            reformatted_pricesymbol = f"{quarter} 20{year}"  # Format as "Qx yyyy"
            
            # Reformat tradedatetimegmt
            tradedatetimegmt = datetime.strptime(item['tradedatetimegmt'], '%m/%d/%Y %I:%M:%S %p')
            reformatted_tradedatetimegmt = tradedatetimegmt.strftime('%d.%m.%Y')
            
            # Get close value
            close = item['close']
            
            # Append to CSV data
            csv_data.append([reformatted_pricesymbol, reformatted_tradedatetimegmt, close])
            
            # Prepare data for Excel
            if reformatted_tradedatetimegmt not in excel_data:
                excel_data[reformatted_tradedatetimegmt] = {}
            excel_data[reformatted_tradedatetimegmt][reformatted_pricesymbol] = close
    else:
        print(f"Failed to fetch data for {expiration_date_str}: {response.status_code}")

# Write all results to a JSON file
with open('eex_data.json', 'w') as file:
    json.dump(all_results, file, indent=4)

# Write reformatted data to a CSV file
with open('eex_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(['Quarter', 'Trade Date', 'Close'])
    # Write data
    writer.writerows(csv_data)

# Create a DataFrame for Excel
df = pd.DataFrame.from_dict(excel_data, orient='index')

# Define custom sorting order for columns
def custom_sort_key(column):
    """Sort columns by year and then by quarter (Q1, Q2, Q3, Q4)."""
    quarter, year = column.split()
    year = int(year)
    quarter_order = {'Q1': 0, 'Q2': 1, 'Q3': 2, 'Q4': 3}
    return (year, quarter_order.get(quarter, 4))

# Sort columns using the custom sorting key
df = df.reindex(sorted(df.columns, key=custom_sort_key), axis=1)

# Convert the index (trade dates) to datetime for proper sorting
df.index = pd.to_datetime(df.index, format='%d.%m.%Y')

# Sort rows (trade dates) in ascending order
df = df.sort_index()

# Convert the index back to the original string format for readability
df.index = df.index.strftime('%d.%m.%Y')

# Write DataFrame to Excel
df.to_excel('eex_data.xlsx')

print("Data has been written to eex_data.json, eex_data.csv, and eex_data.xlsx")