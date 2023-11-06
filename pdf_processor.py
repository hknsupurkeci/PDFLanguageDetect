# pdf_processor.py
import PyPDF2
import langid
import re
import pycountry

class PDFProcessor:
    def __init__(self, language_code):
        self.language_code = language_code

    @staticmethod
    def get_country_name_patterns():
        # Ülke isimleri ve resmi isimlerini al
        countries = [country.name for country in pycountry.countries]
        official_names = [country.official_name for country in pycountry.countries if hasattr(country, 'official_name')]
        all_names = set(countries + official_names)

        # Ülke isimlerinin her bir harfini büyük harf olarak ve kelime aralarında isteğe bağlı boşluklarla eşleştir
        all_names_patterns = []
        for name in all_names:
            pattern = ''.join([f"{char}\\s*" for char in name if char.isalpha()])  # Sadece alfabetik karakterler için
            all_names_patterns.append(pattern)

        return all_names_patterns

    @staticmethod
    def clean_text(text):
        # Ülke isimlerini regex pattern olarak al
        country_name_patterns = PDFProcessor.get_country_name_patterns()

        # Yapışık ülke isimlerini ve tek tek ülke isimlerini metinden çıkar
        for pattern in country_name_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Sayıları ve özel karakterleri çıkar
        clean_text = re.sub(r'\d+', '', text)
        clean_text = re.sub(r'[^\w\s]', '', clean_text)

        # İki karakterden kısa olan kelimeleri çıkar
        clean_text = ' '.join([word for word in clean_text.split() if len(word) > 2])

        # Fazladan boşlukları temizle
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

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
