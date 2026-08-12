import json

with open("tenders.jsonl", encoding="utf-8") as f:
    text = f.read()

decoder = json.JSONDecoder()
records, i = [], 0
while i < len(text):
    while i < len(text) and text[i].isspace():
        i += 1
    if i >= len(text):
        break
    obj, i = decoder.raw_decode(text, i)   # reads one object, returns where it ended
    records.append(obj)

print("records:", len(records))
print("unique tender_id:", len({r["tender_id"] for r in records}))
