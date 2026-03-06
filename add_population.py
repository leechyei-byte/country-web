import json

def main():
    with open('countries.json', 'r', encoding='utf-8') as f:
        countries = json.load(f)
        
    with open('restcountries.json', 'r', encoding='utf-8') as f:
        rest = json.load(f)
        
    pop_map = {}
    for r in rest:
        name = r.get('name', {}).get('common', '')
        if name:
            pop_map[name] = r.get('population', 0)
            
    for c in countries:
        name_en = c.get('name', {}).get('common', '')
        c['population'] = pop_map.get(name_en, -1)
        
    with open("countries.json", "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False, separators=(',', ':'))

    with open("data.js", "w", encoding="utf-8") as f:
        f.write("const countriesData = " + json.dumps(countries, ensure_ascii=False, separators=(',', ':')) + ";\n")
        
    print("Done adding population.")

if __name__ == '__main__':
    main()
