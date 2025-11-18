chcp 1251
adb.exe devices
echo В списке выше должно быть одно устройство (для включения adb нужно в сервисном меню авто несколько раз вкл и выключить ADB, пункт enable ADB/disable ADB)
pause
adb.exe push %~dp0/apk/BackButton.apk /mnt/sdcard/Download/BackButton.apk
adb.exe push %~dp0/apk/FileManager.apk /mnt/sdcard/Download/FileManager.apk
adb.exe push %~dp0/apk/activitylauncher.apk /mnt/sdcard/Download/activitylauncher.apk
adb.exe push %~dp0/apk/JolionWatchKillerStub.apk /mnt/sdcard/Download/JolionWatchKillerStub.apk
adb.exe push %~dp0/apk/MacroDroid.apk /mnt/sdcard/Download/MacroDroid.apk
adb.exe push %~dp0/apk/telegram.apk /mnt/sdcard/Download/telegram.apk
adb.exe shell "cd /mnt/sdcard/Download;pm install BackButton.apk;pm install FileManager.apk;pm install activitylauncher.apk;pm install JolionWatchKillerStub.apk;pm install MacroDroid.apk;pm install telegram.apk;am start -a android.settings.WIRELESS_SETTINGS"
cmd

echo Настройте подключение к wi fi с телефона, в стандартные настройки можно попасть через activity launcher или BackButton, файлы можно скидывать через телеграм
pause