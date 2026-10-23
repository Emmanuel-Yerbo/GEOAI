import requests
import json

url = "https://data.humdata.org/api/3/action/package_search?q=ghana+population&rows=40"
res = requests.get(url)
if res.ok:
    results = res.json().get("result", {}).get("results", [])
    print(f"Found {len(results)} packages:")
    for p in results:
        name = p.get("name", "")
        title = p.get("title", "")
        print(f"  ID: {name:<30} | Title: {title}")
else:
    print(f"Error: {res.status_code}")
