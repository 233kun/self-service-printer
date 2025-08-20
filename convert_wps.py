import logging
import traceback

from pypdf import PdfReader
from pywpsrpc.rpcetapi import createEtRpcInstance
from pywpsrpc.rpcwpsapi import (createWpsRpcInstance, wpsapi)
from pywpsrpc import RpcIter

from convert_util import ConvertUtil
from global_vars.files_attributes_singleton import files_attributes_singleton


class ConvertWPS(ConvertUtil):
    @staticmethod
    def convert_docs(directory, filename):
        hr, rpc = createWpsRpcInstance()
        hr, app = rpc.getWpsApplication()
        files_attributes_global = files_attributes_singleton()
        files_attributes = files_attributes_global.data.get(directory)

        for file_attributes in files_attributes:
            if file_attributes.filename == filename:
                file_attributes.convert_state = 'processing'
        files_attributes_global.data.update({directory: files_attributes})
        try:
            hr, doc = app.Documents.Open(f'uploads/{directory}/raw/{filename}')
            def onDocumentBeforeSave(doc):
                print("onDocumentBeforeSave called for doc: ", doc.Name)
                return True, False

            rpc.registerEvent(app,
                              wpsapi.DIID_ApplicationEvents4,
                              "DocumentBeforeSave",
                              onDocumentBeforeSave)

            output_filename = filename.rsplit(".", 1)[0] + '.pdf'
            doc.SaveAs2(f'uploads/{directory}/converted/{output_filename}', 17)

            for file_attributes in files_attributes:
                if file_attributes.filename == filename:
                    file_attributes.convert_state = 'success'
                    converted_filename = file_attributes.filename.rsplit(".", 1)[0] + '.pdf'
                    reader = PdfReader(f"uploads/{directory}/converted/{converted_filename}")
                    file_attributes.total_pages = len(reader.pages)
                    file_attributes.print_range_end = len(reader.pages)

            files_attributes_global.data.update({directory: files_attributes})
        except Exception as e:
            for file_attributes in files_attributes:
                if file_attributes.filename == filename:
                    file_attributes.convert_state = 'error'
            files_attributes_global.data.update({directory: files_attributes})
            print(e)
            logging.error(f'Exception while converting DOC\nFilename: {filename}', e)
        finally:
            app.Quit(wpsapi.wdDoNotSaveChanges)

    @staticmethod
    def convert_excel(directory, filename):
        hr, rpc = createEtRpcInstance()
        hr, app = rpc.getEtApplication()