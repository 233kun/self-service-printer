import logging
from shutil import copyfile

import img2pdf
from pypdf import PdfReader

from global_vars.files_attributes_singleton import files_attributes_singleton


class ConvertUtil(object):
    @staticmethod
    def convert_dcos(self):
        pass


    @staticmethod
    def convert_excel(self):
        pass


    @staticmethod
    def convert_pdf(directory, filename):
        files_attributes_global = files_attributes_singleton()
        files_attributes = files_attributes_global.data.get(directory)

        for file_attributes in files_attributes:
            if file_attributes.filename == filename:
                file_attributes.convert_state = 'processing'
        files_attributes_global.data.update({directory: files_attributes})

        try:
            for file_attributes in files_attributes:
                if file_attributes.filename == filename:
                    copyfile(f'uploads/{directory}/raw/{filename}',
                             f'uploads/{directory}/converted/{filename}')
                    converted_filename = file_attributes.filename.rsplit(".", 1)[0] + '.pdf'
                    reader = PdfReader(
                        f"uploads/{directory}/converted/{converted_filename}")
                    file_attributes.total_pages = len(reader.pages)
                    file_attributes.print_range_end = len(reader.pages)
                    file_attributes.convert_state = 'success'
            files_attributes_global.data.update({directory: files_attributes})
        except Exception as e:
            for file_attributes in files_attributes:
                if file_attributes.filename == filename:
                    file_attributes.convert_state = 'error'
                    files_attributes_global.data.update({directory: files_attributes})
                    logging.error(f"Failed to convert file to PDF: {filename}")
                    logging.error(f"Exception: {e}")

    @staticmethod
    def convert_images(directory, filename):
        files_attributes_global = files_attributes_singleton()
        files_attributes = files_attributes_global.data.get(directory)

        for file_attributes in files_attributes:
            if file_attributes.filename == filename:
                file_attributes.convert_state = 'processing'
        files_attributes_global.data.update({directory: files_attributes})

        a4inpt = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
        layout_fun = img2pdf.get_layout_fun(a4inpt)
        output_filename = filename.rsplit(".", 1)[0]
        try:
            with open(f"uploads/{directory}/converted/{output_filename}.pdf", "wb") as f:
                f.write(img2pdf.convert(f"uploads/{directory}/raw/{filename}", layout_fun=layout_fun,
                                        rotation=img2pdf.Rotation.ifvaild))

                files_attributes = files_attributes_global.data.get(directory)
                for file_attributes in files_attributes:
                    if file_attributes.filename == filename:
                        file_attributes.convert_state = 'success'
                        converted_filename = file_attributes.filename.rsplit(".", 1)[0] + '.pdf'
                        reader = PdfReader(
                            f"uploads/{directory}/converted/{converted_filename}")
                        file_attributes.total_pages = len(reader.pages)
                        file_attributes.print_range_end = len(reader.pages)
                files_attributes_global.data.update({directory: files_attributes})

        except Exception as e:
            logging.error(f"Failed to convert file to PDF: {filename}")
            logging.error(f"Exception: {e}")
