import requests

# Read the test CSV data
with open("test_data.csv", "r", encoding="utf-8") as f:
    csv_data = f.read()

# Send POST request to the endpoint
url = "http://localhost:5000/generate_price_tags"
response = requests.post(url, data={"data": csv_data})

# Check if request was successful
if response.status_code == 200:
    # Save the PDF
    with open("output.pdf", "wb") as f:
        f.write(response.content)
    print("✓ PDF generated successfully! Saved as output.pdf")
else:
    print(f"✗ Error: {response.status_code}")
    print(response.text)
