"""PDF generation service using weasyprint."""
from weasyprint import HTML, CSS
from nicegui import ui
from .paths import REPORTS_DIR


class PDFService:
    """Service for converting HTML reports to PDF."""

    @staticmethod
    def convert_from_html_file(filename: str):
        """Convert HTML file to PDF bytes.

        :param filename: Name of the HTML file to convert
        :returns: None (triggers file download via NiceGUI)
        """
        file_path = REPORTS_DIR / filename

        try:
            html = HTML(filename=file_path)
            css = CSS(string='@page { size: A4 } body { font-size: 55%}')
            pdf_file = file_path.with_suffix('.pdf')
            print(pdf_file)
            html.write_pdf(pdf_file, stylesheets=[css])
            ui.download.file(pdf_file)
        except Exception as e:
            ui.notify(f'Error generating PDF for {file_path.name}: {e}', color='negative')
            return None
