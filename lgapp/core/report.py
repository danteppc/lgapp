"""Database models for LGApp."""
from tortoise import fields, models
from pathlib import Path

from nicegui import ui

from ..util.paths import REPORTS_DIR, ReportFilename

class Report(models.Model):
    """Test report model for tracking pytest execution results.

    Stores metadata about test reports including filenames, status,
    and creation timestamps. The filename field stores only the stem
    (without extension) while file-specific extensions are added in code.
    """

    id = fields.IntField(pk=True)
    filename = fields.CharField(max_length=255, unique=True)  # Report filename stem (no extension)
    test_filename = fields.CharField(
        max_length=255,
        null=True)  # Original uploaded filename
    status = fields.CharField(max_length=32, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

class ReportsService:
    """Service for managing test reports."""

    def __init__(self):
        self.reports_dir = REPORTS_DIR

    async def get_reports(self):
        """Get all reports as a list of dicts, ordered by id descending.
        
        :returns: List of report dictionaries with database fields
        """
        try:
            return await Report.all().order_by('-id').values("id", "filename", "status", "test_filename")
        except Exception as e:
            ui.notify('Failed to load reports', color='negative')
            return []

    async def delete_all_reports(self) -> int:
        """Delete all report files and their database statuses.
        
        :returns: Number of files successfully deleted
        """
        count = 0
        try:
            # Get all HTML files
            files = list(self.reports_dir.glob('*.html')) + \
                list(self.reports_dir.glob('*.xml')) + \
                list(self.reports_dir.glob('*.pdf'))

            # Delete each file
            for file_path in files:
                try:
                    file_path.unlink(missing_ok=True)
                    count += 1
                except Exception:
                    pass

            # Clear all database records
            await Report.all().delete()

            return count
        except Exception as e:
            ui.notify('Failed to delete reports', color='negative')
            return count

    async def create_report(self, filename: str, status: str,
                            test_filename: str | None = None) -> Report | None:
        """Create a new report in the database.

        :param filename: Report filename stem (without extension)
        :param status: Report status ('Passed', 'Not Passed', etc.)
        :param test_filename: Original test filename (optional)
        :returns: Created Report object, or None if creation failed
        """
        try:
            report = await Report.create(
                filename=filename,
                status=status,
                test_filename=test_filename
            )
            return report
        except Exception as e:
            ui.notify('Failed to create report', color='negative')
            return None

    async def get_report_by_id(self, report_id: int) -> Report | None:
        """Get report model by ID.

        :param report_id: Database ID of the report
        :returns: Report model instance or None if not found
        """
        try:
            return await Report.filter(id=report_id).first()
        except Exception as e:
            ui.notify('Failed to retrieve report', color='negative')
            return None

    def get_report_path_by_id(self, report_id: int, filename: str) -> Path:
        """Get report file path by ID.

        :param report_id: Database ID of the report
        :param filename: Report filename
        :returns: Path to the report file
        """
        return self.reports_dir / filename

    async def delete_report_by_id(self, report_id: int) -> bool:
        """Delete a report by ID.

        :param report_id: Database ID of the report to delete
        :returns: True if deletion was successful, False otherwise
        """
        try:
            report = await Report.filter(id=report_id).first()
            if not report:
                return False

            # Delete files (HTML, XML, and PDF)
            pytest_html_file = self.reports_dir / ReportFilename.pytest_html(report.filename)
            junit_html_file = self.reports_dir / ReportFilename.junit_html(report.filename)
            xml_file = (self.reports_dir / report.filename).with_suffix('.xml')
            pytest_pdf_file = self.reports_dir / ReportFilename.pytest_pdf(report.filename)
            junit_pdf_file = self.reports_dir / ReportFilename.junit_pdf(report.filename)

            pytest_html_file.unlink(missing_ok=True)
            junit_html_file.unlink(missing_ok=True)
            xml_file.unlink(missing_ok=True)
            pytest_pdf_file.unlink(missing_ok=True)
            junit_pdf_file.unlink(missing_ok=True)

            # Delete database record
            await report.delete()
            return True
        except Exception as e:
            ui.notify('Failed to delete report', color='negative')
            return False
