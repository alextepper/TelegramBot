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
    vegan = str(row.get("טבעוני", "N/A")).upper()
    grounding = str(row.get("הארקה", "N/A")).upper()

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

    c.setFont("Montserrat-SemiBold", 18)
    color_y_position = y_start + cell_height - 2.55 * cm
    c.drawString(model_x_start, color_y_position, color)

    # Draw the sole thickness next to the color
    c.setFont("Montserrat-Regular", 18)
    thickness_x = model_x_start + c.stringWidth(color, "Montserrat-SemiBold", 18) + 5
    formatted_thickness = (
        f"{float(sole_thickness):.1f}mm"  # Ensure one digit after the dot
    )
    c.drawString(thickness_x + 0.25 * cm, color_y_position, formatted_thickness)

    # Calculate the x-position after the sole thickness for the icons
    current_x_position = thickness_x + c.stringWidth(
        formatted_thickness, "Montserrat-Regular", 18
    )

    # Draw the vegan icon if applicable
    if vegan == "YES":
        # vegan_string = "המוצר אינו מכיל חומרים מהחי, אולם לא עבר בדיקת מעבדה לקבלת תו תקן טבעוני רשמי"
        vegan_path = "logos1/VEGAN.png"  # Path to vegan logo
        c.setFont("Montserrat-Regular", 18)
        try:
            c.drawImage(
                vegan_path,
                current_x_position,
                color_y_position,  # Align vertically (slightly below the text)
                width=2.1 * cm,
                height=0.75 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
            current_x_position += (
                0.66 * cm + 0.4 * cm
            )  # Update the position for the next icon
        except Exception as e:
            print(f"Error loading vegan icon: {e}")

    # Draw the grounding icon if applicable
    if grounding == "YES":
        grounding_path = "logos1/GROUNDING.png"  # Path to grounding logo
        try:
            c.drawImage(
                grounding_path,
                current_x_position,
                color_y_position,  # Align vertically (slightly below the text)
                width=2.1 * cm,
                height=0.75 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception as e:
            print(f"Error loading grounding icon: {e}")

    # Draw the price
    price_x = x_start + 21 * cm
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
            color_y_position,  # Align vertically
            width=shekel_icon_width,
            height=shekel_icon_height,
            preserveAspectRatio=True,
            mask="auto",
        )

        # Draw the formatted price next to the shekel symbol
        price_text_x = price_x + shekel_icon_width + 5  # Slight gap after icon
        c.setFont("Montserrat-SemiBold", 18)
        text_y_position = price_y_position - text_height / 2
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
    vegan = str(row.get("טבעוני", "N/A")).upper()
    grounding = str(row.get("הארקה", "N/A")).upper()

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
    background_path = "logos1/BACKGROUND.png"  # Path to your background image file
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
    c.drawRightString(22.45 * cm - discount_text_width, sale_y_position, "SALE")

    # Draw "-30%" with Montserrat Bold, green color
    c.setFont("Montserrat-Bold", 25)
    c.setFillColorCMYK(
        0.38, 0.04, 1.0, 0.0
    )  # Bright green color (c=38, m=4, y=100, k=0)
    c.drawRightString(x_start + 21.6 * cm, sale_y_position, f"-{discount}%")

    # Draw the color and sole thickness below the model name

    c.setFont("Montserrat-SemiBold", 18)
    c.setFillColorRGB(1, 1, 1)
    color_y_position = y_start + cell_height - 2.55 * cm
    c.drawString(model_x_start, color_y_position, color)

    # Draw the sole thickness next to the color
    c.setFont("Montserrat-Regular", 18)
    thickness_x = model_x_start + c.stringWidth(color, "Montserrat-SemiBold", 18) + 5
    formatted_thickness = (
        f"{float(sole_thickness):.1f}mm"  # Ensure one digit after the dot
    )
    c.drawString(thickness_x + 0.25 * cm, color_y_position, formatted_thickness)

    # Calculate the x-position after the sole thickness for the icons
    current_x_position = thickness_x + c.stringWidth(
        formatted_thickness, "Montserrat-Regular", 18
    )

    # Draw the vegan icon if applicable
    if vegan == "YES":
        vegan_path = "logos1/vegan_white.png"  # Path to vegan logo
        try:
            c.drawImage(
                vegan_path,
                current_x_position,
                color_y_position,  # Align vertically (slightly below the text)
                width=2.1 * cm,
                height=0.75 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
            current_x_position += (
                0.66 * cm + 0.4 * cm
            )  # Update the position for the next icon
        except Exception as e:
            print(f"Error loading vegan icon: {e}")

    # Draw the grounding icon if applicable
    if grounding == "YES":
        grounding_path = "logos1/grounding_white.png"  # Path to grounding logo
        try:
            c.drawImage(
                grounding_path,
                current_x_position,
                color_y_position,  # Align vertically (slightly below the text)
                width=2.1 * cm,
                height=0.75 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception as e:
            print(f"Error loading grounding icon: {e}")

    brush_path = "logos1/BRUSH.png"  # Path to your background image file
    try:
        brush_x = x_start + 21.62 * cm
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
    price_x = x_start + 21 * cm
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


def draw_kids_price_tag(c, x_start, y_start, cell_width, cell_height, row):
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
    print("used draw kids_price_tag")
    model_name = str(row.get("דגם", "N/A")).upper()
    color = str(row.get("צבע", "N/A")).upper()
    price = str(row.get("מחיר", "N/A"))
    brand_name = str(row.get("מותג"))

    sole_thickness_value = row.get("עובי", "N/A")
    vegan = str(row.get("טבעוני", "N/A")).upper()
    grounding = str(row.get("הארקה", "N/A")).upper()

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
    strip_path = "logos1/strip.png"  # Path to your background image file
    try:
        strip_x = x_start + 5 * cm
        c.drawImage(
            strip_path,
            strip_x,
            y_start + cell_height - 1.9 * cm,
            width=cell_width - 13 * cm,  # Adjust width to fit the rest of the cell
            height=cell_height / 2,
            preserveAspectRatio=False,
            mask="auto",
        )
    except Exception as e:
        print(f"Error loading background image: {e}")

    # Draw the model name area starting from 5.6 cm
    model_x_start = x_start + 5.6 * cm
    c.setFont("Montserrat-Bold", 25)
    c.setFillColorRGB(1, 1, 1)  # Dark green color
    c.drawString(model_x_start, y_start + cell_height - 1.4 * cm, model_name)

    # if vegan == "YES":
    #     vegan_path = "logos1/VEGAN.png"  # Path to store logo
    #     vegan_x = x_start + 13.7 * cm
    #     try:
    #         c.drawImage(
    #             vegan_path,
    #             vegan_x,
    #             y_start + cell_height - 1.4 * cm,
    #             width=2.1 * cm,
    #             height=0.62 * cm,
    #             preserveAspectRatio=True,
    #             mask="auto",
    #         )
    #     except Exception as e:
    #         print(f"Error loading store logo: {e}")

    # if grounding == "YES":
    #     grounding_path = "logos1/grounding.png"  # Path to store logo
    #     grounding_x = x_start + 14.7 * cm
    #     try:
    #         c.drawImage(
    #             grounding_path,
    #             grounding_x,
    #             y_start + cell_height - 1.4 * cm,
    #             width=2.1 * cm,
    #             height=0.62 * cm,
    #             preserveAspectRatio=True,
    #             mask="auto",
    #         )
    #     except Exception as e:
    #         print(f"Error loading store logo: {e}")

    # Draw the color and sole thickness below the model name
    c.setFont("Montserrat-SemiBold", 18)
    c.setFillColorRGB(67 / 255, 75 / 255, 49 / 255)  # Dark green color
    color_y_position = y_start + cell_height - 2.55 * cm
    c.drawString(model_x_start, color_y_position, color)

    # Draw the sole thickness next to the color
    c.setFont("Montserrat-Regular", 18)
    thickness_x = model_x_start + c.stringWidth(color, "Montserrat-SemiBold", 18) + 5
    c.drawString(thickness_x + 0.25 * cm, color_y_position, f"{sole_thickness}mm")

    formatted_thickness = (
        f"{float(sole_thickness):.1f}mm"  # Ensure one digit after the dot
    )

    # Calculate the x-position after the sole thickness for the icons
    current_x_position = thickness_x + c.stringWidth(
        formatted_thickness, "Montserrat-Regular", 18
    )

    # Draw the vegan icon if applicable
    if vegan == "YES":
        vegan_path = "logos1/VEGAN.png"  # Path to vegan logo
        try:
            c.drawImage(
                vegan_path,
                current_x_position,
                color_y_position,  # Align vertically (slightly below the text)
                width=2.1 * cm,
                height=0.75 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
            current_x_position += (
                0.66 * cm + 0.4 * cm
            )  # Update the position for the next icon
        except Exception as e:
            print(f"Error loading vegan icon: {e}")

    # Draw the grounding icon if applicable
    if grounding == "YES":
        grounding_path = "logos1/grounding.png"  # Path to grounding logo
        try:
            c.drawImage(
                grounding_path,
                current_x_position,
                color_y_position,  # Align vertically (slightly below the text)
                width=2.1 * cm,
                height=0.75 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception as e:
            print(f"Error loading grounding icon: {e}")

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
        table_x_start = x_start + cell_width - 8 * cm

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
            c.setFont("Montserrat-Regular", font_size)

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
            c.setFont("Montserrat-Bold", font_size)
            c.drawCentredString(
                table_x_start + 4.2 * cm,
                vertical_center_y + 0.1 * cm,
                f"{price_value}₪",
            )

            # Draw the vertical line between columns
            line_x = x_start + 4.9 * cm
            c.setDash([])  # Reset dash pattern
            c.setStrokeColorCMYK(0.38, 0.04, 1.0, 0.0)  # Bright green color
            c.setLineWidth(1)
            c.line(
                table_x_start + 2.75 * cm,  # Middle point of the row (split columns)
                y_start + 0.65 * cm,
                table_x_start + 2.75 * cm,
                y_start + cell_height - 0.65 * cm,
            )

            # Move down for the next row
            table_y_start -= row_height

    # Draw the store logo at 21.7 cm (1.8 cm wide)
    store_logo_path = "logos1/store_logo_kids.png"  # Path to store logo
    store_logo_x = x_start + 21.7 * cm
    try:
        c.drawImage(
            store_logo_path,
            store_logo_x,
            y_start + (cell_height - 3 * cm) / 2,
            width=2.1 * cm,
            height=3 * cm,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception as e:
        print(f"Error loading store logo: {e}")


def draw_kids_discount_price_tag(c, x_start, y_start, cell_width, cell_height, row):
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
    vegan = str(row.get("טבעוני", "N/A")).upper()
    grounding = str(row.get("הארקה", "N/A")).upper()

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

    if vegan == "YES":
        vegan_path = "logos1/VEGAN.png"  # Path to store logo
        vegan_x = x_start + 13.7 * cm
        try:
            c.drawImage(
                vegan_path,
                vegan_x,
                y_start + cell_height - 1.4 * cm,
                width=2.1 * cm,
                height=0.62 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception as e:
            print(f"Error loading store logo: {e}")

    if grounding == "YES":
        grounding_path = "logos1/grounding.png"  # Path to store logo
        grounding_x = x_start + 14.7 * cm
        try:
            c.drawImage(
                grounding_path,
                grounding_x,
                y_start + cell_height - 1.4 * cm,
                width=2.1 * cm,
                height=0.62 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception as e:
            print(f"Error loading store logo: {e}")

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
