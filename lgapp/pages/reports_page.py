"""Reports page for viewing and managing test reports."""
from nicegui import ui

from ..view.header import header
from ..view.reports_table import ReportsTable
from ..view.dialogs import DeleteConfirmationDialog
from ..view.report_viewer import ReportViewer
from ..core.report import ReportsService
from ..util.pdf_service import PDFService
from ..util.paths import ReportFilename

# Global service instances
reports_service = ReportsService()


@ui.refreshable
async def reports_table() -> None:
    """Create refreshable reports table with status and actions."""

    # Event handlers
    async def handle_delete_confirmed_wrapper(report_id):
        """Handle confirmed delete operation."""
        try:
            success = await reports_service.delete_report_by_id(report_id)
            if success:
                ui.notify(f'Deleted report ID {report_id}', color='positive')
            else:
                ui.notify(f'Failed to delete report ID {report_id}', color='negative')
        except Exception as e:
            ui.notify(f'Error deleting report: {e}', color='negative')
        
        reports_table.refresh()
        action_buttons.refresh()

    def handle_delete_request(report_id):
        """Handle delete request - show confirmation dialog."""
        delete_dialog.show(report_id, "report", f"#{report_id}")

    async def handle_download_pdf(report_id):
        """Handle PDF download request."""
        if report := await reports_service.get_report_by_id(report_id):
            PDFService.convert_from_html_file(ReportFilename.junit_html(report.filename))
        else:
            ui.notify(f'Report ID {report_id} not found', color='negative') 
                                    

    def handle_view_report(report_id):
        """Handle view report navigation."""
        ui.navigate.to(f'/view/{report_id}')

    # Create components
    delete_dialog = DeleteConfirmationDialog(on_confirm=handle_delete_confirmed_wrapper)
    table_component = ReportsTable(
        on_delete=handle_delete_request,
        on_download_pdf=handle_download_pdf,
        on_view_report=handle_view_report
    )

    # Get data and render table
    data = await reports_service.get_reports()
    table_component.render(data)


@ui.refreshable
async def action_buttons() -> None:
    """Create refreshable action buttons row."""
    data = await reports_service.get_reports()
    has_reports = len(data) > 0

    with ui.row().classes('gap-2'):
        ui.button(
            'Refresh',
            icon='refresh',
            on_click=lambda: [reports_table.refresh(), action_buttons.refresh()]
        ).props('flat')

        if has_reports and delete_all_dialog:
            ui.button(
                'Delete All',
                icon='delete_sweep',
                color='negative',
                on_click=delete_all_dialog.open
            ).props('flat')


# Global delete all dialog and handler
delete_all_dialog = None


async def handle_delete_all_confirmed():
    """Handle confirmed delete all operation."""
    try:
        count = await reports_service.delete_all_reports()
        if count > 0:
            ui.notify('Deleted all reports', color='positive')
        else:
            ui.notify('No reports to delete', color='warning')
    except Exception as e:
        ui.notify(f'Error deleting reports: {e}', color='negative')
    
    reports_table.refresh()
    action_buttons.refresh()
    if delete_all_dialog:
        delete_all_dialog.close()


async def render_reports_page() -> None:
    """Render the reports listing and management page."""
    global delete_all_dialog

    header('/reports')

    # Create delete all confirmation dialog
    with ui.dialog() as delete_all_dialog, ui.card():
        ui.label('Delete all reports?')
        ui.label('This action cannot be undone.').classes('text-sm text-gray-600')
        with ui.row():
            ui.button('Cancel', on_click=delete_all_dialog.close)
            ui.button(
                'Delete All',
                color='negative',
                on_click=handle_delete_all_confirmed
            )

    with ui.column().classes('w-full'):
        await reports_table()
        await action_buttons()


async def render_view_page(report_id: str) -> None:
    """Render individual report view page by ID."""
    header('/reports')

    viewer = ReportViewer()

    try:
        # Convert report_id to int and get report from database
        report_id_int = int(report_id)
        report = await reports_service.get_report_by_id(report_id_int)
        with ui.card().classes('w-full'):
            viewer.render(report)

    except ValueError:
        # Invalid report ID (not a number)
        ui.notify('Invalid report ID', color='negative')
        with ui.card().classes('w-full'):
            viewer.render(None)
