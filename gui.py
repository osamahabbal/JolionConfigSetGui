import sys
import time
import os
import hashlib
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# Import functions from vce.py
import vce

# Import Translation Logic
from locales import tr, CURRENT_LANG

class AndroidADBClient:
    """Client for working with Android device via ADB"""

    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.adb_path = self.get_adb_path()

    def get_adb_path(self):
        """Returns absolute path to adb.exe"""
        if getattr(sys, 'frozen', False):
            # If compiled to exe (PyInstaller)
            base_path = os.path.dirname(sys.executable)
        else:
            # If running as Python script
            base_path = os.path.dirname(os.path.abspath(__file__))

        adb_path = os.path.join(base_path, 'adb', 'adb.exe')

        if not os.path.exists(adb_path):
            raise FileNotFoundError(f"{tr('msg_adb_not_found')}: {adb_path}")

        return adb_path

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def decode_output(self, byte_string):
        """Decodes ADB output with correct encoding"""
        encodings = ['cp866', 'utf-8', 'windows-1251', 'iso-8859-1']

        for encoding in encodings:
            try:
                return byte_string.decode(encoding)
            except UnicodeDecodeError:
                continue

        return byte_string.decode('utf-8', errors='replace')

    def run_adb_command(self, command, check_returncode=True):
        """Executes ADB command"""
        full_command = [self.adb_path] + command
        self.log(f"{tr('msg_exec_cmd')}: {' '.join(full_command)}")

        try:
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=False,
                check=check_returncode
            )

            if result.stdout:
                stdout_text = self.decode_output(result.stdout).strip()
                if stdout_text:
                    self.log(stdout_text)

            return result

        except subprocess.CalledProcessError as e:
            error_msg = tr('msg_cmd_error')

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
            self.log(f"{tr('msg_cmd_error')}: {str(e)}")
            raise

    def set_adb_root_key(self):
        """Sets ADB root key similar to bat-script"""
        try:
            result = self.run_adb_command(['shell', 'getprop', 'ro.serialno'])
            serialno = self.decode_output(result.stdout).strip()

            input_string = f"{serialno}Harman@SH--"
            md5_hash = hashlib.md5(input_string.encode()).hexdigest()

            self.run_adb_command(['shell', f'setprop service.adb.root.hkey {md5_hash}'])
            self.log(f"{tr('msg_adb_root_set')}: {md5_hash}")
            return True

        except Exception as e:
            self.log(f"{tr('msg_adb_root_fail')}: {e}")
            return False

    def adb_root(self):
        """Executes adb root"""
        try:
            self.run_adb_command(['root'])
            self.log(tr('msg_adb_root_success'))
            return True
        except Exception as e:
            self.log(f"{tr('msg_adb_root_exec_fail')}: {e}")
            return False

    def pull_config(self, remote_path, local_path):
        """Downloads config file from device"""
        try:
            self.run_adb_command(['pull', remote_path, local_path])
            self.log(f"{tr('msg_file_downloaded')} {remote_path} -> {local_path}")
            return True
        except Exception as e:
            self.log(f"{tr('msg_file_dl_fail')}: {e}")
            return False

    def push_config(self, local_path, remote_path):
        """Uploads config file to device"""
        try:
            self.run_adb_command(['push', local_path, remote_path])
            self.log(f"{tr('msg_file_uploaded')} {local_path} -> {remote_path}")
            return True
        except Exception as e:
            self.log(f"{tr('msg_file_ul_fail')}: {e}")
            return False

    def reboot_device(self):
        """Reboots the device"""
        try:
            self.run_adb_command(['shell', 'reboot'])
            self.log(tr('msg_rebooting'))
            return True
        except Exception as e:
            self.log(f"{tr('msg_reboot_fail')}: {e}")
            return False


class ConfigWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.property_vars = {} 
        try:
            self.adb_client = AndroidADBClient(log_callback=self.log_message)
            self.init_ui()
        except FileNotFoundError as e:
            self.show_error_and_exit(str(e))
        except Exception as e:
            self.show_error_and_exit(f"Init Error: {str(e)}")

    def show_error_and_exit(self, message):
        """Shows error and exits"""
        error_window = tk.Tk()
        error_window.title(tr('error_title'))
        error_window.geometry("400x200")

        ttk.Label(error_window, text=tr('critical_error'), font=('Arial', 12, 'bold')).pack(pady=10)
        ttk.Label(error_window, text=message, wraplength=380).pack(pady=10, padx=10)
        ttk.Label(error_window, text=tr('app_closing'), font=('Arial', 10)).pack(pady=10)

        ttk.Button(error_window, text=tr('btn_ok'),
                   command=lambda: [error_window.destroy(), self.root.destroy(), sys.exit(1)]).pack(pady=10)

        error_window.mainloop()

    def init_ui(self):
        self.root.title(tr('window_title'))
        self.root.geometry('800x700')

        # Check alignment for Arabic
        header_anchor = tk.E if CURRENT_LANG == 'ar' else tk.W

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # ADB Settings Group
        adb_group = ttk.LabelFrame(main_frame, text=tr('adb_settings_group'), padding="10")
        adb_group.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        adb_group.columnconfigure(1, weight=1)

        # IP Input
        ttk.Label(adb_group, text=tr('device_ip')).grid(row=0, column=0, sticky=header_anchor, padx=(0, 5))
        self.ip_input = ttk.Entry(adb_group)
        self.ip_input.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.ip_input.insert(0, '')

        # Port Input
        ttk.Label(adb_group, text=tr('adb_port')).grid(row=1, column=0, sticky=header_anchor, padx=(0, 5), pady=(10, 0))
        self.port_input = ttk.Entry(adb_group)
        self.port_input.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        self.port_input.insert(0, '5555')

        # Connect Button
        self.connect_button = ttk.Button(adb_group, text=tr('btn_connect_load'),
                                         command=self.connect_and_load_config_threaded)
        self.connect_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Configuration Parameters Group
        self.config_group = ttk.LabelFrame(main_frame, text=tr('config_params_group'), padding="10")
        self.config_group.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        self.config_group.columnconfigure(0, weight=1)
        self.config_group.rowconfigure(0, weight=1)

        self.create_scrollable_config_area()

        # Action Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.start_button = ttk.Button(buttons_frame, text=tr('btn_apply'),
                                       command=self.on_start_threaded)
        self.clear_button = ttk.Button(buttons_frame, text=tr('btn_clear_logs'),
                                       command=self.on_clear_logs)

        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        self.clear_button.pack(side=tk.LEFT)

        # Info Frame
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(info_frame, text=f"{tr('adb_path_info')} {self.adb_client.adb_path}",
                  font=('Courier New', 8), foreground='gray').pack(side=tk.LEFT)

        # Logs Group
        log_group = ttk.LabelFrame(main_frame, text=tr('exec_logs_group'), padding="10")
        log_group.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(5, weight=1)
        log_group.columnconfigure(0, weight=1)
        log_group.rowconfigure(0, weight=1)

        self.log_output = scrolledtext.ScrolledText(log_group, height=15,
                                                    font=('Courier New', 9),
                                                    background='#f5f5f5')
        self.log_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status Bar
        self.status_var = tk.StringVar(value=tr('status_ready'))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

    def create_scrollable_config_area(self):
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

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Headers
        ttk.Label(self.scrollable_frame, text=tr('col_param'), font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.scrollable_frame, text=tr('col_curr_val'), font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.scrollable_frame, text=tr('col_new_val'), font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.scrollable_frame, text=tr('col_bits'), font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)

    def log_message(self, message):
        def update_log():
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.log_output.insert(tk.END, formatted_message + '\n')
            self.log_output.see(tk.END)
            self.root.update_idletasks()

        self.root.after(0, update_log)

    def connect_and_load_config(self):
        ip = self.ip_input.get().strip()
        port = self.port_input.get().strip()

        if not ip:
            messagebox.showwarning(tr('error_title'), tr('msg_enter_ip'))
            return

        try:
            self.log_message(f"Connecting to {ip}:{port}...")
            self.adb_client.run_adb_command(['connect', f'{ip}:{port}'])

            self.log_message("Setting ADB root key...")
            if not self.adb_client.set_adb_root_key():
                raise Exception(tr('msg_adb_root_fail'))

            self.log_message("Executing adb root...")
            if not self.adb_client.adb_root():
                raise Exception(tr('msg_adb_root_exec_fail'))

            self.log_message("Downloading config...")
            if not self.adb_client.pull_config(
                    '/data/vendor/vehicleinfo/VehicleConfig.bin',
                    'VehicleConfig.bin'
            ):
                raise Exception(tr('msg_file_dl_fail'))

            self.log_message(tr('msg_connect_success'))
            self.status_var.set(tr('status_config_loaded'))

            self.load_and_display_config()

        except Exception as e:
            self.log_message(f"❌ {tr('status_connect_error')}: {e}")
            self.status_var.set(tr('status_connect_error'))

    def connect_and_load_config_threaded(self):
        thread = threading.Thread(target=self.connect_and_load_config)
        thread.daemon = True
        thread.start()

    def load_and_display_config(self):
        try:
            map_path = 'haval_jolion.json'
            src_path = 'VehicleConfig.bin'

            self.log_message(tr('msg_reading_map'))
            prop_map = vce.readMap(map_path)

            self.log_message(tr('msg_reading_config'))
            data = vce.readConfig(src_path)

            self.log_message(tr('msg_validating'))
            vce.validateConfig(data, prop_map)

            for widget in self.scrollable_frame.winfo_children():
                if hasattr(widget, 'grid_info') and widget.grid_info()['row'] > 0:
                    widget.destroy()

            self.property_vars = {}
            position_table = vce.getPositionTable(prop_map)

            row = 1
            for property_name, position_str in position_table.items():
                if property_name == vce.kProjectCodeProperty:
                    continue

                position = vce.Position(position_str)
                bit_length = position.high_bit - position.low_bit + 1

                current_bitstr = vce.readBits(data, position)
                current_value = int(current_bitstr, 2)

                ttk.Label(self.scrollable_frame, text=property_name).grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
                ttk.Label(self.scrollable_frame, text=str(current_value)).grid(row=row, column=1, padx=5, pady=2, sticky=tk.W)

                var = tk.StringVar(value=str(current_value))
                entry = ttk.Entry(self.scrollable_frame, textvariable=var, width=10)
                entry.grid(row=row, column=2, padx=5, pady=2, sticky=tk.W)

                bits_label = f"[{position.byte_idx}][{position.high_bit}:{position.low_bit}]"
                ttk.Label(self.scrollable_frame, text=bits_label).grid(row=row, column=3, padx=5, pady=2, sticky=tk.W)

                self.property_vars[property_name] = (var, position, bit_length)
                row += 1

            self.log_message(tr('msg_loaded_count').format(len(self.property_vars)))

        except Exception as e:
            self.log_message(f"{tr('msg_load_error')}: {str(e)}")

    def process_configuration(self):
        try:
            map_path = 'haval_jolion.json'
            src_path = 'VehicleConfig.bin'
            dst_path = 'NewVehicleConfig.bin'

            self.log_message(tr('msg_reading_map'))
            prop_map = vce.readMap(map_path)

            self.log_message(tr('msg_reading_config'))
            data = vce.readConfig(src_path)

            self.log_message(tr('msg_validating'))
            vce.validateConfig(data, prop_map)

            updated = False

            for property_name, (var, position, bit_length) in self.property_vars.items():
                try:
                    new_value_str = var.get().strip()
                    if not new_value_str:
                        continue

                    new_value = int(new_value_str)

                    max_value = (1 << bit_length) - 1
                    if new_value < 0 or new_value > max_value:
                        self.log_message(tr('msg_val_out_of_range').format(property_name, max_value))
                        continue

                    vce.writeNumber(data, position, new_value)
                    self.log_message(tr('msg_setting').format(property_name, new_value))
                    updated = True

                except ValueError:
                    self.log_message(f"{tr('msg_val_invalid')} {property_name}: '{var.get()}'")
                except Exception as e:
                    self.log_message(f"{tr('msg_param_set_error')} {property_name}: {str(e)}")

            if updated:
                self.log_message(tr('msg_saving'))
                data[-1] = vce.calcCrc8(data[:-1])
                vce.writeConfig(dst_path, data)
                self.log_message(tr('msg_update_success'))
                return True
            else:
                self.log_message(tr('msg_no_changes'))
                return False

        except Exception as e:
            self.log_message(f"{tr('msg_process_error')}: {str(e)}")
            return False

    def on_start(self):
        try:
            self.status_var.set(tr('status_configuring'))
            self.log_message(tr('msg_start_seq'))

            self.log_message(tr('msg_step_1'))
            if not self.process_configuration():
                raise Exception("Failed to process config")

            self.log_message(tr('msg_step_2'))
            if not self.adb_client.push_config(
                    'NewVehicleConfig.bin',
                    '/data/vendor/vehicleinfo/VehicleConfig.bin'
            ):
                raise Exception("Failed to upload config")

            self.log_message(tr('msg_step_3'))
            self.log_message(tr('msg_applied_reboot'))

            if not self.adb_client.reboot_device():
                raise Exception("Failed to reboot")

            self.log_message(tr('msg_seq_complete'))
            self.status_var.set(tr('status_ready'))

        except Exception as e:
            self.log_message(f"{tr('msg_seq_error')}: {str(e)}")
            self.status_var.set(tr('status_error'))

    def on_start_threaded(self):
        thread = threading.Thread(target=self.on_start)
        thread.daemon = True
        thread.start()

    def on_clear_logs(self):
        self.log_output.delete(1.0, tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = ConfigWindow()
    app.run()