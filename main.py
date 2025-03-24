from docx2pdf import convert
import os
import fitz  # PyMuPDF
def convert_word_to_pdf(input_file, output_file):
    try:
        # Конвертация Word в PDF
        convert(input_file, output_file)
        print(f"Файл {input_file} успешно конвертирован в {output_file}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

folder_path = "5"
for file_name in os.listdir(folder_path):
    input_word_file = f"5/{file_name}"
    output_pdf_file = f"finish/{file_name[:-5]}.pdf"
    convert_word_to_pdf(input_word_file, output_pdf_file)
def add_png_stamp_to_pdf(input_pdf, output_pdf, stamp_image, position=(0, 0), scale=1.0):
    """
    Добавляет PNG-изображение (печать) на каждую страницу PDF-файла.

    :param input_pdf: Путь к исходному PDF-файлу.
    :param output_pdf: Путь к выходному PDF-файлу.
    :param stamp_image: Путь к PNG-изображению (печать).
    :param position: Позиция изображения на странице (x, y).
    :param scale: Масштаб изображения (по умолчанию 1.0).
    """
    # Открываем PDF-файл
    pdf_document = fitz.open(input_pdf)

    # Получаем страницу
    page = pdf_document[0]

    # Открываем изображение
    image_rect = fitz.Rect(position[0], position[1], position[0] + 100 * scale, position[1] + 100 * scale)  # Размер изображения
    page.insert_image(image_rect, filename=stamp_image)

    # Сохраняем измененный PDF
    pdf_document.save(output_pdf)
    pdf_document.close()
    print(f"Печать добавлена в файл: {output_pdf}")
folder_path = 'finish'
for file_name in os.listdir(folder_path):
    sim = file_name.find('Н')
    print(sim)
    if sim>0:
        input_pdf = f"finish/{file_name}"
        output_pdf = f"output/{file_name}"
        stamp_image = "stamp/stamp.png"  # Путь к PNG-изображению печати
        position = (470, 330)  # Позиция печати (x, y)
        scale = 1.4  # Масштаб печати

        add_png_stamp_to_pdf(input_pdf, output_pdf, stamp_image, position, scale)
        input_pdf = f"output/{file_name}"
        output_pdf = f"out/{file_name}"
        stamp_image = "stamp/stamp2.png"  # Путь к PNG-изображению печати
        position = (320, 270)  # Позиция печати (x, y)
        scale = 0.8  # Масштаб печати
        add_png_stamp_to_pdf(input_pdf, output_pdf, stamp_image, position, scale)
    else:
        print("M")
        input_pdf = f"finish/{file_name}"
        output_pdf = f"output/{file_name}"
        stamp_image = "stamp/stamp.png"  # Путь к PNG-изображению печати
        position = (470, 300)  # Позиция печати (x, y)
        scale = 1.4  # Масштаб печати

        add_png_stamp_to_pdf(input_pdf, output_pdf, stamp_image, position, scale)
        input_pdf = f"output/{file_name}"
        output_pdf = f"out/{file_name}"
        stamp_image = "stamp/stamp2.png"  # Путь к PNG-изображению печати
        position = (320, 240)  # Позиция печати (x, y)
        scale = 0.8  # Масштаб печати
        add_png_stamp_to_pdf(input_pdf, output_pdf, stamp_image, position, scale)