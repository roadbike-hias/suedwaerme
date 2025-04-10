import os
import requests
import csv
from datetime import datetime

# Hardcoded variables
chartstartdate = "2025/03/31"
chartstopdate = "2025/04/29"
filename = os.path.join(os.path.dirname(__file__), "egix_month.csv")

# URL and headers
url = "https://webservice-eex.gvsi.com/query/json/getDaily/close/tradedatetimegmt/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Accept": "*/*",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://www.eex.com",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site",
    "Priority": "u=0",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Referer": "https://www.eex.com/"
}

# Parameters
params = {
    "priceSymbol": '"$E.EGIX.M.THE"',
    "chartstartdate": chartstartdate,
    "chartstopdate": chartstopdate,
    "dailybarinterval": "Days",
    "aggregatepriceselection": "First"
}

# Make the request
response = requests.get(url, headers=headers, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    
    # Process the data
    formatted_data = []
    for item in data["results"]["items"]:
        # Format the date
        trade_date = datetime.strptime(item["tradedatetimegmt"], "%m/%d/%Y %I:%M:%S %p")
        formatted_date = trade_date.strftime("%d.%m.%Y")
        
        # Format the close value (replace dot with comma, no quotation marks)
        close_value = str(item["close"]).replace(".", ",")
        
        # Append to the list
        formatted_data.append([close_value, formatted_date])
    
    # Save to a CSV file with tab as delimiter
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        # Write the header
        writer.writerow(["EGIX Month", "Trading Day"])
        # Write the data
        writer.writerows(formatted_data)
    
    print("Data saved to egix_month.csv")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")