import json
import re
import fitz
from pathlib import Path
import unicodedata

class PDFOutlineExtractor:
    def __init__(self):
        self.title_max_candidates = 3
        self.title_max_words = 12 
        self.min_heading_length = 3
        self.max_heading_length = 50
        self.useless_starts = {
            "and", "or", "for", "to", "from", "of", "but", "the",
            "with", "in", "on", "at", "by", "as", "if", "is", "are"
        }
        
        # Patterns to exclude
        self.page_pattern = re.compile(r'^(page|pg|p\.?)\s*\d+$', re.IGNORECASE)
        self.date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4})\b')
        self.number_pattern = re.compile(r'^\d+$')
        self.bullet_pattern = re.compile(r'^[•▪♦▶➢✓✔⦿]')
        self.single_char_pattern = re.compile(r'^\W?[a-zA-Z]\W?$')
        self.special_char_start = re.compile(r'^[^a-zA-Z0-9"\']')

    def clean_text(self, text):
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s\-.,:;()]', '', text)
        return text

    def extract_title(self, first_page_spans):

        title_candidates = set()
        
        for span in sorted(first_page_spans, key=lambda s: s['size'], reverse=True):
            text = self.clean_text(span['text'])
            bbox = span['bbox']

            if not text or len(text.split()) > self.title_max_words:
                continue

            if bbox[1] > 0.5:  # Relaxed vertical position
                continue

            if self.page_pattern.match(text) or self.number_pattern.match(text):
                continue

            # Character ratio check (Copilot suggestion)
            char_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
            if char_ratio < 0.5:
                continue

            title_candidates.add((span['size'], text.title()))

        # Remove duplicates while preserving order
        seen = set()
        final_titles = []
        for _, title in sorted(title_candidates, reverse=True):
            if title not in seen:
                seen.add(title)
                final_titles.append(title)
            if len(final_titles) >= self.title_max_candidates:
                break

        return " - ".join(final_titles) if final_titles else "Untitled Document"

    def is_valid_heading(self, text, page, span_bbox):
        text = self.clean_text(text)
        
        if self.single_char_pattern.match(text):
            return False
        if self.special_char_start.match(text) and not text.startswith(('"', "'", '(')):
            return False
            
        if (len(text) < self.min_heading_length or
            len(text) > self.max_heading_length or
            not any(c.isalpha() for c in text)):
            return False
            
        if (self.page_pattern.match(text) or
            self.date_pattern.search(text) or
            self.number_pattern.match(text) or
            self.bullet_pattern.search(text) or
            text.lower() in {'continued', 'footer', 'header'}):
            return False
            
        first_word = text.split()[0].lower() if text.split() else ""
        if first_word in self.useless_starts:
            return False
        if len(re.findall(r'\d', text)) > 4:
            return False
            
        return True

    def determine_heading_level(self, text, page_num, outline):
        if not outline:
            return "H1"
            
        last_heading = outline[-1]
        if last_heading["level"] == "H1":
            return "H2"
        elif last_heading["level"] == "H2":
            return "H3"
            
        return "H1" if page_num == 0 else "H2"

    def process_pdf(self, pdf_path):
        """Main processing function"""
        doc = fitz.open(pdf_path)
        outline = []
        first_page_spans = []
        
        # First page processing for title
        if len(doc) > 0:
            first_page = doc.load_page(0)
            blocks = first_page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        first_page_spans.append({
                            'text': span["text"],
                            'bbox': span["bbox"],
                            'size': span["size"]
                        })
        
        title = self.extract_title(first_page_spans)
        
        # Process all pages for headings
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        if self.is_valid_heading(span["text"], page, span["bbox"]):
                            level = self.determine_heading_level(
                                span["text"],
                                page_num,
                                outline
                            )
                            outline.append({
                                "level": level,
                                "text": self.clean_text(span["text"]),
                                "page": page_num + 1
                            })
        
        doc.close()
        return {
            "title": title,
            "outline": outline
        }

def main():
    input_dir = Path("./app/input/")
    output_dir = Path("./app/output/")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Processing {pdf_file.name}...")
        try:
            result = extractor.process_pdf(pdf_file)
            
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Saved results to {output_file}")
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")

if __name__ == "__main__":
    main()