"""Report viewer component."""
from nicegui import ui
from ..util.pdf_service import PDFService
from ..util.paths import ReportFilename
from ..core.report import Report


class ReportViewer:
    """Component for viewing individual reports."""

    def render(self, report: Report | None):
        """Render the report viewer using report ID.
        
        :param report: Report model instance or None if not found
        """
        with ui.column().classes('w-full'):
            if not report:
                self._render_not_found()
            else:
                html_file_name = ReportFilename.pytest_html(report.filename)
                self._render_header(report)
                self._render_iframe(html_file_name)

    def _render_not_found(self):
        """Render not found message."""
        with ui.row().classes('items-center gap-2'):
            ui.icon('error', color='negative')
            ui.label('Report not found')

    def _render_header(self, report: Report):
        """Render header with report ID and filename.
        
        :param report: Report model instance to display
        """
        with ui.row().classes('items-center'):
            ui.icon('description', color='primary', size='lg')
            ui.label(f'Report #{report.id}').classes('text-lg font-bold')
            ui.link('Show All Reports', '/reports')
            ui.space()
            DownloadButton('HTML', on_click=lambda: self._download_html(report.filename))
            DownloadButton('PDF', on_click=lambda: self._download_pdf(report.filename))

    def _render_iframe(self, filename: str):
        """Render iframe with report content.
        
        :param filename: HTML report filename to display in iframe
        """
        ui.element('iframe').props(
            f'src=/reports/{filename}'
        ).classes('w-full h-[80vh]')

    def _download_html(self, filename: str):
        """Download report as HTML.
        
        :param filename: Report filename stem for HTML download
        """
        ui.download(f'/reports/{ReportFilename.pytest_html(filename)}')

    def _download_pdf(self, filename: str):
        """Download report as PDF.
        
        :param filename: Report filename stem for PDF conversion and download
        """
        PDFService.convert_from_html_file(ReportFilename.junit_html(filename))


class DownloadButton(ui.button):
    """Custom download button for report files."""

    def __init__(self,
                 label: str,
                 on_click,
                 color: str = 'green',
                 icon: str = 'download'):
        """Initialize download button.

        :param label: Button text
        :param on_click: Click handler function
        :param color: Button color theme
        :param icon: Button icon
        """
        super().__init__(
            text=label,
            icon=icon,
            on_click=on_click,
            color=color
        )
        # self.props('flat')
