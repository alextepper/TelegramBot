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

from utils import draw_price_tag, draw_discount_price_tag

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


def generate_discount_pdf(dataframe):
    pdf_file = io.BytesIO()
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4
    c.setPageSize((height, width))

    cell_width = 24.3 * cm
    cell_height = 3.3 * cm
    x_start = 1 * cm
    y_start = width - cell_height - 1 * cm

    for index, row in dataframe.iterrows():
        discount = str(row.get("הנחה", "N/A"))
        model_name = str(row.get("דגם", "N/A")).upper()
        color = str(row.get("צבע", "N/A")).upper()
        sole_thickness = str(row.get("עובי", "N/A"))
        price = str(row.get("מחיר", "N/A"))
        brand_name = str(row.get("מותג"))

        # Set the stroke color to light grey
        light_grey = colors.Color(0.85, 0.85, 0.85)  # RGB values for light grey
        c.setStrokeColor(light_grey)

        # Set the line style to dotted
        c.setDash(1, 2)  # 1 unit on, 2 units off for a dotted line pattern

        # Draw the cell border with the new settings
        c.rect(x_start, y_start, cell_width, cell_height, stroke=1, fill=0)

        # Draw the brand logo area (0 cm to 4.9 cm)
        brand_logo_path = f"logos1/{brand_name}.png" if brand_name else None
        if brand_logo_path and os.path.exists(brand_logo_path):
            try:
                max_logo_width = 4.2 * cm
                max_logo_height = cell_height - 0.6 * cm
                logo_x = (
                    x_start + (4.9 * cm - max_logo_width) / 2
                )  # Center horizontally
                logo_y = (
                    y_start + (cell_height - max_logo_height) / 2
                )  # Center vertically
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

        background_path = "logos1/background.png"  # Path to your background image file
        try:
            background_x = x_start + 4.9 * cm
            c.drawImage(
                background_path,
                background_x,
                y_start,
                width=cell_width - 4.9 * cm,  # Adjust width to fit the rest of the cell
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
            # c.setFillColorRGB(0.67, 0.75, 0)  # Dark green color
            c.drawString(model_x_start, y_start + cell_height - 1.4 * cm, model_name)
        else:
            line_x = x_start + 4.9 * cm
            c.setDash([])
            c.setStrokeColorCMYK(0.38, 0.04, 1.0, 0.0)
            c.setLineWidth(1)
            c.line(
                line_x, y_start + 0.65 * cm, line_x, y_start + cell_height - 0.65 * cm
            )

        # Draw a vertical bright green line at 4.9 cm

        # Draw the model name area starting from 5.6 cm
        model_x_start = x_start + 5.6 * cm
        c.setFont("Montserrat-Bold", 25)
        c.setFillColorRGB(67 / 255, 75 / 255, 49 / 255)
        # c.setFillColorRGB(0.67, 0.75, 0)  # Dark green color
        c.drawString(model_x_start, y_start + cell_height - 1.4 * cm, model_name)

        # Draw the color and sole thickness below the model name
        c.setFont("Montserrat-SemiBold", 18)
        color_y_position = y_start + cell_height - 2.55 * cm
        c.drawString(model_x_start, color_y_position, color)

        # Draw the sole thickness next to the color
        c.setFont("Montserrat-Regular", 18)
        thickness_x = (
            model_x_start + c.stringWidth(color, "Montserrat-SemiBold", 18) + 5
        )
        c.drawString(thickness_x + 0.25 * cm, color_y_position, f"{sole_thickness}mm")

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

        price_text_width = c.stringWidth(
            formatted_price, "Montserrat-SemiBold", font_size
        )

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
