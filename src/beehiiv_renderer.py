import os
import re
import pyperclip
from fpdf import FPDF
from typing import List
from loguru import logger
from config import Article, OUTPUT_DIR_PDF, CODE_SECTION_MAP


class BeehiivRenderer:
    def generate_javascript_code(self, articles: List[Article]):
        """
        Creates placeholders like Title_IN1, Text_IN1 from each Article's code + summary.
        Then generates JS that:
          1) Replaces those placeholders with actual text if found.
          2) Removes any leftover placeholders altogether for any code prefixes from CODE_SECTION_MAP.
        Copies to clipboard and saves as PDF.
        """
        placeholder_content = {}

        # 1) Gather placeholders from summaries
        for art in articles:
            code = art.code
            link = art.link
            lines = art.summary.split("\n")
            headline = ""
            summary = ""
            for ln in lines:
                if "**Headline**:" in ln:
                    headline = ln.split("**Headline**: ")[-1].strip()
                elif "**Summary**:" in ln:
                    summary = ln.split("**Summary**: ")[-1].strip()

            if not headline:
                logger.error(f"No Headline found in summary for code: {code}")
            if not summary:
                logger.error(f"No Summary found in summary for code: {code}")

            # Append a hyperlink that points to art.link
            summary += f"{link}"

            placeholder_content[f"Title_{code}"] = headline
            placeholder_content[f"Text_{code}"] = summary

        # 2) The main insertion script for placeholders that DO have text
        script_template = r"""
        var elems = document.querySelectorAll('[contenteditable="true"] *');
        for (var i = 0; i < elems.length; i++) {{
            if (elems[i].textContent.trim() === '{placeholder}') {{
                elems[i].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                elems[i].focus();

                if (`{new_text}`.trim() === "") {{
                    elems[i].textContent = "";
                    const selection = window.getSelection();
                    const range = document.createRange();
                    range.setStart(elems[i], 0);
                    range.setEnd(elems[i], 0);
                    selection.removeAllRanges();
                    selection.addRange(range);
                    document.execCommand('delete');
                    console.log(`Deleted empty placeholder '{placeholder}' and removed whitespace.`);
                    continue;
                }}

                elems[i].textContent = `{new_text}`.trim();
                console.log(`Inserted text for placeholder '{placeholder}'.`);
                break;
            }}
        }}
        """

        combined_script = "// JavaScript Code for Beehiiv Editor\n"

        # 2a) Build per-placeholder insertion code
        for placeholder, new_text in placeholder_content.items():
            safe_text = new_text.replace("`", "\\`") if new_text else ""
            combined_script += script_template.format(
                placeholder=placeholder,
                new_text=safe_text
            ) + "\n"

        # 3) Build a final pass to remove leftover placeholders
        section_prefixes = []
        for prefix in CODE_SECTION_MAP.keys():
            section_prefixes.append(f"Title_{prefix}")
            section_prefixes.append(f"Text_{prefix}")

        # Turn that list into a JS array (e.g. ["Title_IN","Text_IN","Title_EM","Text_EM",...])
        leftover_prefixes_js = ", ".join(f'"{p}"' for p in section_prefixes)

        removal_script = f"""
    (function() {{
        var leftoverPrefixes = [{leftover_prefixes_js}];
        var elems = document.querySelectorAll('[contenteditable="true"] *');
        for (var i = 0; i < elems.length; i++) {{
            var text = elems[i].textContent.trim();
            for (var p = 0; p < leftoverPrefixes.length; p++) {{
                var prefix = leftoverPrefixes[p];
                // If the line starts with prefix (like "Title_IN" or "Text_IN")
                if (text.startsWith(prefix)) {{
                    elems[i].remove();
                    console.log("Removed leftover placeholder: " + text);
                    break; // Move on to next element
                }}
            }}
        }}
    }})();
    """

        combined_script += removal_script

        # 4) Copy script to clipboard and save to PDF
        pyperclip.copy(combined_script)
        self.save_js_script_to_pdf(combined_script)

    def save_js_script_to_pdf(self, script):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 10, script)

        filename = "javascript_code.pdf"
        pdf_path = os.path.join(OUTPUT_DIR_PDF, filename)
        pdf.output(pdf_path)
