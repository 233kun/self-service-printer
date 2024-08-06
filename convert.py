import os

import img2pdf
import pythoncom
import win32com.client
from pypdf import PdfReader

import convert_status_global_var
import files_attributes_global_var
import global_var


def convert_docs(directory, filename):
    pythoncom.CoInitialize()
    wdFormatPDF = 17
    word = win32com.client.Dispatch("Word.Application")
    # global_var.global_var_setter(directory + filename, "processing")
    input_doc = os.path.abspath(f"save_files/{directory}/raw/{filename}")
    output_filename = filename.rsplit(".", 1)[0]
    output_pdf = os.path.abspath(f"save_files/{directory}/converted/{output_filename}.pdf")
    files_attributes = files_attributes_global_var.getter(directory)

    for index in range(len(files_attributes)):
        if files_attributes[index].filename == filename:
            files_attributes[index].convert_state = 'processing'
    files_attributes_global_var.setter(directory, files_attributes)

    global doc
    try:
        doc = word.Documents.Open(input_doc)
        doc.SaveAs(output_pdf, FileFormat=wdFormatPDF)
        for file_attributes in files_attributes:
            if file_attributes.filename == filename:
                file_attributes.convert_state = 'success'

            reader = PdfReader(f"save_files/{directory}/converted/{file_attributes.filename.rsplit(".", 1)[0]}.pdf")
            file_attributes.total_pages = len(reader.pages)
            file_attributes.print_range_end = len(reader.pages)

        global_var.global_var_setter(directory, files_attributes)
    except Exception as e:
        for index in range(len(files_attributes)):
            if files_attributes[index].filename == filename:
                files_attributes[index].convert_state = 'error'
        global_var.global_var_setter(directory, files_attributes)
        raise Exception(e)
    finally:
        doc.Close()
        word.Quit()
        pythoncom.CoUninitialize()

def convert_excel(directory, filename):
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = 0
    input_excel = os.path.abspath(f"save_files/{directory}/raw/{filename}")
    output_filename = filename.rsplit(".", 1)[0]
    output_pdf = os.path.abspath(f"save_files/{directory}/converted/{output_filename}.pdf")
    excel.Quit()
    global sheets
    try:
        sheets = excel.Workbooks.Open(input_excel, False)
        sheets.ExportAsFixedFormat(0, output_pdf)
    except Exception as e:
        raise Exception(e)
    finally:
        sheets.Close(False)  # must be closed before excel quit
        excel.Quit()


def convert_images(directory, filename):
    a4inpt = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
    layout_fun = img2pdf.get_layout_fun(a4inpt)
    output_filename = filename.rsplit(".", 1)[0]
    try:
        with open(f"save_files/{directory}/converted/{output_filename}.pdf", "wb") as f:
            f.write(img2pdf.convert(f"save_files/{directory}/raw/{filename}", layout_fun=layout_fun))
    except Exception as e:
        raise Exception(e)
