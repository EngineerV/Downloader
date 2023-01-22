import urllib.error
import pytube.exceptions
from pytube import YouTube
from PIL import Image, ImageTk
import customtkinter
import requests
import tkinter
import os

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # Определяем Размер окна, название окна и запрещаем менять размер окна.
        self.title("Downloader")
        self.geometry("600x450")
        self.resizable(False, False)
        # Устанавливаем иконку приложения
        icon = ImageTk.PhotoImage(file="512png.png")
        self.tk.call('wm', 'iconphoto', self._w, icon)
        # Определяем виджет CTkTabview на котором будет вся навигация
        self.tabview = customtkinter.CTkTabview(self, width=580, height=380)
        self.tabview.grid(row=0, column=0, padx=(10, 10), pady=0, sticky="nsew")
        self.tabview.add("VIDEO ↓")
        self.tabview.add("PLAYLIST ↓")
        self.tabview.tab("VIDEO ↓").grid_columnconfigure(0, weight=0)
        self.tabview.tab("VIDEO ↓").grid_columnconfigure(1, weight=1)
        self.tabview.tab("VIDEO ↓").grid_columnconfigure(2, weight=2)
        self.tabview.tab("PLAYLIST ↓").grid_columnconfigure(0, weight=1)

        self.check_button = customtkinter.CTkButton(self.tabview.tab("VIDEO ↓"),
                                                    text="Проверить ссылку", command=self.check_btn)
        self.check_button.grid(column=0, row=0, sticky="ew", padx=10, pady=20)

        self.entry_link = customtkinter.CTkEntry(self.tabview.tab("VIDEO ↓"),
                                                 placeholder_text="https://www.youtube.com/watch", font=(None, 12))
        self.entry_link.grid(column=1, row=0, columnspan=2, sticky="ew", padx=10, pady=20)

        self.entry_name = customtkinter.CTkEntry(self.tabview.tab("VIDEO ↓"), placeholder_text="Название видео",
                                                 font=(None, 12))
        self.entry_name.grid(column=0, row=1, columnspan=3, sticky="new", padx=10, pady=10)

        self.im = customtkinter.CTkImage(dark_image=Image.open("logo.png"),
                                         size=(200, 150))
        self.im_label = customtkinter.CTkLabel(self.tabview.tab("VIDEO ↓"), text='', image=self.im)
        self.im_label.grid(column=0, row=2, sticky="new", padx=10, pady=10)

        self.textbox = customtkinter.CTkTextbox(self.tabview.tab("VIDEO ↓"), height=150, font=(None, 12))
        self.textbox.grid(column=1, row=2, columnspan=2, padx=10, pady=10, sticky="new")

        self.entry_path = customtkinter.CTkEntry(self.tabview.tab("VIDEO ↓"), placeholder_text=f'{os.getcwd()}',
                                                 font=(None, 12))
        self.entry_path.grid(column=1, row=3, columnspan=2, sticky="ew", padx=10, pady=10)

        self.save_button = customtkinter.CTkButton(self.tabview.tab("VIDEO ↓"),
                                                   text="Выбрать путь", command=self.path_btn)
        self.save_button.grid(column=0, row=3, sticky="ew", padx=10, pady=10)

        self.download_button = customtkinter.CTkButton(self.tabview.tab("VIDEO ↓"), text='Скачать', state="disabled",
                                                       command=self.download_btn)
        self.download_button.grid(column=0, row=4, sticky='ew', padx=10, pady=10)

        self.progressbar = customtkinter.CTkProgressBar(self.tabview.tab("VIDEO ↓"), mode='determinate')
        self.progressbar.grid(column=1, row=4, padx=10, pady=10, sticky="ew")
        self.progressbar.set(0)

        self.label_size = customtkinter.CTkLabel(self.tabview.tab("VIDEO ↓"), text='0.0 Mb', font=(None, 10),
                                                 anchor='e')
        self.label_size.grid(column=2, row=4, padx=(0, 10), pady=10, sticky='new', ipadx=0)

    def check_btn(self):  # Функция для кнопки проверки
        try:
            global check_link
            check_link = self.entry_link.get()
            if check_link == "":
                tkinter.messagebox.showerror(title='Error', message='Пожалуйста введите URL адрес видео')
            else:
                self.entry_name.delete(0, len(self.entry_name.get()))
                self.entry_name.insert(0, YouTube(self.entry_link.get()).title)
                url_image = YouTube(self.entry_link.get()).thumbnail_url
                response = requests.get(url_image)
                if response.status_code == 200:
                    with open("img.jpg", 'wb') as f:
                        f.write(response.content)

                self.im.configure(dark_image=Image.open("img.jpg"))
                self.textbox.insert('0.0', YouTube(self.entry_link.get()).description)
                self.textbox.configure(state='disabled')
                self.label_size.configure(
                    text=f'{YouTube(self.entry_link.get()).streams.get_highest_resolution().filesize * 0.000001: .1f} Mb')
                self.download_button.configure(state='normal')

        except urllib.error.URLError:
            tkinter.messagebox.showerror(title='Error', message='Проверьте соединение с интернетом')
        except pytube.exceptions.RegexMatchError:
            tkinter.messagebox.showerror(title='Error', message='Пожалуйста введите правильный URL адрес видео')
        except Exception as e:
            tkinter.messagebox.showerror(title='Error', message='Что то не так')
            print(type(e))

    def path_btn(self):  # Функция для кнопки выбора пути сохранения
        self.entry_path.insert(0, f'{customtkinter.filedialog.askdirectory()}')

    def download_btn(self):  # Функция для кнопки загрузки
        try:
            download_link = check_link
            file_name = self.entry_name.get()
            if file_name == "":
                file_name = YouTube(download_link).title

            def on_progress(stream, chunk, bytes_remaining):
                # the total size of the video
                total_size = stream.filesize
                # the size downloaded after the start
                bytes_downloaded = total_size - bytes_remaining
                # the percentage downloaded after the start
                percentage_completed = round(bytes_downloaded / total_size * 100) * 0.01
                # updating the progress bar value
                self.progressbar.set(percentage_completed)
                # updating the main window of the app
                self.label_size.configure(text=f'{bytes_downloaded * 0.000001: .1f} / {total_size * 0.000001: .1f} Mb')
                self.update()

            yt = YouTube(download_link, on_progress_callback=on_progress)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
            stream.download(output_path=f'{self.entry_path.get()}', filename=f'{file_name}.mp4')
            tkinter.messagebox.showinfo(title='Download Complete', message='Video has been downloaded successfully.')
        except Exception as e:
            print("log", e)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    if os.path.isfile("img.jpg"):
        os.remove('img.jpg')
