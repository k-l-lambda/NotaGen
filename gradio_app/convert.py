import os
import subprocess
import fitz
from PIL import Image

from .ms import MSCORE


def abc2xml(filename_base):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    abc_filename = f"{filename_base}.abc"
    dir, name = os.path.split(abc_filename)
    subprocess.run(
        ["python", os.path.join(current_dir, "abc2xml.py"), '-o', dir, abc_filename, ],
        check=True,
        capture_output=True,
        text=True
    )


def xml2(filename_base, target_fmt):

    xml_file = filename_base + '.xml'
    if not "." in target_fmt:
        target_fmt = "." + target_fmt

    target_file = filename_base + target_fmt
    command = [MSCORE, "-o", target_file, xml_file]
    result = subprocess.run(command)
    return target_file


def pdf2img(filename_base, dpi=300):

    pdf_path = f"{filename_base}.pdf"
    doc = fitz.open(pdf_path)
    img_list = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # 创建高分辨率矩阵
        matrix = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=matrix)
        
        # 转换为PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_list.append(img)

    return img_list


# if __name__ == '__main__':
#     pdf2img('20250304_200811_Baroque_Bach, Johann Sebastian_Choral')
