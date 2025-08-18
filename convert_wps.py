from pywpsrpc.rpcwpsapi import (createWpsRpcInstance, wpsapi)
from pywpsrpc import RpcIter

from global_vars.files_attributes_singleton import files_attributes_singleton


class ConvertWPS():

    def convert_word(directory, filename):

        hr, rpc = createWpsRpcInstance()
        hr, app = rpc.getWpsApplication()
        files_attributes_global = files_attributes_singleton()
        files_attributes = files_attributes_global.data.get(directory)

        for file_attributes in files_attributes:
            if file_attributes.filename == filename:
                file_attributes.convert_state = 'processing'
        files_attributes_global.data.update({directory: files_attributes})
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

        app.Quit(wpsapi.wdDoNotSaveChanges)
    def convert_excel(directory, filename):
        pass