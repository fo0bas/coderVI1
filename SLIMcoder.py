import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import os
import threading

def get_video_info(filename):
    try:
        video_capture = cv2.VideoCapture(filename)

        if not video_capture.isOpened():
            raise Exception("Не удалось открыть видео файл.")

        codec_name = get_video_codec(filename)
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        extension = os.path.splitext(filename)[1]

        video_capture.release()

        return codec_name, file_size_mb, width, height, extension
    except Exception as e:
        raise e

def get_video_codec(filename):
    try:
        video_capture = cv2.VideoCapture(filename)

        if not video_capture.isOpened():
            raise Exception("Не удалось открыть видео файл.")

        codec = int(video_capture.get(cv2.CAP_PROP_FOURCC))
        codec_chars = "".join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])
        codec_name = codec_chars.strip('\x00')

        video_capture.release()

        return codec_name
    except Exception as e:
        raise e

def check_file_info(filename, output_text_widget):
    try:
        codec_name, file_size_mb, width, height, extension = get_video_info(filename)

        output_text = (
            f"Название видео кодека: {codec_name}\n"
            f"Размер файла: {file_size_mb:.2f} МБ\n"
            f"Разрешение видео: {width}x{height}\n"
            f"Расширение файла: {extension}\n"
        )

        output_text_widget.delete(1.0, tk.END)
        output_text_widget.insert(tk.END, output_text)
    except Exception as e:
        output_text_widget.delete(1.0, tk.END)
        output_text_widget.insert(tk.END, f"Ошибка при проверке файла: {e}")

def convert_video(input_file, output_file, fourcc, progress_bar, status_label):
    try:
        input_video = cv2.VideoCapture(input_file)
        total_frames = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        output_video = cv2.VideoWriter(output_file, fourcc, 25.0, (width, height), True)

        current_frame = 0

        while True:
            ret, frame = input_video.read()
            if ret:
                output_video.write(frame)
                current_frame += 1

                # Обновляем прогресс
                percent_complete = int((current_frame / total_frames) * 100)
                progress_bar['value'] = percent_complete

            else:
                break

        input_video.release()
        output_video.release()

        status_label.config(text="Видео успешно сконвертировано")
    except Exception as e:
        status_label.config(text=f"Ошибка при конвертации видео: {e}")

def convert_file(input_file, codec, progress_bar, status_label):
    output_file = os.path.splitext(input_file)[0] + "_converted.avi"
    fourcc = cv2.VideoWriter_fourcc(*codec)

    t = threading.Thread(target=convert_video, args=(input_file, output_file, fourcc, progress_bar, status_label))
    t.start()

def main():
    root = tk.Tk()
    root.title("SLIMdecoder 1.2.2")

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Вкладка "Проверка файла"
    check_tab = ttk.Frame(tab_control)
    tab_control.add(check_tab, text="Проверка файла")

    check_entry_label = ttk.Label(check_tab, text="Выберите видео файл:")
    check_entry_label.pack(pady=10)

    check_entry = ttk.Entry(check_tab, width=40)
    check_entry.pack(pady=10)

    def browse_file_check():
        filename = filedialog.askopenfilename()
        check_entry.delete(0, tk.END)
        check_entry.insert(0, filename)

    browse_button_check = ttk.Button(check_tab, text="Выбрать файл", command=browse_file_check)
    browse_button_check.pack(pady=10)

    check_output_text = tk.Text(check_tab, width=50, height=10)
    check_output_text.pack(pady=10)

    check_button = ttk.Button(check_tab, text="Проверить", command=lambda: check_file_info(check_entry.get(), check_output_text))
    check_button.pack(pady=10)

    # Вкладка "Конвертирование"
    convert_tab = ttk.Frame(tab_control)
    tab_control.add(convert_tab, text="Конвертирование")

    convert_entry_label = ttk.Label(convert_tab, text="Выберите видео файл:")
    convert_entry_label.pack(pady=10)

    convert_entry = ttk.Entry(convert_tab, width=40)
    convert_entry.pack(pady=10)

    def browse_file_convert():
        filename = filedialog.askopenfilename()
        convert_entry.delete(0, tk.END)
        convert_entry.insert(0, filename)

    browse_button_convert = ttk.Button(convert_tab, text="Выбрать файл", command=browse_file_convert)
    browse_button_convert.pack(pady=10)

    codec_label = ttk.Label(convert_tab, text="Выберите кодек:")
    codec_label.pack(pady=10)

    codec_combobox = ttk.Combobox(convert_tab, values=("DIVX", "XVID", "MP4V"), width=37)
    codec_combobox.pack(pady=10)

    convert_progress_bar = ttk.Progressbar(convert_tab, orient=tk.HORIZONTAL, length=200, mode='determinate')
    convert_progress_bar.pack(pady=10)

    convert_status_label = ttk.Label(convert_tab, text="")
    convert_status_label.pack(pady=10)

    def start_conversion():
        input_file = convert_entry.get()
        selected_codec = codec_combobox.get()

        if input_file and selected_codec:
            convert_file(input_file, selected_codec, convert_progress_bar, convert_status_label)

    convert_button = ttk.Button(convert_tab, text="Конвертировать", command=start_conversion)
    convert_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
