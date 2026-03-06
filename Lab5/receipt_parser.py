import re
import json


def parse_receipt(x: str):
    items = []

    #pat to capture:
    #product name
    #quantity x price
    #total price
    pat = re.compile(
        r"\d+\.\s*(.+?)\n"          #product name
        r"(\d+),\d+\s*x\s*([\d\s]+,\d{2})\n"  #quantity x price
        r"([\d\s]+,\d{2})",         #total price
        re.MULTILINE
    )

    mat = pat.findall(x)

    for match in mat:
        name = match[0].strip()
        quantity = int(match[1])
        price_per_item = float(match[2].replace(" ", "").replace(",", "."))
        total_price = float(match[3].replace(" ", "").replace(",", "."))

        items.append({
            "name": name,
            "quantity": quantity,
            "price_per_item": price_per_item,
            "total_price": total_price
        })

    datetime_match = re.search(r"Время:\s*([\d\.]+\s+[\d:]+)", x)
    datetime_value = datetime_match.group(1) if datetime_match else None

    payment_match = re.search(r"(Банковская карта|Наличные|Карта)", x)
    payment_method = payment_match.group(1) if payment_match else None

    total_match = re.search(r"ИТОГО:\s*([\d\s]+,\d{2})", x)
    receipt_total = None
    if total_match:
        receipt_total = float(
            total_match.group(1).replace(" ", "").replace(",", ".")
        )

    return {
        "items": items,
        "datetime": datetime_value,
        "payment_method": payment_method,
        "receipt_total": receipt_total,
        "calculated_total": sum(item["total_price"] for item in items)
    }


with open("raw.txt", "r") as f:
    x = f.read()

parsed_data = parse_receipt(x)

with open("receipt_parsed.json", "w") as f:
    json.dump(parsed_data, f, indent=4, ensure_ascii=False)

print("done")