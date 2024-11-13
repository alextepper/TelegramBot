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

from utils import (
    draw_kids_discount_price_tag,
    draw_kids_price_tag,
    draw_price_tag,
    draw_discount_price_tag,
)

# Register the Poppins font
pdfmetrics.registerFont(TTFont("Poppins-Bold", "fonts/Poppins-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Poppins-Regular", "fonts/Poppins-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Montserrat-Bold", "fonts/Montserrat-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Montserrat-SemiBold", "fonts/Montserrat-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Montserrat-Regular", "fonts/Montserrat-Regular.ttf"))

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
        # Set the stroke color to light grey
        light_grey = colors.Color(0.85, 0.85, 0.85)  # RGB values for light grey
        c.setStrokeColor(light_grey)

        # Set the line style to dotted
        c.setDash(1, 2)  # 1 unit on, 2 units off for a dotted line pattern

        # Draw the cell border with the new settings
        c.rect(x_start, y_start, cell_width, cell_height, stroke=1, fill=0)

        # Reset the line settings for the rest of the content
        c.setDash([])

        discount = str(row.get("הנחה", "N/A"))
        # Draw the price tag content
        if discount == "nan":
            draw_price_tag(c, x_start, y_start, cell_width, cell_height, row)
        else:
            draw_discount_price_tag(c, x_start, y_start, cell_width, cell_height, row)

        # Move to the next cell or next page if necessary
        x_start += cell_width  # Move to the next cell
        if (
            x_start + cell_width > height - 1 * cm
        ):  # Check if the next cell fits on the current row
            x_start = 1 * cm
            y_start -= cell_height + 1 * cm  # Move to the next row

        if y_start < 1 * cm:  # Check if we need to move to the next page
            c.showPage()
            x_start = 1 * cm
            y_start = width - cell_height - 1 * cm

    c.save()
    pdf_file.seek(0)  # Rewind the file to the beginning
    return pdf_file


def generate_kids_pdf(dataframe):
    pdf_file = io.BytesIO()
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4
    c.setPageSize((height, width))

    cell_width = 24.3 * cm
    cell_height = 3.3 * cm
    x_start = 1 * cm
    y_start = width - cell_height - 1 * cm

    for index, row in dataframe.iterrows():
        # Set the stroke color to light grey
        light_grey = colors.Color(0.85, 0.85, 0.85)  # RGB values for light grey
        c.setStrokeColor(light_grey)

        # Set the line style to dotted
        c.setDash(1, 2)  # 1 unit on, 2 units off for a dotted line pattern

        # Draw the cell border with the new settings
        c.rect(x_start, y_start, cell_width, cell_height, stroke=1, fill=0)

        # Reset the line settings for the rest of the content
        c.setDash([])

        discount = str(row.get("הנחה", "N/A"))
        # Draw the price tag content
        if discount == "N/A":
            draw_kids_price_tag(c, x_start, y_start, cell_width, cell_height, row)
        else:
            draw_kids_discount_price_tag(
                c, x_start, y_start, cell_width, cell_height, row
            )

        # Move to the next cell or next page if necessary
        x_start += cell_width  # Move to the next cell
        if (
            x_start + cell_width > height - 1 * cm
        ):  # Check if the next cell fits on the current row
            x_start = 1 * cm
            y_start -= cell_height + 1 * cm  # Move to the next row

        if y_start < 1 * cm:  # Check if we need to move to the next page
            c.showPage()
            x_start = 1 * cm
            y_start = width - cell_height - 1 * cm

    c.save()
    pdf_file.seek(0)  # Rewind the file to the beginning
    return pdf_file


