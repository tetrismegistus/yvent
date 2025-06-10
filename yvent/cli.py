import argparse
import textwrap
from yvent.base import ImageComposer, parse_event_data
from pathlib import Path
from PIL import ImageFont

def get_parser():
    parser = argparse.ArgumentParser(
        description="Generate a custom event flier with QR code and branding."
    )
    parser.add_argument('--title', required=True, help='Title of the event')
    parser.add_argument('--datetime', required=True, help='Date and time of the event (e.g., 2025-06-15T18:30)')
    parser.add_argument('--location', required=True, help='Location of the event')
    parser.add_argument('--qr-text', required=True, help='Text to encode in the QR code')
    parser.add_argument('--logo-path', type=Path, required=True, help='Path to the logo image file')
    parser.add_argument('--font-path', type=Path, required=True, help='Path to the font file (e.g., .ttf)')
    parser.add_argument('--output-path', type=Path, required=True, help='Path to save the output image or PDF')
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    data = parse_event_data(
        title=args.title,
        dt_str=args.datetime,
        location=args.location,
        qr_text=args.qr_text,
        logo_path=args.logo_path,
        font_path=args.font_path,
        output_path=args.output_path,
    )

    event_date = data["datetime"].strftime("%B %d, %Y")
    event_time = data["datetime"].strftime("%I:%M %p").lstrip('0')

    composer = ImageComposer(gradient=("white", "blue", "vertical"))
    composer.add_overlay(data["logo_path"], x=composer.margin, y=composer.margin, scale_to=750)

    # Load fonts

    title_font = composer.find_fitting_font(
        data["title"],
        str(data["font_path"]),
        max_width=composer.width - 2 * composer.margin,
        max_height=composer.height - 2 * composer.margin
    )


    info_font = ImageFont.truetype(str(data["font_path"]), 48)
    location_font = ImageFont.truetype(str(data["font_path"]), 38)

    # --- Centered Tilted Title ---
    center_x = composer.width // 2
    center_y = composer.height // 2
    composer.add_text(data["title"], x=center_x, y=center_y, font=title_font, rotate=45, anchor="mm")

    # --- QR Code ---
    qr_box_size = 400
    qr_visual_padding = 60
    qr_margin = composer.margin + qr_visual_padding
    qr_x = composer.width - qr_box_size - qr_margin
    qr_y = composer.height - qr_box_size - qr_margin
    qr_img_width = 0

    if data["qr_text"]:
        qr_img_width = composer.add_qr_code(data["qr_text"], x=qr_x, y=qr_y)

    # --- Info Text Block ---
    wrapped_location_lines = textwrap.wrap(data["location"], width=40)

    info_lines = [
        (event_date, info_font),
        (event_time, info_font),
    ] + [(line, location_font) for line in wrapped_location_lines]


    spacing = 10
    total_info_height = sum(
        composer.draw.textbbox((0, 0), text, font=font)[3] - composer.draw.textbbox((0, 0), text, font=font)[1]
        + spacing for text, font in info_lines
    ) - spacing

    current_y = qr_y - total_info_height - (spacing * 2)

    for text, font in info_lines:
        bbox = composer.draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = qr_x + qr_img_width - text_w# right-align with QR box
        composer.add_text(text, x=text_x, y=current_y, font=font)
        current_y += bbox[3] - bbox[1] + spacing

    composer.save_to(data["output_path"])


if __name__ == '__main__':
    main()
