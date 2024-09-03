from flask import Flask, request, send_file
from bot import process_csv, generate_pdf  # Import your existing functions

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
