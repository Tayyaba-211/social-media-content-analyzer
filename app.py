import os
import uuid
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pdfplumber
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'


from pdf2image import convert_from_path

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ocr_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"[OCR error] {str(e)}"


def extract_text_from_pdf(pdf_path):
    text_pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                ptext = page.extract_text()
                if ptext:
                    text_pages.append(ptext)
        joined = "\n\n".join(text_pages).strip()
        if not joined:
            images = convert_from_path(pdf_path)
            ocr_texts = []
            for img in images:
                tmp_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{uuid.uuid4().hex}.png")
                img.save(tmp_path, "PNG")
                t = pytesseract.image_to_string(Image.open(tmp_path))
                ocr_texts.append(t)
                os.remove(tmp_path)
            return "\n\n".join(ocr_texts).strip()
        return joined
    except Exception as e:
        return f"[PDF parse error] {str(e)}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/extract-text', methods=['POST'])
def extract_text():
    import os
    import pdfplumber
    from pdf2image import convert_from_path
    from PIL import Image

    # get uploaded file
    file = request.files['file']
    if not file:
        return jsonify({'success': False, 'error': 'No file uploaded'})

    filename = file.filename
    file_path = os.path.join('uploads', filename)
    file.save(file_path)

    extracted_text = ""

    try:
        # For PDF files
        if filename.lower().endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted_text += page.extract_text() or ""

            # If no text found (scanned PDF), use OCR
            if not extracted_text.strip():
                pages = convert_from_path(file_path)
                for page in pages:
                    text = pytesseract.image_to_string(page)
                    extracted_text += text + "\n"

        # For images
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img)

        else:
            return jsonify({'success': False, 'error': 'Unsupported file type'})

        if not extracted_text.strip():
            extracted_text = "[No readable text found]"

        # Save extracted text
        output_path = os.path.join('uploads', 'extracted.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(extracted_text)

        return jsonify({'success': True, 'text': extracted_text})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



if __name__ == "__main__":
    app.run(debug=True)
