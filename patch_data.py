import json

def patch_data():
    with open("countries.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for c in data:
        name_en = c.get('name', {}).get('common', '')
        
        # Check and fix translations
        zho_common = c.get('translations', {}).get('zho', {}).get('common', '')
        if "麥當勞" in zho_common:
            c['translations']['zho']['common'] = zho_common.replace("麥當勞", "麥克唐納")
        
        # Patch capitals
        if name_en == "Turkey" or name_en == "Türkiye":
            c['capital_en'] = "Ankara"
            c['capital_zh'] = "安卡拉"
        elif name_en == "Macau":
            c['capital_en'] = "Macau"
            c['capital_zh'] = "澳門"
        elif name_en == "Republic of the Congo" or name_en == "Congo":
            c['capital_en'] = "Brazzaville"
            c['capital_zh'] = "布拉柴維爾"
        elif name_en in ["Heard Island and McDonald Islands", "Bouvet Island", "Antarctica", "United States Minor Outlying Islands"]:
            c['capital_en'] = "None"
            c['capital_zh'] = "無常駐首都"

    with open("countries.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    with open("data.js", "w", encoding="utf-8") as f:
        f.write("const countriesData = " + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ";\n")

if __name__ == "__main__":
    patch_data()
