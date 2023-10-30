import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import langid
from pdf_processor import PDFProcessor
import pycountry

class PDFApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("PDF Language Checker")
        self.setup_ui()
        self.processing_flag = False

    def setup_ui(self):
        label1 = tk.Label(self.window, text="PDF File:")
        label1.pack(pady=10)

        self.file_path = tk.StringVar()
        file_entry = tk.Entry(self.window, textvariable=self.file_path, width=40)
        file_entry.pack(pady=10)

        select_button = tk.Button(self.window, text="Select File", command=self.select_file)
        select_button.pack(pady=10)

        label2 = tk.Label(self.window, text="Language Code:")
        label2.pack(pady=10)

        self.language_code_combobox = ttk.Combobox(self.window, values=self.get_language_options())
        self.language_code_combobox.pack(pady=10)
        self.language_code_combobox.bind("<KeyRelease>", self.on_combobox_keyrelease)

        run_button = tk.Button(self.window, text="Run", command=self.run_processing)
        run_button.pack(pady=20)

        self.progress = tk.DoubleVar()
        frame = tk.Frame(self.window)
        frame.pack(pady=10)

        progress_bar = ttk.Progressbar(frame, variable=self.progress, maximum=100)
        progress_bar.pack(fill=tk.BOTH, expand=1)

        self.progress_label = tk.Label(frame, text="0%", font=("Arial", 7))
        self.progress_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def get_language_options(self):
        formatted_languages = []
        for language in pycountry.languages:
            if hasattr(language, 'alpha_2'):
                formatted_languages.append(f"{language.alpha_2} ({language.name})")
        return sorted(formatted_languages)

    def on_combobox_keyrelease(self, event):
        value = self.language_code_combobox.get()
        if value:
            filtered_languages = [lang for lang in self.get_language_options() if value.lower() in lang.lower()]
            self.language_code_combobox["values"] = filtered_languages
            self.language_code_combobox.delete(0, tk.END)
            self.language_code_combobox.insert(0, value)
            # Combobox'ı manuel olarak açmak için:
            # self.language_code_combobox.event_generate('<Down>')


    def update_progress(self, ratio):
        self.progress.set(ratio)
        self.progress_label.config(text=f"{ratio:.2f}%")
        self.window.update_idletasks()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.file_path.set(file_path)

    def run_processing(self):
        if self.processing_flag:
            messagebox.showinfo("Info", "Processing is already in progress.")
            return
        
        def threaded_function():
            try:
                pdf_file = self.file_path.get()
                language_code = self.language_code_combobox.get().split()[0]  # Kısaltmayı almak için
                processor = PDFProcessor(language_code)
                self.processing_flag = True
                found_segments = processor.extract_language_segments(pdf_file, self.update_progress)
                with open("result.txt", "w", encoding="utf-8") as f:
                    if found_segments:
                        f.write(f"Segments found in {pdf_file} for language {language_code}:\n")
                        f.write("\n".join(found_segments))
                    else:
                        f.write(f"No segments found in {pdf_file} for language {language_code}!")
                messagebox.showinfo("Info", "Results written to result.txt!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
            finally:
                self.processing_flag = False
                
        threading.Thread(target=threaded_function, daemon=True).start()

    def run(self):
        self.window.mainloop()
