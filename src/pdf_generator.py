import os
from fpdf import FPDF
from typing import List
from loguru import logger
from config import CODE_SECTION_MAP, OUTPUT_DIR_PDF, FREE_SANS_REGULAR, FREE_SANS_BOLD, Article


class PDFGenerator:
    """
    Generates a summary PDF from a list of Articles. Groups them by code prefix -> sections.
    """
    def create_summary_pdf(self, articles: List[Article], output_filename="Summary_Report.pdf") -> str:
        """
        Creates a PDF summarizing all articles, grouped by section. Returns path to PDF.
        """
        os.makedirs(OUTPUT_DIR_PDF, exist_ok=True)
        pdf_path = os.path.join(OUTPUT_DIR_PDF, output_filename)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)

        font_family = 'FreeSans'

        # Add custom fonts if desired
        try:
            pdf.add_font('FreeSans', '', FREE_SANS_REGULAR, uni=True)
            pdf.add_font('FreeSans', 'B', FREE_SANS_BOLD, uni=True)
        except Exception:
            logger.warning("Could not add FreeSans fonts; ensure .otf files exist in config path.")
            font_family = 'Helvetica'

        pdf.add_page()

        # Group articles by section
        sections_dict = {}
        for article in articles:
            # Identify prefix
            prefix = ""
            for pfx in CODE_SECTION_MAP.keys():
                if article.code.startswith(pfx):
                    prefix = pfx
                    break

            section_name = CODE_SECTION_MAP.get(prefix, "Other")
            if section_name not in sections_dict:
                sections_dict[section_name] = []
            sections_dict[section_name].append(article)

        # Sort each section by code numerically if needed
        for section_name in sections_dict:
            sections_dict[section_name].sort(key=lambda a: int(''.join(filter(str.isdigit, a.code)) or 0))

        # Render PDF
        for section_name, arts in sections_dict.items():
            pdf.set_font(font_family, 'B', 16)
            pdf.cell(0, 10, section_name, ln=True)

            pdf.set_font(font_family, '', 12)
            for art in arts:

                pdf.set_font(font_family, 'B', 12)
                pdf.cell(0, 10, art.code, ln=True)

                pdf.set_font(font_family, '', 12)
                if art.summary:
                    pdf.multi_cell(0, 10, art.summary)
                else:
                    pdf.multi_cell(0, 10, "No summary available.")

                pdf.ln()

            pdf.ln()

        pdf.output(pdf_path)
        logger.info(f"Summary PDF generated.")
        return pdf_path