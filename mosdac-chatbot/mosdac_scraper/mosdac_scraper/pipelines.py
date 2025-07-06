import os
import fitz  # PyMuPDF
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter

class FileDownloadPipeline(FilesPipeline):
    def item_completed(self, results, item, info):
        adapter = ItemAdapter(item)
        files = [{'url': x['url'], 'path': x['path'], 'checksum': x['checksum']} for ok, x in results if ok]
        adapter["file_metadata"] = files

        # Extract PDF text
        text_data = []
        for f in files:
            if f['path'].endswith(".pdf"):
                try:
                    path = os.path.join(self.store.basedir, f['path'])
                    doc = fitz.open(path)
                    text = "".join([page.get_text() for page in doc])
                    doc.close()
                    text_data.append({'file': f['path'], 'text': text})
                except Exception as e:
                    print(f"Failed to extract PDF: {f['path']}", e)
        adapter["pdf_text"] = text_data
        return item

class ImageDownloadPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        adapter = ItemAdapter(item)
        adapter["images"] = [x['path'] for ok, x in results if ok]
        return item
