# pdf_processor.py
import PyPDF2
import langid
import re

class PDFProcessor:
    def __init__(self, language_code):
        self.language_code = language_code

    @staticmethod
    def clean_text(text):
        clean_text = re.sub(r'\d+', '', text)
        clean_text = re.sub(r'[^\w\s]', '', clean_text)
        clean_text = ' '.join([word for word in clean_text.split() if len(word) > 2])
        return clean_text

    def extract_language_segments(self, pdf_file, update_progress):
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            total_pages = len(reader.pages)

            for page_num in range(total_pages):
                page = reader.pages[page_num]
                text += page.extract_text()

                progress_ratio = (page_num + 1) / total_pages * 100
                update_progress(progress_ratio)

            text = self.clean_text(text)
            word_count = 20
            words = text.split()
            segments = [' '.join(words[i:i+word_count]) for i in range(0, len(words), word_count)]
            language_segments = []

            for segment in segments:
                detected_language, _ = langid.classify(segment)
                if detected_language == self.language_code:
                    clean_segment = re.sub(r'\s+', ' ', segment).strip()
                    if clean_segment and len(clean_segment) > 1:
                        language_segments.append(clean_segment)

            return language_segments
