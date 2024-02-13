import os
import win32com.client

import global_var


def doc_convert(directory: str):
    filelist = os.listdir(f"save_files/{directory}/raw")
    converted_filelist = os.listdir(f"save_files/{directory}/converted")
    wdFormatPDF = 17
    word = win32com.client.Dispatch("Word.Application")
    for filename in filelist:  # prevent duplicate conversions
        for converted_filename in converted_filelist:
            if filename.rsplit(".", 1)[0] == converted_filename.rsplit(".", 1)[0]:
                continue
            # if filename.rsplit(".", 1)[1] == "pdf"
        global_var.global_var_setter(directory + filename, "processing")
        input_doc = os.path.abspath(f"save_files/{directory}/raw/{filename}")
        output_filename = filename.rsplit(".", 1)[0]
        output_pdf = os.path.abspath(f"save_files/{directory}/converted/{output_filename}.pdf")
        print(input_doc)
        print(output_pdf)
        global doc
        try:
            doc = word.Documents.Open(input_doc)
            print(1)
            doc.SaveAs(output_pdf, FileFormat=wdFormatPDF)
            print(2)
        except BaseException:
            global_var.global_var_setter(directory + filename, "error")
        else:
            global_var.global_var_setter(directory + filename, "success")
        finally:
            doc.Close()
            print(directory + filename)
    word.Quit()
