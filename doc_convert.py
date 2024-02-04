import os
import win32com.client


def doc_convert(folder: str):
    filelist = os.listdir(f"save_files/{folder}/raw")
    for file in filelist:
        input_doc = os.path.abspath(f"save_files/{folder}/raw/{file}")
        output_filename = file.rsplit(".", 1)[0]
        output_pdf = os.path.abspath(f"save_files/{folder}/converted/{output_filename}.pdf")
        print(input_doc)
        print(output_pdf)
        wdFormatPDF = 17
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(input_doc)
        doc.SaveAs(output_pdf, FileFormat=wdFormatPDF)
        # doc = word.Documents.Open("C://Users/Administrator/PycharmProjects/self-service-printer/save_files/c95f7428-182a-4dbe-96e9-ae1faadaa7c5/raw/file.sample_1MB.doc")
        # doc.SaveAs("C://Users/1.pdf", FileFormat=wdFormatPDF)
        doc.Close()
        word.Quit()
