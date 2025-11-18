import sys
import time
import os
import hashlib
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# Импортируем функции из vce.py
import vce


class AndroidADBClient:
    """Клиент для работы с Android устройством через ADB"""

    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.adb_path = self.get_adb_path()

    def get_adb_path(self):
        """Возвращает абсолютный путь к adb.exe"""
        # Определяем базовый путь: к директории запущенной программы или распакованного exe
        if getattr(sys, 'frozen', False):
            # Если программа собрана в exe (PyInstaller)
            base_path = os.path.dirname(sys.executable)  # <-- Ключевое изменение!
        else:
            # Если запущена как скрипт Python
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Формируем путь к adb.exe
        adb_path = os.path.join(base_path, 'adb', 'adb.exe')

        # Проверяем существование файла
        if not os.path.exists(adb_path):
            raise FileNotFoundError(f"ADB не найден по пути: {adb_path}")

        return adb_path

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def decode_output(self, byte_string):
        """Декодирует вывод ADB с правильной кодировкой"""
        encodings = ['cp866', 'utf-8', 'windows-1251', 'iso-8859-1']

        for encoding in encodings:
            try:
                return byte_string.decode(encoding)
            except UnicodeDecodeError:
                continue

        # Если ни одна кодировка не подошла, возвращаем с заменой ошибок
        return byte_string.decode('utf-8', errors='replace')

    def run_adb_command(self, command, check_returncode=True):
        """Выполняет ADB команду с правильной кодировкой"""
        full_command = [self.adb_path] + command
        self.log(f"Выполняется: {' '.join(full_command)}")

        try:
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=False,  # Получаем байты
                check=check_returncode
            )

            # Декодируем вывод
            if result.stdout:
                stdout_text = self.decode_output(result.stdout).strip()
                if stdout_text:
                    self.log(stdout_text)

            return result

        except subprocess.CalledProcessError as e:
            # Декодируем ошибки
            error_msg = "Ошибка выполнения команды"

            if e.stdout:
                stdout_text = self.decode_output(e.stdout).strip()
                if stdout_text:
                    error_msg += f"\nSTDOUT: {stdout_text}"

            if e.stderr:
                stderr_text = self.decode_output(e.stderr).strip()
                if stderr_text:
                    error_msg += f"\nSTDERR: {stderr_text}"

            self.log(error_msg)
            raise
        except Exception as e:
            self.log(f"Ошибка выполнения команды: {str(e)}")
            raise

    def set_adb_root_key(self):
        """Устанавливает ADB root key как в bat-скрипте"""
        try:
            # Получаем серийный номер
            result = self.run_adb_command(['shell', 'getprop', 'ro.serialno'])
            serialno = self.decode_output(result.stdout).strip()

            # Вычисляем MD5 хеш
            input_string = f"{serialno}Harman@SH--"
            md5_hash = hashlib.md5(input_string.encode()).hexdigest()

            # Устанавливаем свойство
            self.run_adb_command(['shell', f'setprop service.adb.root.hkey {md5_hash}'])
            self.log(f"Установлен ADB root key: {md5_hash}")
            return True

        except Exception as e:
            self.log(f"Ошибка установки ADB root key: {e}")
            return False

    def adb_root(self):
        """Выполняет adb root"""
        try:
            self.run_adb_command(['root'])
            self.log("ADB root выполнен успешно")
            return True
        except Exception as e:
            self.log(f"Ошибка выполнения adb root: {e}")
            return False

    def pull_config(self, remote_path, local_path):
        """Скачивает файл конфигурации с устройства"""
        try:
            self.run_adb_command(['pull', remote_path, local_path])
            self.log(f"Файл {remote_path} скачан как {local_path}")
            return True
        except Exception as e:
            self.log(f"Ошибка скачивания файла: {e}")
            return False

    def push_config(self, local_path, remote_path):
        """Загружает файл конфигурации на устройство"""
        try:
            self.run_adb_command(['push', local_path, remote_path])
            self.log(f"Файл {local_path} загружен как {remote_path}")
            return True
        except Exception as e:
            self.log(f"Ошибка загрузки файла: {e}")
            return False

    def reboot_device(self):
        """Перезагружает устройство"""
        try:
            self.run_adb_command(['shell', 'reboot'])
            self.log("Устройство перезагружается...")
            return True
        except Exception as e:
            self.log(f"Ошибка перезагрузки устройства: {e}")
            return False


class ConfigWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.property_vars = {}  # Словарь для хранения переменных параметров
        try:
            self.adb_client = AndroidADBClient(log_callback=self.log_message)
            self.init_ui()
        except FileNotFoundError as e:
            self.show_error_and_exit(str(e))
        except Exception as e:
            self.show_error_and_exit(f"Ошибка инициализации: {str(e)}")

    def show_error_and_exit(self, message):
        """Показывает ошибку и завершает программу"""
        error_window = tk.Tk()
        error_window.title("Ошибка")
        error_window.geometry("400x200")

        ttk.Label(error_window, text="Критическая ошибка", font=('Arial', 12, 'bold')).pack(pady=10)
        ttk.Label(error_window, text=message, wraplength=380).pack(pady=10, padx=10)
        ttk.Label(error_window, text="Программа будет закрыта", font=('Arial', 10)).pack(pady=10)

        ttk.Button(error_window, text="OK",
                   command=lambda: [error_window.destroy(), self.root.destroy(), sys.exit(1)]).pack(pady=10)

        error_window.mainloop()

    def init_ui(self):
        self.root.title('JolionConfigSetGui (Сначала включить ADB на ГУ!!!, потом подключиться. ГУ и ноут в одной WIFI сети)')
        self.root.geometry('800x700')

        # Основной frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов строк и столбцов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Группа для настроек ADB
        adb_group = ttk.LabelFrame(main_frame, text="Настройки ADB подключения", padding="10")
        adb_group.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        adb_group.columnconfigure(1, weight=1)

        # Поле для IP устройства
        ttk.Label(adb_group, text='IP устройства:').grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ip_input = ttk.Entry(adb_group)
        self.ip_input.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.ip_input.insert(0, '')

        # Поле для порта ADB
        ttk.Label(adb_group, text='Порт ADB:').grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.port_input = ttk.Entry(adb_group)
        self.port_input.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        self.port_input.insert(0, '5555')

        # Кнопка подключения
        self.connect_button = ttk.Button(adb_group, text='Подключиться и загрузить конфигурацию',
                                         command=self.connect_and_load_config_threaded)
        self.connect_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Группа для параметров конфигурации
        self.config_group = ttk.LabelFrame(main_frame, text="Параметры конфигурации", padding="10")
        self.config_group.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        self.config_group.columnconfigure(0, weight=1)
        self.config_group.rowconfigure(0, weight=1)

        # Создаем скроллируемую область для параметров
        self.create_scrollable_config_area()

        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.start_button = ttk.Button(buttons_frame, text='Применить изменения на устройстве',
                                       command=self.on_start_threaded)
        self.clear_button = ttk.Button(buttons_frame, text='Очистить логи',
                                       command=self.on_clear_logs)

        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        self.clear_button.pack(side=tk.LEFT)

        # Информация о пути ADB
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(info_frame, text=f"ADB путь: {self.adb_client.adb_path}",
                  font=('Courier New', 8), foreground='gray').pack(side=tk.LEFT)

        # Поле для логов
        log_group = ttk.LabelFrame(main_frame, text="Логи выполнения", padding="10")
        log_group.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(5, weight=1)
        log_group.columnconfigure(0, weight=1)
        log_group.rowconfigure(0, weight=1)

        self.log_output = scrolledtext.ScrolledText(log_group, height=15,
                                                    font=('Courier New', 9),
                                                    background='#f5f5f5')
        self.log_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

    def create_scrollable_config_area(self):
        """Создает скроллируемую область для отображения параметров конфигурации"""
        # Создаем фрейм с canvas и scrollbar
        canvas_frame = ttk.Frame(self.config_group)
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Привязываем события мыши для прокрутки колесиком
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Заголовок для параметров
        ttk.Label(self.scrollable_frame, text="Параметр", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5,
                                                                                           pady=2, sticky=tk.W)
        ttk.Label(self.scrollable_frame, text="Текущее значение", font=('Arial', 10, 'bold')).grid(row=0, column=1,
                                                                                                   padx=5, pady=2,
                                                                                                   sticky=tk.W)
        ttk.Label(self.scrollable_frame, text="Новое значение", font=('Arial', 10, 'bold')).grid(row=0, column=2,
                                                                                                 padx=5, pady=2,
                                                                                                 sticky=tk.W)
        ttk.Label(self.scrollable_frame, text="Биты", font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=5, pady=2,
                                                                                       sticky=tk.W)

    def log_message(self, message):
        """Добавляет сообщение в лог с временной меткой"""

        def update_log():
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.log_output.insert(tk.END, formatted_message + '\n')
            self.log_output.see(tk.END)
            self.root.update_idletasks()

        self.root.after(0, update_log)

    def connect_and_load_config(self):
        """Подключается к Android устройству и загружает конфигурацию"""
        ip = self.ip_input.get().strip()
        port = self.port_input.get().strip()

        if not ip:
            messagebox.showwarning("Ошибка", "Введите IP адрес устройства")
            return

        try:
            self.log_message(f"Подключение к устройству {ip}:{port}...")
            self.adb_client.run_adb_command(['connect', f'{ip}:{port}'])

            self.log_message("Установка ADB root key...")
            if not self.adb_client.set_adb_root_key():
                raise Exception("Не удалось установить ADB root key")

            self.log_message("Выполнение adb root...")
            if not self.adb_client.adb_root():
                raise Exception("Не удалось выполнить adb root")

            self.log_message("Скачивание конфигурации с устройства...")
            if not self.adb_client.pull_config(
                    '/data/vendor/vehicleinfo/VehicleConfig.bin',
                    'VehicleConfig.bin'
            ):
                raise Exception("Не удалось скачать конфигурацию")

            self.log_message("✅ Подключение установлено и конфигурация скачана")
            self.status_var.set("Конфигурация загружена")

            # Загружаем и отображаем параметры конфигурации
            self.load_and_display_config()

        except Exception as e:
            self.log_message(f"❌ Ошибка подключения: {e}")
            self.status_var.set("Ошибка подключения")

    def connect_and_load_config_threaded(self):
        """Запускает подключение и загрузку конфигурации в отдельном потоке"""
        thread = threading.Thread(target=self.connect_and_load_config)
        thread.daemon = True
        thread.start()

    def load_and_display_config(self):
        """Загружает конфигурацию из bin-файла и отображает параметры"""
        try:
            # Читаем карту свойств и конфигурацию
            map_path = 'haval_jolion.json'
            src_path = 'VehicleConfig.bin'

            self.log_message("Чтение карты свойств...")
            prop_map = vce.readMap(map_path)

            self.log_message("Чтение конфигурации...")
            data = vce.readConfig(src_path)

            self.log_message("Проверка конфигурации...")
            vce.validateConfig(data, prop_map)

            # Очищаем старые параметры
            for widget in self.scrollable_frame.winfo_children():
                if hasattr(widget, 'grid_info') and widget.grid_info()['row'] > 0:
                    widget.destroy()

            self.property_vars = {}
            position_table = vce.getPositionTable(prop_map)

            # Создаем элементы управления для каждого параметра
            row = 1
            for property_name, position_str in position_table.items():
                if property_name == vce.kProjectCodeProperty:
                    continue  # Пропускаем код проекта

                position = vce.Position(position_str)
                bit_length = position.high_bit - position.low_bit + 1

                # Читаем текущее значение
                current_bitstr = vce.readBits(data, position)
                current_value = int(current_bitstr, 2)

                # Отображаем параметр
                ttk.Label(self.scrollable_frame, text=property_name).grid(row=row, column=0, padx=5, pady=2,
                                                                          sticky=tk.W)
                ttk.Label(self.scrollable_frame, text=str(current_value)).grid(row=row, column=1, padx=5, pady=2,
                                                                               sticky=tk.W)

                # Создаем поле для ввода нового значения
                var = tk.StringVar(value=str(current_value))
                entry = ttk.Entry(self.scrollable_frame, textvariable=var, width=10)
                entry.grid(row=row, column=2, padx=5, pady=2, sticky=tk.W)

                # Отображаем битовый диапазон
                bits_label = f"[{position.byte_idx}][{position.high_bit}:{position.low_bit}]"
                ttk.Label(self.scrollable_frame, text=bits_label).grid(row=row, column=3, padx=5, pady=2, sticky=tk.W)

                self.property_vars[property_name] = (var, position, bit_length)
                row += 1

            self.log_message(f"✅ Загружено {len(self.property_vars)} параметров конфигурации")

        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки конфигурации: {str(e)}")

    def process_configuration(self):
        """Обрабатывает конфигурацию с использованием функций из vce.py"""
        try:
            # Параметры файлов
            map_path = 'haval_jolion.json'
            src_path = 'VehicleConfig.bin'
            dst_path = 'NewVehicleConfig.bin'

            self.log_message("Чтение карты свойств...")
            prop_map = vce.readMap(map_path)

            self.log_message("Чтение конфигурации...")
            data = vce.readConfig(src_path)

            self.log_message("Проверка конфигурации...")
            vce.validateConfig(data, prop_map)

            updated = False

            # Обрабатываем каждое свойство
            for property_name, (var, position, bit_length) in self.property_vars.items():
                try:
                    new_value_str = var.get().strip()
                    if not new_value_str:
                        continue  # Пропускаем пустые значения

                    new_value = int(new_value_str)

                    # Проверяем, что значение входит в допустимый диапазон
                    max_value = (1 << bit_length) - 1
                    if new_value < 0 or new_value > max_value:
                        self.log_message(
                            f"⚠️ Параметр {property_name}: значение {new_value} вне диапазона [0-{max_value}]")
                        continue

                    # Записываем новое значение
                    vce.writeNumber(data, position, new_value)
                    self.log_message(f"Установка {property_name} = {new_value}")
                    updated = True

                except ValueError:
                    self.log_message(f"⚠️ Некорректное значение для параметра {property_name}: '{var.get()}'")
                except Exception as e:
                    self.log_message(f"❌ Ошибка установки параметра {property_name}: {str(e)}")

            if updated:
                self.log_message("Сохранение обновленной конфигурации...")
                data[-1] = vce.calcCrc8(data[:-1])
                vce.writeConfig(dst_path, data)
                self.log_message("✅ Конфигурация успешно обновлена")
                return True
            else:
                self.log_message("⚠️ Конфигурация не была изменена")
                return False

        except Exception as e:
            self.log_message(f"❌ Ошибка при обработке конфигурации: {str(e)}")
            return False

    def on_start(self):
        """Выполняет полную последовательность как в bat-скрипте"""
        try:
            self.status_var.set("Выполняется настройка...")
            self.log_message("🚀 Начало выполнения полной последовательности...")

            # Обработка конфигурации
            self.log_message("1. Обработка конфигурации...")
            if not self.process_configuration():
                raise Exception("Не удалось обработать конфигурацию")

            # Push обновленной конфигурации
            self.log_message("2. Загрузка обновленной конфигурации на устройство...")
            if not self.adb_client.push_config(
                    'NewVehicleConfig.bin',
                    '/data/vendor/vehicleinfo/VehicleConfig.bin'
            ):
                raise Exception("Не удалось загрузить конфигурацию на устройство")

            # Перезагрузка устройства
            self.log_message("3. Перезагрузка устройства...")
            self.log_message("✅ Настройки применены, перезагрузка...")

            if not self.adb_client.reboot_device():
                raise Exception("Не удалось перезагрузить устройство")

            self.log_message("🎉 Полная последовательность выполнена успешно!")
            self.status_var.set("Готов к работе")

        except Exception as e:
            self.log_message(f"❌ Ошибка выполнения: {str(e)}")
            self.status_var.set("Ошибка выполнения")

    def on_start_threaded(self):
        """Запускает выполнение в отдельном потоке"""
        thread = threading.Thread(target=self.on_start)
        thread.daemon = True
        thread.start()

    def on_clear_logs(self):
        """Очистка логов"""
        self.log_output.delete(1.0, tk.END)

    def run(self):
        """Запускает главный цикл приложения"""
        self.root.mainloop()


if __name__ == '__main__':
    app = ConfigWindow()
    app.run()