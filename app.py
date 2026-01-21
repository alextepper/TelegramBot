from flask import Flask, request, send_file
import pandas as pd
from bot import (
    generate_children_pdf,
    generate_kids_pdf,
    generate_mixed_pdf,
    process_csv,
    generate_pdf,
    convert_csv_format,
)  # Import your existing functions

app = Flask(__name__)


def _normalize_bool(value):
    return str(value).strip().lower() in ["yes", "true", "1"]


def _normalize_str(value, default="N/A"):
    if value is None:
        return default
    text = str(value)
    return text if text.strip() != "" else default


def _parse_kids_price_ranges(price_value):
    if price_value is None:
        return []
    if isinstance(price_value, (int, float)):
        return []
    price_text = str(price_value).strip()
    if not price_text:
        return []
    parts = [part.strip() for part in price_text.split(";") if part.strip()]
    size_prices = []
    for part in parts:
        if ":" not in part:
            continue
        size_range, price = part.split(":", 1)
        size_prices.append((size_range.strip(), price.strip()))
    return size_prices


def _build_rows_from_items(items):
    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue

        base_row = {
            "דגם": _normalize_str(item.get("דגם")),
            "מותג": _normalize_str(item.get("מותג")),
            "צבע": _normalize_str(item.get("צבע")),
            "עובי": _normalize_str(item.get("עובי")),
            "טבעוני": _normalize_str(item.get("טבעוני"), default="NO"),
            "הארקה": _normalize_str(item.get("הארקה"), default="NO"),
        }

        is_kids = _normalize_bool(item.get("ילדים", "NO"))
        discount_value = item.get("הנחה")

        if is_kids:
            row = dict(base_row)
            row["ילדים"] = "YES"
            row["הנחה"] = (
                "N/A" if discount_value in (None, "", "nan") else discount_value
            )

            size_prices = _parse_kids_price_ranges(item.get("מחיר"))
            for index, (size_range, price) in enumerate(size_prices[:4], 1):
                row[f"מידות{index}"] = size_range
                row[f"מחיר{index}"] = price

            rows.append(row)
        else:
            row = dict(base_row)
            row["ילדים"] = "NO"
            row["מחיר"] = item.get("מחיר", "")
            row["הנחה"] = (
                "nan" if discount_value in (None, "", "nan") else discount_value
            )
            rows.append(row)

    return rows


@app.route("/handle_csv", methods=["POST"])
def handle_csv():
    csv_data = request.form.get("data")
    if not csv_data:
        return "No CSV data received", 400

    dataframe = process_csv(csv_data)
    if dataframe is None:
        return "Failed to process CSV", 400

    pdf = generate_pdf(dataframe)

    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="generated.pdf",
    )


@app.route("/handle_items", methods=["POST"])
def handle_items():
    items = request.get_json(silent=True)
    if not isinstance(items, list):
        return "Expected a JSON array of items", 400

    rows = _build_rows_from_items(items)
    if not rows:
        return "No valid items found", 400

    pdf = generate_mixed_pdf(rows)
    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="price_tags.pdf",
    )


@app.route("/handle_csv_children", methods=["POST"])
def handle_csv_children():
    csv_data = request.form.get("data")
    if not csv_data:
        return "No CSV data received", 400

    dataframe = process_csv(csv_data)
    if dataframe is None:
        return "Failed to process CSV", 400

    pdf = generate_kids_pdf(dataframe)

    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="generated.pdf",
    )


@app.route("/generate_price_tags", methods=["POST"])
def generate_price_tags():
    """Endpoint to generate both regular and children price tag PDFs from CSV data."""
    csv_data = request.form.get("data")
    if not csv_data:
        return "No CSV data received", 400

    # Process the CSV
    original_dataframe = process_csv(csv_data)
    if original_dataframe is None:
        return "Failed to process CSV", 400

    # Convert to Hebrew format
    hebrew_dataframe = convert_csv_format(original_dataframe)

    # Separate regular and children items
    regular_items = []
    children_items = []

    for index, row in original_dataframe.iterrows():
        hebrew_row = hebrew_dataframe.iloc[index]

        # Check if it has size ranges (children with size ranges)
        import json

        price = str(row.get("price", ""))
        try:
            price_data = json.loads(price)
            if isinstance(price_data, list):
                children_items.append(hebrew_row)
            else:
                regular_items.append(hebrew_row)
        except (json.JSONDecodeError, ValueError, TypeError):
            regular_items.append(hebrew_row)

    # Generate PDFs based on which lists have items
    if regular_items and children_items:
        # If both exist, we'll prioritize regular for now
        regular_df = pd.DataFrame(regular_items)
        pdf = generate_pdf(regular_df)
        return send_file(
            pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="regular_price_tags.pdf",
        )
    elif regular_items:
        regular_df = pd.DataFrame(regular_items)
        pdf = generate_pdf(regular_df)
        return send_file(
            pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="regular_price_tags.pdf",
        )
    elif children_items:
        children_df = pd.DataFrame(children_items)
        pdf = generate_children_pdf(children_df)
        return send_file(
            pdf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="children_price_tags.pdf",
        )
    else:
        return "No valid items found in CSV", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
