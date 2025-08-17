import os
import tkinter as tk
from tkinter import filedialog, font
from PIL import Image
from playsound import playsound
import threading

OUTPUT_DIR = 'kucultulmus_resimler'
MAX_WIDTH = 1200
MAX_HEIGHT = 1080
JPEG_QUALITY = 85
SOUND_FILE = 'success.mp3'

class ResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Akıllı Resim Küçültücü v2")
        self.root.geometry("500x300")
        self.root.configure(bg="#f0f0f0")

        self.main_font = font.Font(family="Helvetica", size=12)
        self.button_font = font.Font(family="Helvetica", size=14, weight="bold")

        main_frame = tk.Frame(root, padx=20, pady=20, bg="#f0f0f0")
        main_frame.pack(expand=True, fill=tk.BOTH)

        info_label = tk.Label(main_frame, text="Yüksek çözünürlüklü resimlerinizi seçerek\nkolayca optimize edin.",
                              font=self.main_font, wraplength=450, justify=tk.CENTER, bg="#f0f0f0")
        info_label.pack(pady=(10, 20))

        self.process_button = tk.Button(main_frame, text="Resimleri Seç ve Küçült", font=self.button_font,
                                bg="#00b050", fg="white", pady=15, relief=tk.FLAT, 
                                activebackground="#00913a",  
                                command=self.start_processing)
        self.process_button.pack(fill=tk.X, pady=10)

        self.status_label = tk.Label(main_frame, text="İşlem için hazır.", font=self.main_font,
                                     fg="#555", bg="#f0f0f0")
        self.status_label.pack(pady=(20, 10))

    def start_processing(self):
        selected_files = filedialog.askopenfilenames(
            title="Yeniden Boyutlandırılacak Resimleri Seçin",
            filetypes=[('Resim Dosyaları', '*.jpg *.jpeg *.png *.gif *.bmp'), ('Tüm Dosyalar', '*.*')]
        )
        
        if not selected_files:
            self.status_label.config(text="Hiçbir dosya seçilmedi.")
            return

        self.process_button.config(state=tk.DISABLED, text="İşleniyor...")
        
        processing_thread = threading.Thread(
            target=self.process_images_thread, 
            args=(selected_files,)
        )
        processing_thread.start()

    def process_images_thread(self, files_to_process):
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        total_files = len(files_to_process)
        for i, input_path in enumerate(files_to_process):
            filename = os.path.basename(input_path)
            self.root.after(0, self.update_status, f"İşleniyor: {i+1}/{total_files} - {filename}")
            output_path = os.path.join(OUTPUT_DIR, filename)
            self.resize_image(input_path, output_path)

        self.root.after(0, self.show_completion_dialog, total_files)

    def update_status(self, message):
        self.status_label.config(text=message)

    def resize_image(self, input_path, output_path):
        try:
            with Image.open(input_path) as img:
                if img.width <= MAX_WIDTH and img.height <= MAX_HEIGHT:
                    img.save(output_path)
                    return
                
                ratio = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

                if output_path.lower().endswith(('.jpg', '.jpeg')):
                    if resized_img.mode in ('RGBA', 'P'):
                        resized_img = resized_img.convert('RGB')
                    resized_img.save(output_path, quality=JPEG_QUALITY, optimize=True)
                else:
                    resized_img.save(output_path)
        except Exception as e:
            print(f"Hata: {input_path} işlenemedi - {e}")

    def show_completion_dialog(self, count):
        self.status_label.config(text=f"İşlem tamamlandı! {count} resim işlendi.")
        self.process_button.config(state=tk.NORMAL, text="Yeni Resimleri Seç")

        if os.path.exists(SOUND_FILE):
            threading.Thread(target=playsound, args=(SOUND_FILE,)).start()

        dialog = tk.Toplevel(self.root)
        dialog.title("Başarılı!")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        canvas = tk.Canvas(dialog, width=100, height=100, bg="white", highlightthickness=0)
        canvas.pack(pady=(20, 10))

        message_label = tk.Label(dialog, text=f"{count} adet resim başarıyla işlendi!", font=self.main_font, bg="white")
        message_label.pack(pady=5)
        
        ok_button = tk.Button(dialog, text="Tamam", command=dialog.destroy, width=10, font=self.main_font)
        ok_button.pack(pady=15)
        
        self.animate_checkmark(canvas)
    
    def animate_checkmark(self, canvas, step=0):
        green_color = "#28a745"
        
        if step <= 50:
            angle = step * 7.2
            canvas.create_arc(10, 10, 90, 90, start=90, extent=-angle, outline=green_color, width=5, style=tk.ARC)
        elif step <= 70:
            x = 30 + (step - 50)
            y = 55 + (step - 50)
            canvas.create_line(30, 55, x, y, fill=green_color, width=5, capstyle=tk.ROUND)
        elif step <= 100:
            x = 50 + (step - 70)
            y = 75 - (step - 70) * 1.33
            canvas.create_line(50, 75, x, y, fill=green_color, width=5, capstyle=tk.ROUND)
        
        if step < 100:
            canvas.after(5, self.animate_checkmark, canvas, step + 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = ResizerApp(root)
    root.mainloop()
