# ai_rag_complex_doc
Building rag for a complex document containing text, images and tables

# Project Setup: PDF & OCR Dependencies (Windows)

This project relies on several system-level binaries for processing PDFs, performing OCR (Optical Character Recognition), and identifying file types. Follow these steps to configure your Windows environment.

---

## 📋 Prerequisites

Before installing Python packages, you must set up the following system dependencies.

### 1. Poppler (PDF Processing)
Poppler provides essential tools like `pdftotext` used by many Python libraries to parse PDF content.

1.  **Download:** Visit the [Poppler Windows Releases](https://github.com/oschwartz10612/poppler-windows/releases) and download the latest `Release-xx.x.x-0.zip`.
2.  **Extract:** Unzip the contents to a folder, for example: `C:\poppler`.
3.  **Add to PATH:**
    * Search for **"Edit the system environment variables"** in your Start Menu.
    * Click **Environment Variables**.
    * Under **System Variables**, select **Path** and click **Edit**.
    * Click **New** and paste: `C:\poppler\Library\bin`.
    * Click **OK** on all windows.
4.  **Verify:** Open a new terminal and type:
    ```bash
    pdftotext -v
    ```

---

### 2. Tesseract OCR
Tesseract is the engine required for reading text from images and scanned PDFs.

1.  **Download:** Download the installer (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`) from the [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
2.  **Install:** Follow the installation wizard. Note the installation path (default: `C:\Program Files\Tesseract-OCR`).
3.  **Add to PATH:** * If not added automatically during installation, add `C:\Program Files\Tesseract-OCR` to your **System Path** (following the same steps used for Poppler).
4.  **Verify:** Open a terminal and type:
    ```bash
    tesseract --version
    ```

---

### 3. Libmagic (File Type Identification)
The standard `python-magic` library is designed for Linux. For Windows, you must use the binary-bundled version.

**Do NOT install `python-magic`.** Instead, run:

```bash
pip install python-magic-bin
