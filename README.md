# 📘 PDF Heading & Title Extractor – Adobe Hackathon 2025 Challenge 1A

This Python-based tool processes PDF files to extract their **document title** and **structured heading outline (H1, H2, H3)**. Built for Adobe Hackathon 2025 – Challenge 1A, it leverages font size, layout features, and rule-based logic for accurate text classification.

---

## 🧠 Features

* ✅ **Extracts title** from the first page using font size, position, and character heuristics
* ✅ **Identifies valid headings** while ignoring noise like page numbers, dates, and bullets
* ✅ **Classifies heading levels** (H1, H2, H3) based on position and structure
* ✅ **Cleans text** using Unicode normalization and regex patterns
* ✅ **Outputs structured JSON** for each PDF with title and heading tree

---

## 📂 Folder Structure

```
./
 | ├──/app/ 
 | ├── input/        # Place your input PDFs here  
 | ├── output/       # JSON results will be saved here  
 └─── App_1A.py       # Core script  
```

---

## 🚀 How to Run

1. Place all your `.pdf` files into the `/app/input/` folder.
2. Run the script using Python:

   ```
   python App_1A.py
   ```
3. The output will be saved as `.json` files in `/app/output/`.

---

## 📦 Dependencies

* `PyMuPDF` (fitz)
* `pathlib`
* `json`, `re`, `unicodedata`

Install required library:

```
pip install pymupdf
```

---

## 📄 Sample Output (JSON)

```json
{
  "title": "Sample PDF Document",
  "outline": [
    {"level": "H1", "text": "Introduction", "page": 1},
    {"level": "H2", "text": "Background", "page": 2},
    {"level": "H3", "text": "History of the Topic", "page": 2}
  ]
}
```

---

## 🎯 Use Case

Perfect for:

* Automatic document summarization
* Accessibility tools
* Building search indexes
* Pre-processing before NLP tasks

---

## 🛠️ Notes

* Title is extracted based on largest font sizes on the first page.
* Headings are validated using regex filters and word heuristics.
* Level assignment is position-aware and context-sensitive.

---

## 👨‍💼 Author

Developed by [Sai Mohith Gopisetty](https://github.com/saimohith-27)
As part of **Adobe Hackathon 2025** – Round 2 Challenge
