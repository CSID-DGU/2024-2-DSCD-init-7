
import os
import olefile
import zlib
import struct
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from requests import get
from urllib.parse import urlparse, unquote
import os
import openai
from docx import Document
from dotenv import load_dotenv

load_dotenv()
chatgpt_api_key = os.getenv('chatgpt_api_key')
openai.api_key = chatgpt_api_key

# DOCX 텍스트 추출 함수
def get_docx_text(file_name):
    doc = Document(file_name)
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text

# PDF 텍스트 및 이미지 OCR 추출 함수
def get_pdf_text(file_name):
    doc = fitz.open(file_name)
    text = ""

    for page_num, page in enumerate(doc, start=1):
        # 페이지에서 텍스트 추출
        page_text = page.get_text("text")
        if page_text.strip():
            text += f"--- Page {page_num} Text ---\n{page_text}\n"
        else:
            print(f"Page {page_num}: No extractable text found.")

        # 이미지에서 텍스트(OCR) 추출
        images = page.get_images(full=True)
        if images:
            print(f"Page {page_num} contains images. Performing OCR.")
            for img_index, img in enumerate(images, start=1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))

                # OCR 수행
                ocr_text = pytesseract.image_to_string(image, lang="kor")
                if ocr_text.strip():
                    text += f"--- Page {page_num} Image {img_index} OCR Text ---\n{ocr_text}\n"
                else:
                    print(f"Page {page_num} Image {img_index}: No text found in the image.")
    
    doc.close()
    return text

# HWP 텍스트 추출 함수
def get_hwp_text(filename):
    with olefile.OleFileIO(filename) as f:
        dirs = f.listdir()

        # HWP 파일 검증
        if ["FileHeader"] not in dirs or ["\x05HwpSummaryInformation"] not in dirs:
            raise Exception("Not Valid HWP.")

        # 문서 포맷 압축 여부 확인
        header = f.openstream("FileHeader")
        header_data = header.read()
        is_compressed = (header_data[36] & 1) == 1

        # Body Sections 불러오기
        sections = [f"BodyText/Section{x}" for x in sorted(int(d[1][len("Section"):]) for d in dirs if d[0] == "BodyText")]

        # 전체 text 추출
        text = ""
        for section in sections:
            bodytext = f.openstream(section)
            data = bodytext.read()
            unpacked_data = zlib.decompress(data, -15) if is_compressed else data

            i = 0
            size = len(unpacked_data)
            while i < size:
                header = struct.unpack_from("<I", unpacked_data, i)[0]
                rec_type = header & 0x3ff
                rec_len = (header >> 20) & 0xfff

                if rec_type == 67:
                    rec_data = unpacked_data[i+4:i+4+rec_len]
                    text += rec_data.decode('utf-16') + "\n"

                i += 4 + rec_len

    return text

# 로컬 파일에서 텍스트 추출 함수
def extract_text_from_local_file(file_path):
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1].lower()

    hwp_extensions = [".hwp", ".hwpx", ".hwt", ".hml"]

    try:
        if file_extension in hwp_extensions:
            print(f"Extracting text from Hancom file: {file_name}")
            extracted_text = get_hwp_text(file_path)

        elif file_extension == ".pdf":
            print(f"Extracting text from PDF file: {file_name}")
            extracted_text = get_pdf_text(file_path)

        elif file_extension == ".png":
            print(f"Extracting text from PNG file: {file_name}")
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image, lang='kor+eng')

        elif file_extension == ".docx":
            print(f"Extracting text from DOCX file: {file_name}")
            extracted_text = get_docx_text(file_path)

        else:
            print(f"Unsupported file format: {file_extension}")
            extracted_text = ""

    except Exception as e:
        print(f"Error occurred: {e}")
        extracted_text = ""

    return extracted_text

def augment_evaluation(extracted_text, objective):
    augmentation_clf = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """당신은 다양한 평가 데이터를 생성하는 전문가입니다.
                        당신은 원본 텍스트의 의미와 구조를 유지할 필요 없이, 같은 주제에 대해 전혀 다른 평가 내용을 생성할 수 있습니다.
                        다양한 성과 평가, 기술 기여도, 문제 해결 능력, 협업 및 리더십 평가 등을 창의적으로 작성할 수 있습니다."""},
            {"role": "user", "content": """다음 텍스트를 바탕으로 '{}'에 관련된 완전히 다른 평가 내용을 여러 가지 버전으로 다양하게 작성해줘. 
                    원본 텍스트에 포함된 프로젝트와 기술적 기여 등을 다른 방식으로 평가하고, 그에 따라 새로운 성과 평가와 종합 평가를 생성해줘. 
                    무조건 답은 한국어로 작성해줘.
                    
                    텍스트: '{}'""".format(objective, extracted_text)}
        ]
    )

    return augmentation_clf.choices[-1].message.content


file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', '인사평가서.docx')

# 파일에서 텍스트 추출
extracted_text = extract_text_from_local_file(file_path)

objective = 'We built a system that integrated various alarm messages such as weather deteriorated, order, orders, new enterprises, and promotions.'


# 추출한 텍스트를 바탕으로 평가 내용 생성
augmented_evaluation = augment_evaluation(objective, extracted_text)

print(augmented_evaluation)