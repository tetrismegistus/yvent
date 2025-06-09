from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import qrcode

DEFAULT_WIDTH = 1570
DEFAULT_HEIGHT = 2048
DEFAULT_MARGIN = 60


def parse_event_data(title: str, dt_str: str, location: str, qr_text: str, logo_path: Path, font_path: Path, output_path: Path):
    # Parse datetime string to datetime object
    event_datetime = datetime.fromisoformat(dt_str)

    # Ensure paths are absolute and exist where appropriate
    logo_path = Path(logo_path).resolve()
    font_path = Path(font_path).resolve()
    output_path = Path(output_path).resolve()

    # Return parsed and validated data
    return {
        "title": title,
        "datetime": event_datetime,
        "location": location,
        "qr_text": qr_text,
        "logo_path": logo_path,
        "font_path": font_path,
        "output_path": output_path,
    }


def parse_event_data(title: str, dt_str: str, location: str, qr_text: str, logo_path: Path, font_path: Path, output_path: Path):
    event_datetime = datetime.fromisoformat(dt_str)
    logo_path = Path(logo_path).resolve()
    font_path = Path(font_path).resolve()
    output_path = Path(output_path).resolve()

    return {
        "title": title,
        "datetime": event_datetime,
        "location": location,
        "qr_text": qr_text,
        "logo_path": logo_path,
        "font_path": font_path,
        "output_path": output_path,
    }


class ImageComposer:
    def __init__(self, output_width=DEFAULT_WIDTH, output_height=DEFAULT_HEIGHT, background_color='white', margin=DEFAULT_MARGIN, gradient=None):
        self.width = output_width
        self.height = output_height
        self.margin = margin

        if gradient:
            self.canvas = self.create_gradient_background(*gradient)
        else:
            self.canvas = Image.new('RGB', (self.width, self.height), background_color)

        self.draw = ImageDraw.Draw(self.canvas)

    def create_gradient_background(self, from_color, to_color, direction='vertical'):
        base = Image.new('RGB', (self.width, self.height), from_color)
        top = Image.new('RGB', (self.width, self.height), to_color)
        mask = Image.new('L', (self.width, self.height))
        mask_data = []

        if direction == 'vertical':
            for y in range(self.height):
                mask_data.extend([int(255 * (y / self.height))] * self.width)
        else:  # horizontal
            for y in range(self.height):
                row = [int(255 * (x / self.width)) for x in range(self.width)]
                mask_data.extend(row)

        mask.putdata(mask_data)
        gradient = Image.composite(top, base, mask)
        return gradient

    def add_overlay(self, png_path, x, y, scale_to=None):
        overlay = Image.open(png_path).convert('RGBA')
        if scale_to:
            overlay.thumbnail((scale_to, scale_to))
        self.canvas.paste(overlay, (x, y), overlay)

    def add_text(self, text, x, y, font_size=48, color='black', font_path=None, rotate=0):
        font = ImageFont.truetype(str(font_path), font_size) if font_path else None

        # Estimate text size
        dummy_img = Image.new('RGBA', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        text_size = dummy_draw.textbbox((0, 0), text, font=font)
        width = text_size[2] - text_size[0]
        height = text_size[3] - text_size[1]

        # Create small text image and draw on it
        text_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((0, 0), text, font=font, fill=color)

        # Rotate text if needed
        if rotate != 0:
            text_img = text_img.rotate(rotate, expand=1)

        # Paste text image onto canvas
        self.canvas.paste(text_img, (x, y), text_img)

    def generate_qr_code(self, qr_text, pixel_size=10, border_modules=1):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=pixel_size,
            border=border_modules,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
        return img

    def add_qr_code(self, qr_text, x, y, pixel_size=10):
        qr_img = self.generate_qr_code(qr_text, pixel_size=pixel_size)
        self.canvas.paste(qr_img, (x, y), qr_img)

    def save_to(self, path):
        self.canvas.save(path)