def generate_children_pdf(dataframe):
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
        grounding = str(row.get("הארקה", "No")).lower()

        # Construct the path to the brand logo
        brand_logo_path = f"logos1/{brand_name}.png" if brand_name else None

        # Draw cell border
        c.setStrokeColor(colors.black)
        c.setDash(1, 3)
        c.rect(x_start, y_start, cell_width, cell_height, stroke=1, fill=0)

        # Draw the brand logo on the left side with scaling if the file exists
        if brand_logo_path and os.path.exists(brand_logo_path):
            try:
                max_logo_width = 3.5 * cm
                max_logo_height = 2.5 * cm
                c.drawImage(
                    brand_logo_path,
                    x_start + 0.4 * cm,
                    y_start + 0.4 * cm,
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
        model_name_position = x_start + cell_width / 2 - 1 * cm
        c.drawCentredString(
            model_name_position, y_start + cell_height - 1.3 * cm, model_name
        )

        # Add vegan "V" icon in green if applicable, right after the model name
        vegan_icon_x = None
        if vegan in ["yes", "true", "1"]:
            try:
                vegan_icon_path = "logos1/VEGAN.png"  # Path to your VEGAN.png file
                name_width = c.stringWidth(model_name, "Poppins-Bold", 36)
                vegan_icon_x = model_name_position + name_width / 2 + 10
                c.drawImage(
                    vegan_icon_path,
                    vegan_icon_x,
                    y_start + cell_height - 1.4 * cm,
                    width=1.2 * cm,
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
                grounding_icon_x = vegan_icon_x + 1.5 * cm
                c.drawImage(
                    grounding_icon_path,
                    grounding_icon_x,
                    y_start + cell_height - 1.4 * cm,
                    width=1.2 * cm,
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
        start_x = x_start + (cell_width - total_text_width) / 2 - 1 * cm

        # Draw the color in bold
        c.setFont("Poppins-Bold", 22)
        c.drawString(start_x, y_start + 0.7 * cm, f"{color}")

        # Draw the sole thickness in regular right after the color
        c.setFont("Poppins-Regular", 22)
        c.drawString(start_x + color_width, y_start + 0.7 * cm, thickness_text)

        # Determine the number of valid size ranges
        valid_size_prices = []
        for i in range(1, 5):
            size_column = f"מידות{i}"
            price_column = f"מחיר{i}"
            size_range = str(row.get(size_column, "")).strip()
            price_value = str(row.get(price_column, "")).strip()
            if (
                size_range
                and price_value
                and size_range.lower() != "nan"
                and price_value.lower() != "nan"
            ):
                valid_size_prices.append((size_range, price_value))

        # Only draw the table if there are valid size ranges
        if valid_size_prices:
            # Set table position on the right side of the cell
            table_x_start = x_start + cell_width - 5.5 * cm

            # Adjust cell size and font size based on the number of valid size-price pairs
            if len(valid_size_prices) == 4:
                table_y_start = y_start + cell_height - 0.65 * cm
                font_size = 14
                row_height = 0.69 * cm
            elif len(valid_size_prices) == 3:
                table_y_start = y_start + cell_height - 0.675 * cm
                font_size = 16
                row_height = 0.95 * cm
            else:
                table_y_start = y_start + cell_height - 1 * cm
                font_size = 18
                row_height = 1.2 * cm

            # Set stroke color and dash style for the table border
            c.setStrokeColor(colors.grey)
            c.setDash(1, 3)

            # Draw size ranges and prices as table rows
            for size_range, price_value in valid_size_prices:
                # Set font size for size range
                c.setFont("Poppins-Regular", font_size)

                # Calculate the vertical position to center the text within the row
                text_height = (
                    font_size * 0.3527
                )  # Convert font size to points height (approximation)
                vertical_center_y = table_y_start - (row_height - text_height) / 2

                # Draw size range and price, centered vertically in the row
                c.drawCentredString(
                    table_x_start + 1.2 * cm, vertical_center_y + 0.1 * cm, size_range
                )

                # Set font size for price value
                c.setFont("Poppins-Bold", font_size)
                c.drawCentredString(
                    table_x_start + 4.2 * cm,
                    vertical_center_y + 0.1 * cm,
                    f"{price_value}₪",
                )

                # Draw dotted rectangle around the table row
                c.rect(
                    table_x_start - 0.2 * cm,
                    table_y_start - row_height / 2,
                    5.5 * cm,
                    row_height,
                )

                # Draw the vertical line between columns
                c.line(
                    table_x_start
                    + 2.75 * cm,  # Middle point of the row (split columns)
                    table_y_start + row_height / 2,
                    table_x_start + 2.75 * cm,
                    table_y_start - row_height / 2,
                )

                # Move down for the next row
                table_y_start -= row_height

        # Move to the next cell or next page if necessary
        x_start += cell_width  # Move to the next cell
        if (
            x_start + cell_width > height - 1 * cm
        ):  # Check if the next cell fits on the current row
            x_start = 1 * cm
            y_start -= cell_height + 1 * cm  # Move to the next row

        if y_start < 1 * cm:  # Check if we need to move to the next page
            c.showPage()
            x_start = 1 * cm
            y_start = width - cell_height - 1 * cm

    c.save()
    pdf_file.seek(0)  # Rewind the file to the beginning
    return pdf_file
