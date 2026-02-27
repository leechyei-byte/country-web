import json
import urllib.request
import time
from googletrans import Translator
import os
import sys

def update_capitals():
    print("Loading countries.json...")
    with open("countries.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Fetching capitals from GitHub...")
    req = urllib.request.Request('https://raw.githubusercontent.com/mledoze/countries/master/countries.json')
    resp = urllib.request.urlopen(req)
    rest_data = json.loads(resp.read())

    capital_map = {}
    for c in rest_data:
        name = c.get('name', {}).get('common', '')
        cap = c.get('capital', [])
        if name and cap:
            capital_map[name] = cap[0]

    translator = Translator()
    
    updated_count = 0
    for c in data:
        name_en = c.get('name', {}).get('common', '')
        # Fallback to translation if not in map
        capital_en = capital_map.get(name_en, '')
        
        if not capital_en:
            print(f"[{name_en}] has no capital.")
            c['capital_en'] = 'N/A'
            c['capital_zh'] = '無'
            continue
            
        try:
            # Sleep briefly to avoid Google Rate Limit
            if updated_count > 0 and updated_count % 10 == 0:
                time.sleep(0.5)
            res = translator.translate(capital_en, dest='zh-tw')
            capital_zh = res.text
        except Exception as e:
            print(f"Error translating {capital_en}: {e}")
            capital_zh = capital_en
            time.sleep(1)
            
        c['capital_en'] = capital_en
        c['capital_zh'] = capital_zh
        updated_count += 1
        
        if updated_count % 20 == 0:
            print(f"Processed {updated_count}/{len(data)} countries...")
            
    print("Saving countries.json...")
    with open("countries.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        
    print("Saving data.js...")
    with open("data.js", "w", encoding="utf-8") as f:
        f.write("const countriesData = " + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ";\n")
        
    print(f"Done! Updated {updated_count} countries.")

if __name__ == "__main__":
    update_capitals()
