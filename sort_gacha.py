import json

with open('json_files/gacha.json', 'r') as f:
    data = json.load(f)

# Group by teleporter
temp_dict = {}
for item in data:
    tp = item['teleporter']
    if tp not in temp_dict:
        temp_dict[tp] = []
    temp_dict[tp].append(item)

sorted_data = []
for tp, items in temp_dict.items():
    # Sort so 'right' comes before 'left'
    items_sorted = sorted(items, key=lambda x: 0 if x['side'] == 'right' else 1)
    sorted_data.extend(items_sorted)

with open('json_files/gacha.json', 'w') as f:
    json.dump(sorted_data, f, indent=4)
