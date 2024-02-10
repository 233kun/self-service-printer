import os
import win32com.client

import global_var


async def doc_convert(folder: str):
    filelist = os.listdir(f"save_files/{folder}/raw")
    converted_filelist = os.listdir(f"save_files/{folder}/converted")
    for filename in filelist:
        for converted_filename in converted_filelist:
            if filename == converted_filename:
                break
            # if filename.rsplit(".", 1)[1] == "pdf"
        global_var.global_var_setter(folder, "processing")
        input_doc = os.path.abspath(f"save_files/{folder}/raw/{filename}")
        output_filename = filename.rsplit(".", 1)[0]
        output_pdf = os.path.abspath(f"save_files/{folder}/converted/{output_filename}.pdf")
        print(input_doc)
        print(output_pdf)
        wdFormatPDF = 17
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(input_doc)
        try:
            doc.SaveAs(output_pdf, FileFormat=wdFormatPDF)
        except BaseException:
            global_var.global_var_setter(folder, "error")
        finally:
            doc.Close()
            word.Quit()
        global_var.global_var_setter(folder, "success")
