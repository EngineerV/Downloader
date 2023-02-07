from pytube import YouTube, Playlist, exceptions as PYex
from threading import Thread
from PIL import Image, ImageTk
import http.client
import urllib.error
import customtkinter
import requests
import tkinter
import os

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


class App(customtkinter.CTk):
    def __init__(self, count=0):
        super().__init__()
        self.count = count
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
        self.tabview.tab("PLAYLIST ↓").grid_columnconfigure(0, weight=0)
        self.tabview.tab("PLAYLIST ↓").grid_columnconfigure(1, weight=1)

        # Виджеты вкладки VIDEO:
        # Кнопка проверки видео
        self.check_button = customtkinter.CTkButton(self.tabview.tab("VIDEO ↓"),
                                                    text="Проверить ссылку", command=self.check_btn)
        self.check_button.grid(column=0, row=0, sticky="ew", padx=10, pady=20)

        # Поле для вставки ссылки
        self.entry_link = customtkinter.CTkEntry(self.tabview.tab("VIDEO ↓"),
                                                 placeholder_text="https://www.youtube.com/watch", font=(None, 12))
        self.entry_link.grid(column=1, row=0, columnspan=2, sticky="ew", padx=10, pady=20)

        # Поле для получения и изменения названия полученного видео
        self.entry_name = customtkinter.CTkEntry(self.tabview.tab("VIDEO ↓"), placeholder_text="Название видео",
                                                 font=(None, 12))
        self.entry_name.grid(column=0, row=1, columnspan=3, sticky="new", padx=10, pady=10)

        # Базовое изображение (лого) в месте, где будет превью полученного видео
        self.im = customtkinter.CTkImage(dark_image=Image.open("logo.png"),
                                         size=(200, 150))
        self.im_label = customtkinter.CTkLabel(self.tabview.tab("VIDEO ↓"), text='', image=self.im)
        self.im_label.grid(column=0, row=2, sticky="new", padx=10, pady=10)

        # Текстовое поле с описанием полученного видео
        self.textbox = customtkinter.CTkTextbox(self.tabview.tab("VIDEO ↓"), height=150, font=(None, 12))
        self.textbox.grid(column=1, row=2, columnspan=2, padx=10, pady=10, sticky="new")

        # Поле с отображением места загрузки (сохранения) видео
        self.entry_path = customtkinter.CTkEntry(self.tabview.tab("VIDEO ↓"), placeholder_text=f'{os.getcwd()}',
                                                 font=(None, 12))
        self.entry_path.grid(column=1, row=3, columnspan=2, sticky="ew", padx=10, pady=10)

        # Кнопка для выбора места загрузки (сохранения) видео
        self.save_button = customtkinter.CTkButton(self.tabview.tab("VIDEO ↓"),
                                                   text="Выбрать путь", command=self.path_btn)
        self.save_button.grid(column=0, row=3, sticky="ew", padx=10, pady=10)

        # Кнопка загрузки видео
        self.download_button = customtkinter.CTkButton(self.tabview.tab("VIDEO ↓"), text='Скачать', state="disabled",
                                                       command=self.threading)
        self.download_button.grid(column=0, row=4, sticky='ew', padx=10, pady=10)

        # Шкала прогресса загрузки
        self.progressbar = customtkinter.CTkProgressBar(self.tabview.tab("VIDEO ↓"), mode='determinate')
        self.progressbar.grid(column=1, row=4, padx=10, pady=10, sticky="ew")
        self.progressbar.set(0)

        # Лэйбл с информацией о размере полученного видео и текущем размере загрузки
        self.label_size = customtkinter.CTkLabel(self.tabview.tab("VIDEO ↓"), text='0.0 Mb', font=(None, 10),
                                                 anchor='e')
        self.label_size.grid(column=2, row=4, padx=(0, 10), pady=10, sticky='new', ipadx=0)

        # Виджеты вкладки PLAYLIST:
        # Кнопка проверки плэйлиста
        self.check_button_playlist = customtkinter.CTkButton(self.tabview.tab("PLAYLIST ↓"),
                                                             text="Проверить ссылку", command=self.check_btn_playlist)
        self.check_button_playlist.grid(column=0, row=0, sticky="ew", padx=10, pady=20)

        # Поле для вставки ссылки
        self.entry_link_playlist = customtkinter.CTkEntry(self.tabview.tab("PLAYLIST ↓"),
                                                          placeholder_text="https://www.youtube.com/watch",
                                                          font=(None, 12))
        self.entry_link_playlist.grid(column=1, row=0, columnspan=2, sticky="ew", padx=10, pady=20)

        # Listbox для списка ссылок вилео из плэйлиста
        self.listbox = tkinter.Listbox(self.tabview.tab("PLAYLIST ↓"), selectmode='extended',
                                       font=(None, 12))
        self.listbox.grid(column=0, row=1, columnspan=3, padx=10, pady=10, sticky="ew")
        self.listbox.bind("<<ListboxSelect>>", self.selected)

        # Чекбокс для выделения (отмены выделения) всех полученных ссылок в Listbox
        self.var = tkinter.BooleanVar()
        self.checkbox = customtkinter.CTkCheckBox(self.tabview.tab("PLAYLIST ↓"), text="Select All",
                                                  command=self.selected_all, variable=self.var)
        self.checkbox.grid(column=0, row=2, padx=10, pady=10, sticky="w")

        # Лэйбл с информацией о количестве выбранных файлов
        self.label_count_playlist = customtkinter.CTkLabel(self.tabview.tab("PLAYLIST ↓"), text='0 / 0',
                                                           font=(None, 10), anchor='w')
        self.label_count_playlist.grid(column=1, row=2, padx=(10, 10), pady=10, sticky='ew', ipadx=0)

        # Лэйбл с информацией о размере полученного видео и текущем размере загрузки
        self.label_size_playlist = customtkinter.CTkLabel(self.tabview.tab("PLAYLIST ↓"), text='0.0 Mb',
                                                          font=(None, 10), anchor='e')
        self.label_size_playlist.grid(column=2, row=2, padx=(10, 10), pady=10, sticky='ew', ipadx=0)

        # Кнопка для выбора места загрузки (сохранения) playlist
        self.save_button_playlist = customtkinter.CTkButton(self.tabview.tab("PLAYLIST ↓"),
                                                            text="Выбрать путь", command=self.path_btn_playlist)
        self.save_button_playlist.grid(column=0, row=3, sticky="ew", padx=10, pady=10)

        # Поле с отображением места загрузки (сохранения) playlist
        self.entry_path_playlist = customtkinter.CTkEntry(self.tabview.tab("PLAYLIST ↓"),
                                                          placeholder_text=f'{os.getcwd()}',
                                                          font=(None, 12))
        self.entry_path_playlist.grid(column=1, row=3, columnspan=2, sticky="ew", padx=10, pady=10)

        # Кнопка для загрузки всех выделенных ссылок в Listbox
        self.download_button_playlist = customtkinter.CTkButton(self.tabview.tab("PLAYLIST ↓"), text='Скачать',
                                                                state="disabled", command=self.threading)
        self.download_button_playlist.grid(column=0, row=4, sticky='ew', padx=10, pady=10)

        #  Шкала прогресса загрузки
        self.progressbar_playlist = customtkinter.CTkProgressBar(self.tabview.tab("PLAYLIST ↓"), mode='determinate')
        self.progressbar_playlist.grid(column=1, columnspan=2, row=4, padx=10, pady=10, sticky="ew")
        self.progressbar_playlist.set(0.0)

    def check_btn(self):
        """Функция для кнопки проверки video"""
        try:
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
            if type(e) == http.client.IncompleteRead:
                print(f'****** {type(e)} ********')
                self.check_btn()
            else:
                tkinter.messagebox.showerror(title='Error', message='Что-то не так, повторите попытку')

    def check_btn_playlist(self):
        """Функция для кнопки проверки playlist"""
        try:
            check_link_playlist = self.entry_link_playlist.get()
            playlist = Playlist(check_link_playlist)
            if check_link_playlist == "":
                tkinter.messagebox.showerror(title='Error', message='Пожалуйста введите URL адрес плэйлиста')
            else:
                self.listbox.delete(0, 'end')
                END = playlist.length
                for num, url in enumerate(playlist.video_urls, 0):
                    self.listbox.insert(END, f'{num + 1}) {url}')
                self.download_button_playlist.configure(state='normal')
        except urllib.error.URLError:
            tkinter.messagebox.showerror(title='Error', message='Проверьте соединение с интернетом')
        except pytube.exceptions.RegexMatchError:
            tkinter.messagebox.showerror(title='Error', message='Пожалуйста введите правильный URL адрес видео')
        except KeyError:
            tkinter.messagebox.showerror(title='Error', message='Проверьте ссылку плэйлиста')
        except Exception as e:
            if type(e) == http.client.IncompleteRead:
                print(f'****** {type(e)} ********')
                self.check_btn_playlist()
            else:
                tkinter.messagebox.showerror(title='Error', message='Что-то не так, повторите попытку')

    def selected_all(self):
        """Функция checkbox для выделееия (снятия выделения) всех элементов из listbox"""
        if self.var.get():
            self.listbox.select_set(0, self.listbox.size())
        else:
            self.listbox.select_clear(0, self.listbox.size())
        selected_indices = self.listbox.curselection()
        selected_links = " ".join(self.listbox.get(i) for i in selected_indices)
        self.label_count_playlist.configure(text=f'{self.count} / {len(selected_links.split()[1::2])}')

    def selected(self, event):
        """Функция для получения выбранных элементов"""
        selected_indices = self.listbox.curselection()
        selected_links = " ".join(self.listbox.get(i) for i in selected_indices)
        self.label_count_playlist.configure(text=f'{self.count} / {len(selected_links.split()[1::2])}')

    def path_btn(self):
        """Функция для кнопки выбора пути сохранения video"""
        self.entry_path_playlist.delete(0, len(self.entry_path_playlist.get()))
        self.entry_path.insert(0, f'{customtkinter.filedialog.askdirectory()}')

    def path_btn_playlist(self):
        """Функция для кнопки выбора пути сохранения playlist"""
        self.entry_path_playlist.delete(0, len(self.entry_path_playlist.get()))
        self.entry_path_playlist.insert(0, f'{customtkinter.filedialog.askdirectory()}')

    def download_video(self):
        """Функция для кнопки загрузки video"""
        try:
            download_link = self.entry_link.get()
            file_name = self.entry_name.get()
            self.entry_path.configure(state="disabled")
            self.download_button.configure(state="disabled")
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

            yt = YouTube(download_link, on_progress_callback=on_progress)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
            stream.download(output_path=f'{self.entry_path.get()}', filename=f'{file_name}.mp4')
            tkinter.messagebox.showinfo(title='Download Complete', message='Video has been downloaded successfully.')
            self.entry_path.configure(state="normal")
            self.download_button.configure(state="normal")
        except Exception as e:
            if type(e) == http.client.IncompleteRead or type(e) == PYex.PytubeError:
                print(f'****** {type(e)} ********')
                self.download_video()
            else:
                print(e)
                tkinter.messagebox.showerror(title='Error', message='Что-то не так, повторите попытку')

    def download_playlist(self):
        """Функция для кнопки загрузки playlist"""
        try:
            def on_progress(stream, chunk, bytes_remaining):
                # the total size of the video
                total_size = stream.filesize
                # the size downloaded after the start
                bytes_downloaded = total_size - bytes_remaining
                # the percentage downloaded after the start
                percentage_completed = round(bytes_downloaded / total_size * 100) * 0.01
                # updating the progress bar value
                self.progressbar_playlist.set(percentage_completed)
                # updating the main window of the app
                self.label_size_playlist.configure(
                    text=f'{bytes_downloaded * 0.000001: .1f} / {total_size * 0.000001: .1f} Mb')

            selected_indices = self.listbox.curselection()
            selected_links = " ".join(self.listbox.get(i) for i in selected_indices).split()[1::2]
            self.entry_path_playlist.configure(state="disabled")
            self.download_button_playlist.configure(state="disabled")

            if self.entry_path_playlist.get() == '':
                path = os.getcwd()
            else:
                path = self.entry_path_playlist.get()

            for i in selected_links:
                yt_obj = YouTube(i, on_progress_callback=on_progress)
                if os.path.isfile(f'{path}/{yt_obj.title}.mp4'):
                    print("уже скачано")
                    self.label_count_playlist.configure(text=f'{self.count} / {len(selected_links)}')
                    continue
                else:
                    filters = yt_obj.streams.filter(progressive=True, file_extension='mp4')
                    filters.get_highest_resolution().download(output_path=f'{self.entry_path_playlist.get()}',
                                                              filename=f'{yt_obj.title}.mp4')
                    print(f'Uploaded {yt_obj.title}.mp4')

                    if self.count < len(selected_links):
                        self.count += 1
                    self.label_count_playlist.configure(text=f'{self.count} / {len(selected_links)}')
            tkinter.messagebox.showinfo(title='Download Complete',
                                        message='Selected videos uploaded successfully.')
            self.count = 0
            self.entry_path_playlist.configure(state="normal")
            self.download_button_playlist.configure(state="normal")
        except Exception as e:
            if type(e) == http.client.IncompleteRead or type(e) == PYex.PytubeError:
                print(f'****** {type(e)} ********')
                self.download_playlist()
            else:
                print(e)
                tkinter.messagebox.showerror(title='Error', message='Что-то не так, повторите попытку')

    def threading(self):
        try:

            if self.tabview.get() == 'VIDEO ↓':
                t1 = Thread(target=self.download_video)
                t1.start()
            else:
                t2 = Thread(target=self.download_playlist)
                t2.start()
        except Exception as e:
            print('4to to tyt ne tak')
            print(e)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    if os.path.isfile("img.jpg"):
        os.remove('img.jpg')
