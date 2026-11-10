import os
import hashlib
import re
from typing import Dict, Any, Tuple
import fitz  # PyMuPDF
import docx

class DocumentParserService:
    @staticmethod
    def compute_sha256(content: bytes) -> str:
        """Compute SHA-256 checksum for deduplication and content addressing."""
        hasher = hashlib.sha256()
        hasher.update(content)
        return hasher.hexdigest()

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extract clean text from PDF using PyMuPDF (fitz)."""
        doc = fitz.open(file_path)
        text_parts = []
        for page in doc:
            text = page.get_text("text")
            if text:
                text_parts.append(text)
        doc.close()
        return "\n".join(text_parts).strip()

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Extract clean text from Word DOCX document."""
        doc = docx.Document(file_path)
        text_parts = []
        for p in doc.paragraphs:
            if p.text:
                text_parts.append(p.text)
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                if row_text:
                    text_parts.append(row_text)
        return "\n".join(text_parts).strip()

    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Extract text from plain text file."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

    def parse_document(self, file_path: str, filename: str) -> Tuple[str, str]:
        """
        Parses document according to extension.
        Returns: (raw_text, file_hash)
        """
        ext = os.path.splitext(filename)[1].lower()
        with open(file_path, "rb") as f:
            content = f.read()
        file_hash = self.compute_sha256(content)

        if ext == ".pdf":
            raw_text = self.parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            raw_text = self.parse_docx(file_path)
        elif ext in [".txt", ".md"]:
            raw_text = self.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Permitted formats: .pdf, .docx, .txt")

        return raw_text, file_hash

    @staticmethod
    def segment_resume_sections(text: str) -> Dict[str, str]:
        """
        Segments a resume into functional blocks: Experience, Education, Skills, Projects.
        """
        sections = {
            "summary": "",
            "skills": "",
            "experience": "",
            "education": "",
            "projects": ""
        }

        # Common headers
        headers_pattern = re.compile(
            r'^(summary|profile|about|technical\s+skills|skills|work\s+experience|professional\s+experience|experience|employment\s+history|education|academic\s+background|projects|personal\s+projects)\b',
            re.IGNORECASE | re.MULTILINE
        )

        lines = text.split("\n")
        current_section = "summary"
        current_buffer = []

        for line in lines:
            line_stripped = line.strip()
            match = headers_pattern.match(line_stripped)
            if match and len(line_stripped) < 40:
                header = match.group(1).lower()
                # Flush previous buffer
                if current_buffer:
                    sections[current_section] = sections.get(current_section, "") + "\n" + "\n".join(current_buffer)
                    current_buffer = []

                if "skill" in header:
                    current_section = "skills"
                elif "experience" in header or "employment" in header:
                    current_section = "experience"
                elif "education" in header or "academic" in header:
                    current_section = "education"
                elif "project" in header:
                    current_section = "projects"
                else:
                    current_section = "summary"
            else:
                if line_stripped:
                    current_buffer.append(line_stripped)

        if current_buffer:
            sections[current_section] = sections.get(current_section, "") + "\n" + "\n".join(current_buffer)

        return {k: v.strip() for k, v in sections.items()}

document_parser = DocumentParserService()
