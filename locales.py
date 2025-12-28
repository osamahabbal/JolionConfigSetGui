import sys

# Language Configuration: Change to 'ar' for Arabic, 'en' for English
CURRENT_LANG = 'ar'

# Optional: Fix for Arabic text display in Tkinter (Right-to-Left support)
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_SUPPORT = True
except ImportError:
    HAS_ARABIC_SUPPORT = False

TRANSLATIONS = {
    'en': {
        # Titles & Groups
        'window_title': 'JolionConfigSetGui (Enable ADB on HU first! HU & PC must be on same WiFi)',
        'adb_settings_group': 'ADB Connection Settings',
        'config_params_group': 'Configuration Parameters',
        'exec_logs_group': 'Execution Logs',
        'error_title': 'Error',
        'critical_error': 'Critical Error',
        
        # Labels
        'device_ip': 'Device IP:',
        'adb_port': 'ADB Port:',
        'adb_path_info': 'ADB Path:',
        'app_closing': 'The program will close',
        
        # Table Headers
        'col_param': 'Parameter',
        'col_curr_val': 'Current Value',
        'col_new_val': 'New Value',
        'col_bits': 'Bits',

        # Buttons
        'btn_connect_load': 'Connect & Load Config',
        'btn_apply': 'Apply Changes to Device',
        'btn_clear_logs': 'Clear Logs',
        'btn_ok': 'OK',

        # Status & Logs
        'status_ready': 'Ready',
        'status_config_loaded': 'Configuration Loaded',
        'status_connect_error': 'Connection Error',
        'status_configuring': 'Configuring...',
        'status_error': 'Execution Error',
        
        # Messages
        'msg_enter_ip': 'Please enter Device IP',
        'msg_adb_not_found': 'ADB not found at path',
        'msg_exec_cmd': 'Executing',
        'msg_cmd_error': 'Command execution error',
        'msg_adb_root_set': 'ADB root key set',
        'msg_adb_root_fail': 'Failed to set ADB root key',
        'msg_adb_root_success': 'ADB root successful',
        'msg_adb_root_exec_fail': 'Failed to execute adb root',
        'msg_file_downloaded': 'File downloaded',
        'msg_file_dl_fail': 'Failed to download file',
        'msg_file_uploaded': 'File uploaded',
        'msg_file_ul_fail': 'Failed to upload file',
        'msg_rebooting': 'Rebooting device...',
        'msg_reboot_fail': 'Failed to reboot device',
        'msg_connect_fail': 'Failed to connect',
        'msg_connect_success': '✅ Connection established & config downloaded',
        'msg_reading_map': 'Reading property map...',
        'msg_reading_config': 'Reading config...',
        'msg_validating': 'Validating config...',
        'msg_loaded_count': '✅ Loaded {} parameters',
        'msg_load_error': '❌ Config load error',
        'msg_val_out_of_range': '⚠️ Param {}: value {} out of range',
        'msg_val_invalid': '⚠️ Invalid value for param',
        'msg_param_set_error': '❌ Error setting param',
        'msg_setting': 'Setting {} = {}',
        'msg_saving': 'Saving updated config...',
        'msg_update_success': '✅ Config updated successfully',
        'msg_no_changes': '⚠️ Configuration was not changed',
        'msg_process_error': '❌ Processing error',
        'msg_start_seq': '🚀 Starting full sequence...',
        'msg_step_1': '1. Processing configuration...',
        'msg_step_2': '2. Uploading config to device...',
        'msg_step_3': '3. Rebooting device...',
        'msg_applied_reboot': '✅ Settings applied, rebooting...',
        'msg_seq_complete': '🎉 Full sequence completed successfully!',
        'msg_seq_error': '❌ Execution error',
    },
    'ar': {
        # Titles & Groups
        'window_title': 'إعدادات جوليون (فعل ADB في السيارة أولاً! يجب أن تكون السيارة والكمبيوتر على نفس الشبكة)',
        'adb_settings_group': 'إعدادات اتصال ADB',
        'config_params_group': 'متغيرات الإعدادات',
        'exec_logs_group': 'سجلات التنفيذ',
        'error_title': 'خطأ',
        'critical_error': 'خطأ جسيم',
        
        # Labels
        'device_ip': 'عنوان IP للسيارة:',
        'adb_port': 'منفذ ADB:',
        'adb_path_info': 'مسار ADB:',
        'app_closing': 'سيتم إغلاق البرنامج',
        
        # Table Headers
        'col_param': 'المتغير',
        'col_curr_val': 'القيمة الحالية',
        'col_new_val': 'القيمة الجديدة',
        'col_bits': 'البتات',

        # Buttons
        'btn_connect_load': 'اتصال وتحميل الإعدادات',
        'btn_apply': 'تطبيق التغييرات على السيارة',
        'btn_clear_logs': 'مسح السجلات',
        'btn_ok': 'موافق',

        # Status & Logs
        'status_ready': 'جاهز للعمل',
        'status_config_loaded': 'تم تحميل الإعدادات',
        'status_connect_error': 'خطأ في الاتصال',
        'status_configuring': 'جاري الإعداد...',
        'status_error': 'خطأ في التنفيذ',
        
        # Messages
        'msg_enter_ip': 'الرجاء إدخال عنوان IP',
        'msg_adb_not_found': 'لم يتم العثور على ADB في المسار',
        'msg_exec_cmd': 'جاري تنفيذ',
        'msg_cmd_error': 'خطأ في تنفيذ الأمر',
        'msg_adb_root_set': 'تم تعيين مفتاح ADB Root',
        'msg_adb_root_fail': 'فشل تعيين مفتاح ADB Root',
        'msg_adb_root_success': 'نجح ADB Root',
        'msg_adb_root_exec_fail': 'فشل تنفيذ adb root',
        'msg_file_downloaded': 'تم تحميل الملف',
        'msg_file_dl_fail': 'فشل تحميل الملف',
        'msg_file_uploaded': 'تم رفع الملف',
        'msg_file_ul_fail': 'فشل رفع الملف',
        'msg_rebooting': 'جاري إعادة تشغيل الجهاز...',
        'msg_reboot_fail': 'فشل إعادة التشغيل',
        'msg_connect_fail': 'فشل الاتصال',
        'msg_connect_success': '✅ تم الاتصال وتحميل الإعدادات',
        'msg_reading_map': 'قراءة خريطة الخصائص...',
        'msg_reading_config': 'قراءة الإعدادات...',
        'msg_validating': 'التحقق من الإعدادات...',
        'msg_loaded_count': '✅ تم تحميل {} متغير',
        'msg_load_error': '❌ خطأ تحميل الإعدادات',
        'msg_val_out_of_range': '⚠️ المتغير {}: القيمة {} خارج النطاق',
        'msg_val_invalid': '⚠️ قيمة غير صحيحة للمتغير',
        'msg_param_set_error': '❌ خطأ تعيين المتغير',
        'msg_setting': 'تعيين {} = {}',
        'msg_saving': 'حفظ التحديثات...',
        'msg_update_success': '✅ تم تحديث الإعدادات بنجاح',
        'msg_no_changes': '⚠️ لم يتم تغيير أي إعدادات',
        'msg_process_error': '❌ خطأ في المعالجة',
        'msg_start_seq': '🚀 بدء التسلسل الكامل...',
        'msg_step_1': '1. معالجة الإعدادات...',
        'msg_step_2': '2. رفع الإعدادات للجهاز...',
        'msg_step_3': '3. إعادة تشغيل الجهاز...',
        'msg_applied_reboot': '✅ تم التطبيق، جاري إعادة التشغيل...',
        'msg_seq_complete': '🎉 تمت العملية بنجاح!',
        'msg_seq_error': '❌ خطأ في التنفيذ',
    }
}

def tr(key):
    """Returns translated text based on CURRENT_LANG"""
    text = TRANSLATIONS.get(CURRENT_LANG, TRANSLATIONS['en']).get(key, key)
    
    # Fix for Arabic text in Tkinter (Right-to-Left reshaping)
    if CURRENT_LANG == 'ar' and HAS_ARABIC_SUPPORT:
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except:
            return text
    return text