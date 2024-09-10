import os
import pandas as pd
import io

# import telebot
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the Poppins font
pdfmetrics.registerFont(TTFont("Poppins-Bold", "fonts/Poppins-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Poppins-Regular", "fonts/Poppins-Regular.ttf"))

# BOT_TOKEN = os.environ.get("BOT_TOKEN")

# bot = telebot.TeleBot(BOT_TOKEN)


def process_csv(csv_data):
    try:
        dataframe = pd.read_csv(io.StringIO(csv_data))
        return dataframe
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return None


def generate_pdf(dataframe):
    pdf_file = io.BytesIO()
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4
    c.setPageSize((height, width))

    cell_width = 23.9 * cm
    cell_height = 3.4 * cm
    x_start = 1 * cm
    y_start = width - cell_height - 1 * cm

    for index, row in dataframe.iterrows():
        model_name = row.get("דגם", "N/A").upper()
        color = row.get("צבע", "N/A").upper()
        sole_thickness = row.get("עובי", "N/A")
        price = row.get("מחיר", "N/A")
        brand_name = row.get("מותג")
        vegan = row.get("טבעוני", "No")

        # Construct the path to the brand logo
        brand_logo_path = f"logos1/{brand_name}.png" if brand_name else None

        # Draw cell border
        c.setStrokeColor(colors.black)
        c.rect(x_start, y_start, cell_width, cell_height, stroke=1, fill=0)

        # Draw the brand logo on the left side with scaling if the file exists
        if brand_logo_path and os.path.exists(brand_logo_path):
            try:
                max_logo_width = 4 * cm
                max_logo_height = 2.8 * cm
                c.drawImage(
                    brand_logo_path,
                    x_start + 0.2 * cm,
                    y_start + 0.2 * cm,
                    width=max_logo_width,
                    height=max_logo_height,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as e:
                print(f"Error loading brand logo: {e}")
        else:
            # If logo does not exist, print the brand name as text
            c.setFont("Poppins-Bold", 15)
            c.drawString(
                x_start + 0.5 * cm, y_start + cell_height - 1.3 * cm, brand_name
            )

        # Draw the model name at the top center using Poppins-Bold
        c.setFont("Poppins-Bold", 36)
        model_name_position = x_start + cell_width / 2
        c.drawCentredString(
            model_name_position, y_start + cell_height - 1.3 * cm, model_name
        )

        # Add vegan "V" icon in green if applicable, right after the model name
        if vegan in ["yes", "true", "1"]:
            c.setFont("Poppins-Bold", 36)
            c.setFillColor(colors.green)
            v_position = (
                model_name_position
                + c.stringWidth(model_name, "Poppins-Bold", 36) / 2
                + 10
            )
            c.drawString(v_position, y_start + cell_height - 1.3 * cm, "V")
            c.setFillColor(colors.black)  # Reset the color back to black

        # Draw color and sole thickness at the bottom center using Poppins-Regular
        c.setFont("Poppins-Regular", 26)
        c.drawCentredString(
            x_start + cell_width / 2,
            y_start + 0.7 * cm,
            f"{color} | {sole_thickness}mm",
        )

        # Draw the price on the right side of the cell using Poppins-Regular
        c.setFont("Poppins-Regular", 26)
        c.drawRightString(
            x_start + cell_width - 0.5 * cm, y_start + 0.7 * cm, f"{price}"
        )

        x_start += cell_width  # Add some space between cells

        if x_start + cell_width > height - 1 * cm:
            x_start = 1 * cm
            y_start -= cell_height  # Move down for the next row

        if y_start < 1 * cm:
            c.showPage()
            x_start = 1 * cm
            y_start = width - cell_height - 1 * cm

    c.save()
    pdf_file.seek(0)  # Rewind the file to the beginning
    return pdf_file


# @bot.message_handler(commands=["start", "hello"])
# def send_welcome(message):
#     bot.reply_to(message, "Howdy, how are you doing?")


# @bot.message_handler(func=lambda msg: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)


# @bot.message_handler(content_types=["document"])
# def handle_document(message):
#     try:
#         file_info = bot.get_file(message.document.file_id)
#         file = bot.download_file(file_info.file_path)
#         dataframe = process_csv(file)
#         if dataframe is None:
#             bot.reply_to(message, "Failed to process CSV file.")
#             return

#         pdf = generate_pdf(dataframe)
#         bot.send_document(message.chat.id, pdf, visible_file_name="generated.pdf")
#     except Exception as e:
#         bot.reply_to(message, f"Error: {e}")


# bot.infinity_polling()
