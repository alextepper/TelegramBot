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

    cell_width = 24.3 * cm
    cell_height = 3.3 * cm
    x_start = 1 * cm
    y_start = width - cell_height - 1 * cm

    for index, row in dataframe.iterrows():
        model_name = str(row.get("דגם", "N/A")).upper()
        color = str(row.get("צבע", "N/A")).upper()
        sole_thickness = str(row.get("עובי", "N/A"))
        price = str(row.get("מחיר", "N/A"))
        brand_name = str(row.get("מותג"))
        vegan = str(row.get("טבעוני", "No")).lower()
        grounding = str(row.get("הארקה", "No")).lower()  # New grounding column

        # Construct the path to the brand logo
        brand_logo_path = f"logos1/{brand_name}.png" if brand_name else None

        # Draw cell border
        c.setStrokeColor(colors.black)
        c.rect(x_start, y_start, cell_width, cell_height, stroke=1, fill=0)

        # Draw the brand logo on the left side with scaling if the file exists
        if brand_logo_path and os.path.exists(brand_logo_path):
            try:
                max_logo_width = 3.5 * cm
                max_logo_height = 2.8 * cm
                c.drawImage(
                    brand_logo_path,
                    x_start + 0.4 * cm,
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
        c.setFont("Poppins-Bold", 32)
        model_name_position = x_start + cell_width / 2
        c.drawCentredString(
            model_name_position, y_start + cell_height - 1.3 * cm, model_name
        )

        # Add vegan "V" icon in green if applicable, right after the model name
        vegan_icon_x = None
        if vegan in ["yes", "true", "1"]:
            try:
                vegan_icon_path = "logos1/VEGAN.png"  # Path to your VEGAN.png file
                # Calculate the width of the model name
                name_width = c.stringWidth(model_name, "Poppins-Bold", 36)
                # Position the vegan icon after the model name
                vegan_icon_x = model_name_position + name_width / 2 + 10
                c.drawImage(
                    vegan_icon_path,
                    vegan_icon_x,
                    y_start + cell_height - 1.4 * cm,
                    width=1.2 * cm,  # Adjust icon size here
                    height=1.2 * cm,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as e:
                print(f"Error loading vegan icon: {e}")

        # Add grounding icon next to the vegan icon if applicable
        if grounding in ["yes", "true", "1"] and vegan_icon_x:
            try:
                grounding_icon_path = (
                    "logos1/GROUNDING.png"  # Path to your GROUNDING.png file
                )
                # Position the grounding icon after the vegan icon
                grounding_icon_x = (
                    vegan_icon_x + 1.5 * cm
                )  # Adjust the space between the two icons
                c.drawImage(
                    grounding_icon_path,
                    grounding_icon_x,
                    y_start + cell_height - 1.4 * cm,
                    width=1.2 * cm,  # Adjust icon size here
                    height=1.2 * cm,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as e:
                print(f"Error loading grounding icon: {e}")

        # Calculate the total width of the color and sole thickness together
        c.setFont("Poppins-Bold", 22)
        color_width = c.stringWidth(f"{color}", "Poppins-Bold", 22)

        c.setFont("Poppins-Regular", 22)
        thickness_text = f" | {sole_thickness}mm"
        thickness_width = c.stringWidth(thickness_text, "Poppins-Regular", 22)

        # Total width of the combined text
        total_text_width = color_width + thickness_width

        # Calculate the starting point to center the combined text
        start_x = x_start + (cell_width - total_text_width) / 2

        # Draw the color in bold
        c.setFont("Poppins-Bold", 22)
        c.drawString(start_x, y_start + 0.7 * cm, f"{color}")

        # Draw the sole thickness in regular right after the color
        c.setFont("Poppins-Regular", 22)
        c.drawString(start_x + color_width, y_start + 0.7 * cm, thickness_text)

        # Draw the price on the right side of the cell using Poppins-Regular
        c.setFont("Poppins-Bold", 22)
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
