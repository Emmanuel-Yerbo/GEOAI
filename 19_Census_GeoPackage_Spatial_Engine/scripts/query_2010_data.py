import requests
import json
import time

url = "https://statsbank.statsghana.gov.gh/api/v1/en/PHC2010/Population/ethnic_table.px"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Query payload
payload = {
  "query": [
    {
      "code": "Ethnicity",
      "selection": {
        "filter": "item",
        "values": ["Total"]
      }
    },
    {
      "code": "Education",
      "selection": {
        "filter": "item",
        "values": ["Total"]
      }
    },
    {
      "code": "Locality",
      "selection": {
        "filter": "item",
        "values": ["All Locality Types"]
      }
    },
    {
      "code": "Sex",
      "selection": {
        "filter": "item",
        "values": ["Both sexes"]
      }
    },
    {
      "code": "Age",
      "selection": {
        "filter": "item",
        "values": ["All ages"]
      }
    }
  ],
  "response": {
    "format": "json"
  }
}

print("Sending query to StatsBank with headers...")
try:
    res = requests.post(url, json=payload, headers=headers, timeout=30)
    if res.ok:
        data = res.json()
        print("Success! Data preview:")
        if isinstance(data, dict):
            print("Keys in response:", list(data.keys()))
            if "data" in data:
                print(f"Data rows count: {len(data['data'])}")
                print("First 10 rows:")
                print(json.dumps(data["data"][:10], indent=2))
        elif isinstance(data, list):
            print(f"List items count: {len(data)}")
            print("First 5 items:")
            print(json.dumps(data[:5], indent=2))
    else:
        print(f"Failed: {res.status_code}")
        print(res.text)
except Exception as e:
    print(f"Exception raised: {e}")
