from flask import Flask, request, send_file
import pandas as pd
from io import BytesIO
from bot import (
    generate_pdf,
)  # Replace with the actual module name where generate_pdf is defined

app = Flask(__name__)


@app.route("/")
def index():
    return "Welcome to the Shoe Model PDF Generator!"


@app.route("/generate", methods=["POST"])
def generate():
    file = request.files["file"]
    if not file:
        return "No file provided", 400

    # Convert the uploaded CSV to a DataFrame
    df = pd.read_csv(file)

    # Generate the PDF
    pdf = generate_pdf(df)

    # Return the PDF as a downloadable file
    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="shoe_models.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
