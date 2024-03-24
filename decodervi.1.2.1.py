import PySimpleGUI as sg
import cv2
import os
import time

def get_quality(width, height):
    if width >= 1920 and height >= 1080:
        return "1080p"
    elif width >= 1280 and height >= 720:
        return "720p"
    elif width >= 854 and height >= 480:
        return "480p"
    elif width >= 640 and height >= 360:
        return "360p"
    elif width >= 426 and height >= 240:
        return "240p"
    else:
        return "Низкое разрешение"

def get_video_info(filename):
    try:
        # Открываем видео файл
        video_capture = cv2.VideoCapture(filename)
        
        # Проверяем, открылся ли файл успешно
        if not video_capture.isOpened():
            raise Exception("Не удалось открыть видео файл.")
        
        # Получаем длительность видео в секундах
        duration_seconds = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) / video_capture.get(cv2.CAP_PROP_FPS)
        
        # Получаем размер файла в мегабайтах
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        
        # Получаем разрешение видео
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Получаем качество изображения
        quality = get_quality(width, height)
        
        # Закрываем видео файл
        video_capture.release()
        
        return duration_seconds, file_size_mb, (width, height), quality
    except Exception as e:
        raise e

def get_video_codec(filename):
    try:
        # Открываем видео файл
        video_capture = cv2.VideoCapture(filename)
        
        # Проверяем, открылся ли файл успешно
        if not video_capture.isOpened():
            raise Exception("Не удалось открыть видео файл.")
        
        # Получаем кодек
        codec = int(video_capture.get(cv2.CAP_PROP_FOURCC))
        
        # Закрываем видео файл
        video_capture.release()
        
        # Преобразуем числовой кодек в название
        codec_chars = "".join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])
        codec_name = codec_chars.strip('\x00')
        
        return codec_name
    except Exception as e:
        raise e

def convert_video(input_file, output_file, fourcc, window):
    try:
        input_video = cv2.VideoCapture(input_file)
        total_frames = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        output_video = cv2.VideoWriter(output_file, fourcc, 25.0, (width, height), True)
        
        # Рассчитываем оценочное время обработки
        start_time = time.time()  # Запоминаем время начала обработки
        estimated_total_time = total_frames / 25 / 60  # Оценочное время в минутах
        
        window["-CONVERT_STATUS-"].update(f"Процесс запущен.Время обработки: {estimated_total_time:.2f} мин")
        
        current_frame = 0
        while True:
            ret, frame = input_video.read()
            if ret:
                output_video.write(frame)
                current_frame += 1
                percent_complete = int((current_frame / total_frames) * 100)
                window["-PROGRESS_BAR-"].update(percent_complete)
                window["-PERCENTAGE-"].update(f"{percent_complete}%")
            else:
                break
        
        input_video.release()
        output_video.release()
        
        # Вычисляем реальное время обработки и выводим его
        end_time = time.time()  # Запоминаем время завершения обработки
        processing_time = end_time - start_time  # Вычисляем общее время обработки
        window["-CONVERT_STATUS-"].update(f"Видео успешно сконвертировано. Затраченное время: {processing_time:.2f} сек")

        return True
    except Exception as e:
        raise e


def main():
    # Вкладка "Проверка видео кодека"
    check_layout = [
        [sg.Text("Выберите видео файл:")],
        [sg.InputText(key="-FILE-"), sg.FileBrowse("Выбрать файл")],
        [sg.Button("Проверить")],
        [sg.Multiline(size=(50, 10), key="-OUTPUT-", autoscroll=True)],
    ]
    
    # Вкладка "Реформатирование"
    convert_layout = [
    [sg.Text("Выберите видео файл:")],
    [sg.InputText(key="-INPUT_FILE-"), sg.FileBrowse("Выбрать файл")],
    [sg.Text("Выберите кодек:")],
    [sg.InputCombo(("DIVX", "XVID", "MP4V"), key="-CODEC-")],
    [sg.Button("Конвертировать")],
    [sg.ProgressBar(100, orientation='h', size=(20, 20), key="-PROGRESS_BAR-"), sg.Text("0%", size=(4, 1), key="-PERCENTAGE-")],
    [sg.Text("", size=(40, 1), key="-CONVERT_STATUS-")],
    [sg.Text("Описание кодеков:")],
    [sg.Text("DIVX — Обеспечивает хорошее соотношение качества и размера файла.")],
    [sg.Text("XVID — Более оптимизированный и быстрый кодек.")],
    [sg.Text("MP4V — Хорошее качество видео при сравнительно низком объеме файла.")]
]

    
    # Общий макет с двумя вкладками
    layout = [
        [sg.TabGroup([
            [sg.Tab("Проверка видеокодека", check_layout), 
             sg.Tab("Изменение видеокодека", convert_layout)]
        ])]
    ]

    window = sg.Window("DcoderVI 1.2.1 by f0bas", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Проверить":
            filename = values["-FILE-"]
            if filename:
                try:
                    codec_name = get_video_codec(filename)
                    duration_seconds, file_size_mb, resolution, quality = get_video_info(filename)
                    window["-OUTPUT-"].print(f"Название видео кодека: {codec_name}\nРазмер файла: {file_size_mb:.2f} МБ\nРазрешение видео: {resolution[0]}x{resolution[1]}\nКачество изображения: {quality}\n")
                except Exception as e:
                    window["-OUTPUT-"].print(f"Ошибка при проверке видео: {e}\n", end="")
        elif event == "Конвертировать":
            input_file = values["-INPUT_FILE-"]
            codec = values["-CODEC-"]
            if input_file and codec:
                try:
                    output_file = os.path.splitext(input_file)[0] + "_converted.avi"
                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    success = convert_video(input_file, output_file, fourcc, window)
                    if success:
                        window["-CONVERT_STATUS-"].update("Видео успешно сконвертировано")
                except Exception as e:
                    window["-CONVERT_STATUS-"].update(f"Ошибка при конвертировании видео: {e}")

    window.close()

if __name__ == "__main__":
    main()