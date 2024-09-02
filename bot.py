import os
import pandas as pd
import io
import telebot
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)


def process_csv(file):
    """
    Receives a CSV file, processes it, and returns a DataFrame.

    :param file: The CSV file to process (in-memory file).
    :return: DataFrame containing the processed data.
    """
    try:
        # Convert the file content to a DataFrame
        dataframe = pd.read_csv(io.StringIO(file.decode("utf-8")))
        return dataframe
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return None


def generate_pdf(dataframe):
    """
    Generates a landscape A4 PDF with 4 cells per page, each representing a shoe model.

    :param dataframe: DataFrame containing the data to include in the PDF.
    :return: The PDF file as a BytesIO object.
    """
    pdf_file = io.BytesIO()
    c = canvas.Canvas(pdf_file, pagesize=A4)

    # Set the PDF to landscape
    width, height = A4
    c.setPageSize((height, width))

    # Define cell dimensions and starting positions
    cell_width = 25 * cm
    cell_height = 4 * cm
    x_start = 1 * cm
    y_start = width - cell_height - 1 * cm  # Start from top

    for index, row in dataframe.iterrows():
        model_name = row.get("Model Name", "N/A")
        color = row.get("Color", "N/A")
        sole_thickness = row.get("Sole Thickness", "N/A")
        price = row.get("Price", "N/A")
        brand_logo = row.get("Brand Logo URL")
        vegan = row.get("Vegan", "No")

        # Debug print statements
        print(f"Processing {model_name}, Vegan: {vegan}, Logo: {brand_logo}")

        # Draw cell border
        c.setStrokeColor(colors.black)
        c.rect(x_start, y_start, cell_width, cell_height, stroke=1, fill=0)

        # Draw the brand logo on the left side with scaling
        if brand_logo:
            try:
                # Desired maximum dimensions for the logo
                max_logo_width = 4 * cm
                max_logo_height = 3 * cm

                # Draw the image directly with preserveAspectRatio
                c.drawImage(
                    brand_logo,
                    x_start + 0.5 * cm,
                    y_start + 0.5 * cm,
                    width=max_logo_width,
                    height=max_logo_height,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as e:
                print(f"Error loading brand logo: {e}")

        # Draw the model name at the top center
        c.setFont("Helvetica-Bold", 36)
        model_name_position = x_start + cell_width / 2
        c.drawCentredString(
            model_name_position, y_start + cell_height - 1.8 * cm, model_name
        )

        # Add vegan "V" icon in green if applicable, right after the model name
        if vegan.lower() in ["yes", "true", "1"]:
            c.setFont("Helvetica-Bold", 36)
            c.setFillColor(colors.green)
            v_position = (
                model_name_position
                + c.stringWidth(model_name, "Helvetica-Bold", 36) / 2
                + 10
            )
            c.drawString(v_position, y_start + cell_height - 1.8 * cm, "V")
            c.setFillColor(colors.black)  # Reset the color back to black

        # Draw color and sole thickness at the bottom center
        c.setFont("Helvetica", 26)
        c.drawCentredString(
            x_start + cell_width / 2,
            y_start + 1 * cm,
            f"{color} | {sole_thickness}mm",
        )

        # Draw the price on the right side of the cell
        c.setFont("Helvetica-Bold", 36)
        c.drawRightString(
            x_start + cell_width - 0.5 * cm, y_start + 1 * cm, f"${price}"
        )

        # Move to the next cell
        x_start += cell_width  # Add some space between cells

        # Check if the next cell would go out of the page
        if x_start + cell_width > height - 1 * cm:
            x_start = 1 * cm
            y_start -= cell_height + 1 * cm  # Move down for the next row

        # Check if we're out of space on the page
        if y_start < 1 * cm:
            c.showPage()
            x_start = 1 * cm
            y_start = width - cell_height - 1 * cm

    c.save()
    pdf_file.seek(0)  # Rewind the file to the beginning
    return pdf_file


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)


@bot.message_handler(content_types=["document"])
def handle_document(message):
    try:
        # Download the file from Telegram
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        print(f"Received file: {file_info.file_path}")

        # Process the CSV file
        dataframe = process_csv(file)
        print(f"Processed CSV file: {dataframe}")
        if dataframe is None:
            bot.reply_to(message, "Failed to process CSV file.")
            return

        # Generate the PDF
        pdf = generate_pdf(dataframe)
        print("Generated PDF")

        # Send the PDF back to the user
        bot.send_document(message.chat.id, pdf, visible_file_name="generated.pdf")

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


bot.infinity_polling()
