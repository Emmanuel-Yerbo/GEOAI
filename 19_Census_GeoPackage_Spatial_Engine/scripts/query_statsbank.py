import requests
import json

BASE_URL = "https://statsbank.statsghana.gov.gh/api/v1/en/"

def get_node(path=""):
    url = BASE_URL + path
    try:
        res = requests.get(url)
        if res.ok:
            return res.json()
        else:
            print(f"Error fetching path '{path}': {res.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching path '{path}': {e}")
        return None

# Traverse top level
top_level = get_node()
if top_level and isinstance(top_level, list):
    print("--- TOP LEVEL PORTALS ---")
    for item in top_level:
        item_id = item.get('id', 'N/A')
        item_type = item.get('type', 'N/A')
        item_text = item.get('text', 'N/A')
        print(f"ID: {str(item_id):<15} | Type: {str(item_type):<5} | Title: {item_text}")
        
    for item in top_level:
        item_id = item.get('id')
        item_text = item.get('text', '')
        if item_id and ('population' in item_text.lower() or 'census' in item_text.lower() or item_id in ['PHC', 'POP']):
            print(f"\n--- EXPLORING: {item_text} ({item_id}) ---")
            sub_level = get_node(item_id)
            if sub_level and isinstance(sub_level, list):
                for sub_item in sub_level[:30]:
                    sub_id = sub_item.get('id', 'N/A')
                    sub_type = sub_item.get('type', 'N/A')
                    sub_text = sub_item.get('text', 'N/A')
                    print(f"  SubID: {str(sub_id):<25} | Type: {str(sub_type):<5} | Title: {sub_text}")
                    # If it is a directory (type 'l'), let's explore it one level deeper
                    if sub_type == 'l':
                        sub_sub = get_node(f"{item_id}/{sub_id}")
                        if sub_sub and isinstance(sub_sub, list):
                            for sse in sub_sub[:10]:
                                sse_id = sse.get('id', 'N/A')
                                sse_type = sse.get('type', 'N/A')
                                sse_text = sse.get('text', 'N/A')
                                print(f"    SSeID: {str(sse_id):<30} | Type: {str(sse_type):<5} | Title: {sse_text}")
else:
    print("Top level node returned invalid format:", top_level)
