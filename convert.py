import os

import img2pdf
import win32com.client

import global_var


def convert_docs(directory, filename):
    # filelist = os.listdir(f"save_files/{directory}/raw")
    # converted_filelist = os.listdir(f"save_files/{directory}/converted")

    # for filename in filelist:  # prevent duplicate conversions
    #     for converted_filename in converted_filelist:
    #         if filename.rsplit(".", 1)[0] == converted_filename.rsplit(".", 1)[0]:
    #             continue
    # if filename.rsplit(".", 1)[1] == "pdf"
    wdFormatPDF = 17
    word = win32com.client.Dispatch("Word.Application")
    global_var.global_var_setter(directory + filename, "processing")
    input_doc = os.path.abspath(f"save_files/{directory}/raw/{filename}")
    output_filename = filename.rsplit(".", 1)[0]
    output_pdf = os.path.abspath(f"save_files/{directory}/converted/{output_filename}.pdf")
    print(input_doc)
    print(output_pdf)
    global doc
    try:
        doc = word.Documents.Open(input_doc)
        doc.SaveAs(output_pdf, FileFormat=wdFormatPDF)
    except BaseException:
        global_var.global_var_setter(directory + filename, "error")  # free in files_dump.py but not implement
    else:
        global_var.global_var_setter(directory + filename, "success")
    finally:
        doc.Close()
        word.Quit()


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
    except:
        global_var.global_var_setter(directory + filename, "error")  # free in files_dump.py but not implement
    else:
        global_var.global_var_setter(directory + filename, "success")
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
    except:
        global_var.global_var_setter(directory + filename, "error")
    else:
        global_var.global_var_setter(directory + filename, "success")  # free in files_dump.py but not implement
