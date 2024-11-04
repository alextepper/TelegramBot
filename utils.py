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
pdfmetrics.registerFont(TTFont("Montserrat-Bold", "fonts/Montserrat-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Montserrat-SemiBold", "fonts/Montserrat-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Montserrat-Regular", "fonts/Montserrat-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Montserrat-Medium", "fonts/Montserrat-Medium.ttf"))


def draw_price_tag(c, x_start, y_start, cell_width, cell_height, row):
    """
    Draws the price tag on the canvas.

    :param c: The canvas object to draw on.
    :param x_start: The starting x-coordinate for the cell.
    :param y_start: The starting y-coordinate for the cell.
    :param cell_width: The width of the cell.
    :param cell_height: The height of the cell.
    :param row: The row data containing model, color, price, etc.
    """
    # Extract the row data
    model_name = str(row.get("דגם", "N/A")).upper()
    color = str(row.get("צבע", "N/A")).upper()
    price = str(row.get("מחיר", "N/A"))
    brand_name = str(row.get("מותג"))

    sole_thickness_value = row.get("עובי", "N/A")

    try:
        # Convert the sole thickness to a float and format it with one digit after the dot
        sole_thickness = f"{float(sole_thickness_value):.1f}"
    except (ValueError, TypeError):
        # Handle cases where sole_thickness_value is not a valid float
        sole_thickness = "N/A"

    # Draw the brand logo area (0 cm to 4.9 cm)
    brand_logo_path = f"logos1/{brand_name}.png" if brand_name else None
    if brand_logo_path and os.path.exists(brand_logo_path):
        try:
            max_logo_width = 4.2 * cm
            max_logo_height = cell_height - 0.6 * cm
            logo_x = x_start + (4.9 * cm - max_logo_width) / 2  # Center horizontally
            logo_y = y_start + (cell_height - max_logo_height) / 2  # Center vertically
            c.drawImage(
                brand_logo_path,
                logo_x,
                logo_y,
                width=max_logo_width,
                height=max_logo_height,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception as e:
            print(f"Error loading brand logo: {e}")

    # Draw a vertical bright green line at 4.9 cm
    line_x = x_start + 4.9 * cm
    c.setDash([])  # Reset dash pattern
    c.setStrokeColorCMYK(0.38, 0.04, 1.0, 0.0)  # Bright green color
    c.setLineWidth(1)
    c.line(line_x, y_start + 0.65 * cm, line_x, y_start + cell_height - 0.65 * cm)

    # Draw the model name area starting from 5.6 cm
    model_x_start = x_start + 5.6 * cm
    c.setFont("Montserrat-Bold", 25)
    c.setFillColorRGB(67 / 255, 75 / 255, 49 / 255)  # Dark green color
    c.drawString(model_x_start, y_start + cell_height - 1.4 * cm, model_name)

    # Draw the color and sole thickness below the model name
    c.setFont("Montserrat-SemiBold", 18)
    color_y_position = y_start + cell_height - 2.55 * cm
    c.drawString(model_x_start, color_y_position, color)

    # Draw the sole thickness next to the color
    c.setFont("Montserrat-Regular", 18)
    thickness_x = model_x_start + c.stringWidth(color, "Montserrat-SemiBold", 18) + 5
    c.drawString(thickness_x + 0.25 * cm, color_y_position, f"{sole_thickness}mm")

    # Draw the price
    price_x = x_start + 20.5 * cm
    try:
        formatted_price = f"{float(price):,.2f}"
    except ValueError:
        formatted_price = price  # Fallback to original if conversion fails

    price_y_position = y_start + cell_height / 2

    shekel_icon_path = "logos1/shekel.png"  # Path to your shekel symbol PNG file
    shekel_icon_height = 0.35 * cm  # 4 mm height
    shekel_icon_width = shekel_icon_height * 1.2  # Keep aspect ratio

    font_size = 18
    text_height = font_size * 0.6

    price_text_width = c.stringWidth(formatted_price, "Montserrat-SemiBold", font_size)

    try:
        # Draw the shekel symbol PNG
        c.drawImage(
            shekel_icon_path,
            price_x - price_text_width,
            price_y_position - text_height / 2,  # Align vertically
            width=shekel_icon_width,
            height=shekel_icon_height,
            preserveAspectRatio=True,
            mask="auto",
        )

        # Draw the formatted price next to the shekel symbol
        price_text_x = price_x + shekel_icon_width + 5  # Slight gap after icon
        c.setFont("Montserrat-SemiBold", 18)
        text_y_position = price_y_position - text_height / 2
        c.drawRightString(price_text_x, text_y_position, formatted_price)

    except Exception as e:
        print(f"Error loading shekel icon: {e}")

    # Draw the store logo at 21.7 cm (1.8 cm wide)
    store_logo_path = "logos1/store_logo.png"  # Path to store logo
    store_logo_x = x_start + 21.7 * cm
    try:
        c.drawImage(
            store_logo_path,
            store_logo_x,
            y_start + (cell_height - 2.1 * cm) / 2,
            width=2.1 * cm,
            height=2.1 * cm,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception as e:
        print(f"Error loading store logo: {e}")


def draw_discount_price_tag(c, x_start, y_start, cell_width, cell_height, row):
    """
    Draws the price tag with background on the canvas.

    :param c: The canvas object to draw on.
    :param x_start: The starting x-coordinate for the cell.
    :param y_start: The starting y-coordinate for the cell.
    :param cell_width: The width of the cell.
    :param cell_height: The height of the cell.
    :param row: The row data containing model, color, price, etc.
    """
    model_name = str(row.get("דגם", "N/A")).upper()
    color = str(row.get("צבע", "N/A")).upper()
    price = str(row.get("מחיר", "N/A"))
    brand_name = str(row.get("מותג"))
    discount = str(int(row.get("הנחה")))
    sole_thickness_value = row.get("עובי", "N/A")

    try:
        # Convert the sole thickness to a float and format it with one digit after the dot
        sole_thickness = f"{float(sole_thickness_value):.1f}"
    except (ValueError, TypeError):
        # Handle cases where sole_thickness_value is not a valid float
        sole_thickness = "N/A"

    # Draw the brand logo area (0 cm to 4.9 cm)
    brand_logo_path = f"logos1/{brand_name}.png" if brand_name else None
    if brand_logo_path and os.path.exists(brand_logo_path):
        try:
            max_logo_width = 4.2 * cm
            max_logo_height = cell_height - 0.6 * cm
            logo_x = x_start + (4.9 * cm - max_logo_width) / 2  # Center horizontally
            logo_y = y_start + (cell_height - max_logo_height) / 2  # Center vertically
            c.drawImage(
                brand_logo_path,
                logo_x,
                logo_y,
                width=max_logo_width,
                height=max_logo_height,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception as e:
            print(f"Error loading brand logo: {e}")

    # Draw the background starting from 4.9 cm
    background_path = "logos1/background.png"  # Path to your background image file
    try:
        background_x = x_start + 4.6 * cm
        c.drawImage(
            background_path,
            background_x,
            y_start,
            width=cell_width - 4.6 * cm,  # Adjust width to fit the rest of the cell
            height=cell_height,
            preserveAspectRatio=False,
            mask="auto",
        )
    except Exception as e:
        print(f"Error loading background image: {e}")

    # Draw the model name area starting from 5.6 cm
    model_x_start = x_start + 5.6 * cm
    c.setFont("Montserrat-Bold", 25)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(model_x_start, y_start + cell_height - 1.4 * cm, model_name)

    # Draw the "SALE -30%" text to the right of the model name
    sale_text_x_start = (
        model_x_start + c.stringWidth(f"-{discount}%", "Montserrat-Bold", 25) + 15
    )
    sale_y_position = y_start + cell_height - 1.4 * cm

    discount_text_width = c.stringWidth(f"-{discount}%", "Montserrat-Bold", 25)

    # Draw "SALE" with Montserrat Medium, white color
    c.setFont("Montserrat-Medium", 25)
    c.setFillColorRGB(1, 1, 1)
    c.drawRightString(21.95 * cm - discount_text_width, sale_y_position, "SALE")

    # Draw "-30%" with Montserrat Bold, green color
    c.setFont("Montserrat-Bold", 25)
    c.setFillColorCMYK(
        0.38, 0.04, 1.0, 0.0
    )  # Bright green color (c=38, m=4, y=100, k=0)
    c.drawRightString(x_start + 21.1 * cm, sale_y_position, f"-{discount}%")

    # Draw the color and sole thickness below the model name
    c.setFont("Montserrat-SemiBold", 18)
    c.setFillColorRGB(1, 1, 1)
    color_y_position = y_start + cell_height - 2.55 * cm
    c.drawString(model_x_start, color_y_position, color)

    # Draw the sole thickness next to the color
    c.setFont("Montserrat-Regular", 18)
    thickness_x = model_x_start + c.stringWidth(color, "Montserrat-SemiBold", 18) + 5
    c.drawString(thickness_x + 0.25 * cm, color_y_position, f"{sole_thickness}mm")

    brush_path = "logos1/brush.png"  # Path to your background image file
    try:
        brush_x = x_start + 21.12 * cm
        c.drawImage(
            brush_path,
            brush_x,
            y_start + cell_height / 2 - 0.2 * cm,
            width=-4.7 * cm,  # Adjust width to fit the rest of the cell
            height=0.2 * cm,
            preserveAspectRatio=False,
            mask="auto",
        )
    except Exception as e:
        print(f"Error loading background image: {e}")

    # Draw the price at the right position, aligned with the color
    price_x = x_start + 20.5 * cm
    try:
        formatted_price = f"{float(price):,.2f}"
    except ValueError:
        formatted_price = price  # Fallback to original if conversion fails

    shekel_icon_path = "logos1/white_Shekel.png"  # Path to your shekel symbol PNG file
    shekel_icon_height = 0.35 * cm  # 4 mm height
    shekel_icon_width = shekel_icon_height * 1.2  # Keep aspect ratio

    font_size = 18
    text_height = font_size * 0.6

    price_text_width = c.stringWidth(formatted_price, "Montserrat-SemiBold", font_size)

    try:
        # Draw the shekel symbol PNG aligned with the color
        c.drawImage(
            shekel_icon_path,
            price_x - price_text_width,
            color_y_position,  # Align vertically
            width=shekel_icon_width,
            height=shekel_icon_height,
            preserveAspectRatio=True,
            mask="auto",
        )

        # Draw the formatted price next to the shekel symbol
        price_text_x = price_x + shekel_icon_width + 5  # Slight gap after icon
        c.setFont("Montserrat-SemiBold", 18)
        c.drawRightString(price_text_x, color_y_position, formatted_price)
    except Exception as e:
        print(f"Error loading shekel icon: {e}")

    # Draw the store logo at 21.7 cm (1.8 cm wide)
    store_logo_path = "logos1/store_logo.png"  # Path to store logo
    store_logo_x = x_start + 21.7 * cm
    try:
        c.drawImage(
            store_logo_path,
            store_logo_x,
            y_start + (cell_height - 2.1 * cm) / 2,
            width=2.1 * cm,
            height=2.1 * cm,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception as e:
        print(f"Error loading store logo: {e}")
