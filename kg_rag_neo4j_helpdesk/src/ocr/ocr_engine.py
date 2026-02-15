from PIL import Image
import pytesseract

def ocr_image_to_text(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return (text or "").strip()
