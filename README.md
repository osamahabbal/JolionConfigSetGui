# 🚗 Jolion Config Tool (Global Edition)

**Advanced Configuration Tool for Haval Jolion Head Units (HUT)**
*Configure your vehicle parameters safely via ADB.*

[🇺🇸 English](#english) | [🇸🇦 العربية](#arabic)

---

<a name="english"></a>
## 🇺🇸 English Documentation

### 📖 Overview
This project provides a Graphical User Interface (GUI) to modify the system configuration (`VehicleConfig.bin`) of the Haval Jolion multimedia unit. It allows you to enable hidden features (like Voice Assistant "VAM" or Voice Assistant Language "ZA4") and customize other vehicle parameters.

### ⭐ Credits & Acknowledgements
This tool is a GUI wrapper built upon the powerful core logic developed by **DymOK93**.
* **Core Logic (VCE):** [GWM-Harman-VCE by DymOK93](https://github.com/DymOK93/GWM-Harman-VCE)
* **Original GUI Concept:** JolionMagic

### 🚀 Features
* **Bilingual Support:** Fully translated into **English** and **Arabic**.
* **Safety First:** Automatically verifies values and calculates Checksum (CRC) to prevent errors.
* **Two Modes:** Includes a **Full Editor** for experts and a **One-Click Patcher** for quick fixes.
* **Wireless:** Works over Wi-Fi (ADB).

### 📥 Included Tools
When you download the release, you will find two executable files. Choose the one that fits your needs:

#### 1. `JolionConfigTool_Global.exe` (Recommended)
**The Full Manual Editor.**
* View and edit **all** available parameters.
* Backup and restore configurations.
* Supports language switching (English/Arabic).

#### 2. `ConfigToolVoice.exe` (Quick Fix)
**The One-Click Patcher.**
* Automatically finds **Voice Assistant (VAM)** and **Language (ZA4)**.
* Sets them to `4` (Enabled) and reboots the car immediately.
* No manual searching required.

### ⚙️ Installation & Usage

#### Prerequisites
1.  **Laptop/PC** with Windows.
2.  **Wi-Fi Connection:** Your Laptop and Car must be connected to the **same Wi-Fi network**.
3.  **ADB Connection:** Ensure you have ADB access to your Head Unit.

#### How to Run
1.  Download the latest ZIP file from the [Releases Page](../../releases).
2.  **Extract the ZIP file** to a folder on your Desktop.
    * *Note: Do not run the exe directly from inside the ZIP.*
3.  Run `JolionConfigTool_Global.exe`.
4.  Enter your car's **IP Address** and click **Connect**.

### 🌐 How to Change Language
The tool supports **English** and **Arabic**. To switch languages:

1.  Open the file named `locales.py` using **Notepad**.
2.  Find the line: `CURRENT_LANG = 'en'`
3.  Change it to your preferred language:
    * For **English**: `CURRENT_LANG = 'en'`
    * For **Arabic**: `CURRENT_LANG = 'ar'`
4.  Save the file and restart the program.

### ⚠️ Disclaimer
**Use this tool at your own risk.** Modifying system files (`VehicleConfig.bin`) can affect your vehicle's functionality. Always ensure you have a backup of your original configuration before making changes.

---

<a name="arabic"></a>
## 🇸🇦 العربية: دليل الاستخدام

### 📖 نبذة عن الأداة
تتيح لك هذه الأداة تعديل إعدادات النظام لشاشة هافال جوليون (Haval Jolion) بسهولة عبر الكمبيوتر. توفر واجهة رسومية آمنة لتفعيل الميزات المخفية (مثل الأوامر الصوتية ولغة المساعد الصوتي "حتى الآن لم اجد كونفق اللغة العربية") وتعديل ملف `VehicleConfig.bin`.

### ⭐ شكر وتقدير
هذه الأداة عبارة عن واجهة رسومية تعتمد على البرمجيات الأساسية التي طورها **DymOK93**.
* **المصدر الأساسي (VCE):** [GWM-Harman-VCE by DymOK93](https://github.com/DymOK93/GWM-Harman-VCE)
* **فكرة الواجهة الأصلية:** JolionMagic

### 🚀 المميزات
* **دعم كامل للغة العربية:** واجهة وقوائم معربة بالكامل.
* **نظام حماية:** التحقق من صحة القيم وحساب Checksum تلقائياً لمنع الأخطاء.
* **أداتين في واحد:** محرر شامل للمحترفين، وأداة سريعة للتفعيل التلقائي.
* **لا سلكي:** تعمل عبر شبكة الواي فاي (ADB).

### 📥 الأدوات المرفقة
عند تحميل الملف المضغوط، ستجد أداتين، اختر ما يناسبك:

#### 1. `JolionConfigTool_Global.exe` (الخيار الموصى به)
**المحرر اليدوي الشامل.**
* يتيح لك رؤية وتعديل **جميع** خصائص السيارة.
* عمل نسخ احتياطية واستعادتها.
* يدعم تغيير اللغة بين العربية والإنجليزية.

#### 2. `ConfigToolVoice.exe` (الإصلاح السريع)
**أداة التفعيل بضغطة زر.**
* تقوم تلقائياً بالبحث عن **المساعد الصوتي (VAM)** و **اللغة (ZA4)**.
* تقوم بتغيير قيمتها إلى `4` (تفعيل) وإعادة تشغيل الشاشة فوراً.
* لا تحتاج للبحث اليدوي.

### ⚙️ التثبيت وطريقة الاستخدام

#### المتطلبات
1.  **كمبيوتر محمول (لابتوب)** بنظام ويندوز.
2.  **اتصال Wi-Fi:** يجب أن تكون السيارة واللابتوب متصلين **بنفس شبكة الواي فاي**.
3.  **اتصال ADB:** تأكد من توفر صلاحية الاتصال عبر ADB في الشاشة.

#### خطوات التشغيل
1.  حمل آخر إصدار من صفحة [Releases](../../releases).
2.  **فك الضغط** عن الملف بالكامل في مجلد على سطح المكتب.
    * *ملاحظة: لا تشغل البرنامج من داخل ملف الـ ZIP مباشرة.*
3.  شغل ملف `JolionConfigTool_Global.exe`.
4.  أدخل **عنوان IP** الخاص بالشاشة واضغط **اتصال**.

### 🌐 طريقة تغيير اللغة
البرنامج يدعم اللغتين العربية والإنجليزية. للتحويل بينهما:

1.  افتح الملف المسمى `locales.py` باستخدام **المفكرة (Notepad)**.
2.  ابحث عن السطر: `CURRENT_LANG = 'en'`
3.  غير القيمة حسب رغبتك:
    * للغة **الإنجليزية**: `CURRENT_LANG = 'en'`
    * للغة **العربية**: `CURRENT_LANG = 'ar'`
4.  احفظ الملف وأعد تشغيل البرنامج.

### ⚠️ إخلاء مسؤولية
**استخدام هذه الأداة على مسؤوليتك الخاصة.** تعديل ملفات النظام قد يؤثر على وظائف السيارة. تأكد دائماً من وجود نسخة احتياطية لإعداداتك الأصلية قبل إجراء أي تغييرات.
