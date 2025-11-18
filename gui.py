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
        self.root.title('JolionConfigSetGui')
        self.root.geometry('700x600')

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
        self.connect_button = ttk.Button(adb_group, text='Подключиться к устройству',
                                         command=self.connect_to_device_threaded)
        self.connect_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Группа для чекбоксов
        checkboxes_group = ttk.LabelFrame(main_frame, text="Выберите опции конфигурации", padding="10")
        checkboxes_group.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Чекбоксы
        self.vam_var = tk.BooleanVar()
        self.za4_var = tk.BooleanVar()
        self.mal_var = tk.BooleanVar()

        self.vam_checkbox = ttk.Checkbutton(checkboxes_group, text='VAM(голос)', variable=self.vam_var)
        self.za4_checkbox = ttk.Checkbutton(checkboxes_group, text='ZA4(голос)', variable=self.za4_var)
        self.mal_checkbox = ttk.Checkbutton(checkboxes_group, text='MAL(лобовое дорест)', variable=self.mal_var)

        self.vam_checkbox.grid(row=0, column=0, padx=(0, 20))
        self.za4_checkbox.grid(row=0, column=1, padx=(0, 20))
        self.mal_checkbox.grid(row=0, column=2)

        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.start_button = ttk.Button(buttons_frame, text='Выполнить на устройстве',
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

    def log_message(self, message):
        """Добавляет сообщение в лог с временной меткой"""

        def update_log():
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.log_output.insert(tk.END, formatted_message + '\n')
            self.log_output.see(tk.END)
            self.root.update_idletasks()

        self.root.after(0, update_log)

    def connect_to_device(self):
        """Подключается к Android устройству через ADB"""
        ip = self.ip_input.get().strip()
        port = self.port_input.get().strip()

        if not ip:
            messagebox.showwarning("Ошибка", "Введите IP адрес устройства")
            return

        try:
            self.log_message(f"Подключение к устройству {ip}:{port}...")
            self.adb_client.run_adb_command(['connect', f'{ip}:{port}'])
            self.log_message("✅ Подключение установлено")
            self.status_var.set("Подключено к устройству")
        except Exception as e:
            self.log_message(f"❌ Ошибка подключения: {e}")
            self.status_var.set("Ошибка подключения")

    def connect_to_device_threaded(self):
        """Запускает подключение в отдельном потоке"""
        thread = threading.Thread(target=self.connect_to_device)
        thread.daemon = True
        thread.start()

    def process_configuration(self):
        """Обрабатывает конфигурацию с использованием функций из vce.py"""
        try:
            # Получаем состояние чекбоксов
            vam_checked = self.vam_var.get()
            za4_checked = self.za4_var.get()
            mal_checked = self.mal_var.get()

            # Формируем список свойств для изменения
            props = []

            # Всегда устанавливаем все свойства, в зависимости от состояния чекбоксов
            # MAL: если выбран - 1, если нет - 0
            props.append(f"MAL={'1' if mal_checked else '0'}")

            # VAM: если выбран - 1, если нет - 0
            props.append(f"VAM={1 if vam_checked else 0}")

            # ZA4: если выбран - 3, если нет - 0
            props.append(f"ZA4={3 if za4_checked else 0}")

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
            for prop_str in props:
                property = vce.Property(prop_str)
                name = property.name

                if name == vce.kProjectCodeProperty:
                    self.log_message("Ошибка: Изменение кода проекта не поддерживается")
                    continue

                position = vce.getPositionTable(prop_map).get(name)
                if position is None:
                    self.log_message(f"Ошибка: Свойство '{name}' не найдено в карте")
                    continue

                if len(property.bitstr) > 0:
                    vce.writeBits(data, vce.Position(position), property.bitstr)
                    self.log_message(f"Установка {name} в битовую строку: {property.bitstr}")
                else:
                    vce.writeNumber(data, vce.Position(position), property.number)
                    self.log_message(f"Установка {name} в числовое значение: {property.number}")

                updated = True

            if updated:
                self.log_message("Сохранение обновленной конфигурации...")
                data[-1] = vce.calcCrc8(data[:-1])
                vce.writeConfig(dst_path, data)
                self.log_message("✅ Конфигурация успешно обновлена")

                # Логируем итоговые настройки
                self.log_message("=== ИТОГОВЫЕ НАСТРОЙКИ ===")
                self.log_message(f"MAL: {'ВКЛЮЧЕНО (1)' if mal_checked else 'ВЫКЛЮЧЕНО (0)'}")
                self.log_message(f"VAM: {'ВКЛЮЧЕНО (1)' if vam_checked else 'ВЫКЛЮЧЕНО (0)'}")
                self.log_message(f"ZA4: {'ВКЛЮЧЕНО (3)' if za4_checked else 'ВЫКЛЮЧЕНО (0)'}")

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

            # Шаг 1: Установка ADB root key
            self.log_message("1. Установка ADB root key...")
            if not self.adb_client.set_adb_root_key():
                raise Exception("Не удалось установить ADB root key")

            # Шаг 2: ADB root
            self.log_message("2. Выполнение adb root...")
            if not self.adb_client.adb_root():
                raise Exception("Не удалось выполнить adb root")

            # Шаг 3: Pull конфигурации
            self.log_message("3. Скачивание конфигурации с устройства...")
            if not self.adb_client.pull_config(
                    '/data/vendor/vehicleinfo/VehicleConfig.bin',
                    'VehicleConfig.bin'
            ):
                raise Exception("Не удалось скачать конфигурацию")

            # Шаг 4: Обработка конфигурации
            self.log_message("4. Обработка конфигурации...")
            if not self.process_configuration():
                raise Exception("Не удалось обработать конфигурацию")

            # Шаг 5: Push обновленной конфигурации
            self.log_message("5. Загрузка обновленной конфигурации на устройство...")
            if not self.adb_client.push_config(
                    'NewVehicleConfig.bin',
                    '/data/vendor/vehicleinfo/VehicleConfig.bin'
            ):
                raise Exception("Не удалось загрузить конфигурацию на устройство")

            # Шаг 6: Перезагрузка устройства
            self.log_message("6. Перезагрузка устройства...")
            selected_options = []
            if self.mal_var.get():
                selected_options.append("MAL")
            if self.vam_var.get():
                selected_options.append("VAM")
            if self.za4_var.get():
                selected_options.append("ZA4")

            options_text = ", ".join(selected_options) if selected_options else "все опции отключены"
            self.log_message(f"✅ Настройки применены: {options_text}, перезагрузка...")

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