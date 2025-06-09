import argparse
from yvent.base import ImageComposer, parse_event_data
from pathlib import Path


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
    # Use parser function to validate and normalize inputs
    data = parse_event_data(
        title=args.title.lower(),
        dt_str=args.datetime.lower(),
        location=args.location.lower(),
        qr_text=args.qr_text,
        logo_path=args.logo_path,
        font_path=args.font_path,
        output_path=args.output_path,
    )

    event_date = data["datetime"].strftime("%B %d, %Y").lower()
    event_time = data["datetime"].strftime("%I:%M %p").lstrip('0').lower()

    composer = ImageComposer(gradient=("white", "blue", "vertical"))

    composer.add_overlay(data["logo_path"], x=composer.margin, y=composer.margin, scale_to=750)

    angle = 45
    diagonal_x = int(composer.width / 4.25)
    diagonal_y = int(composer.height / 2.75)
    composer.add_text(data["title"], x=diagonal_x, y=diagonal_y, font_size=140, rotate=angle, font_path=data["font_path"])

    info_x = composer.width - 460
    info_y = int(composer.height / 1.85)
    composer.add_text(event_date,  x=info_x, y=info_y + 120, font_size=48, font_path=data["font_path"])
    composer.add_text(event_time,  x=info_x, y=info_y + 200, font_size=48, font_path=data["font_path"])
    composer.add_text(data["location"], x=info_x, y=info_y + 280, font_size=38, font_path=data["font_path"])

    if data["qr_text"]:
        composer.add_qr_code(data["qr_text"], x=info_x - 20, y=info_y + 380, pixel_size=15)

    composer.save_to(data["output_path"])

if __name__ == '__main__':
    main()
