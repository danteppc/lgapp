"""Run page for selecting and executing pytest files."""
from pathlib import Path

from nicegui import ui, run, app

from ..view.header import header
from ..core.test_runner import TestRunnerService
from ..core.report import ReportsService
from ..util.local_file_picker import local_file_picker


def render_run_page() -> None:
    """Render the main file selection and test execution page."""
    header('/')

    # Initialize services
    test_runner = TestRunnerService()
    reports_service = ReportsService()

    # Simple state
    selected_file_path: Path | None = None

    async def handle_file_selection():
        """Handle file selection from dialog and automatically run tests."""
        nonlocal selected_file_path

        if not (file := await local_file_picker.py(tests_dir='~/lgtest')):
            ui.notify('No file selected')
            return

        # NATIVE:
        # if not app.native.main_window:
        #     ui.notify('File dialog not available', color='negative')
        #     return
        # if not (file := await app.native.main_window.create_file_dialog(
        #     allow_multiple=False,
        #     file_types=("Python files (*.py)",)
        # )):
        #     ui.notify('No file selected')
        #     return
        print(file)
        path = Path(file[0])
        selected_file_path = path
        ui.notify(f'File "{path.name}" selected successfully',
                  color='positive')

        # Update UI
        file_info.set_text(path.name)

        # Automatically run tests
        await run_tests()

    async def run_tests():
        """Run tests and redirect to reports page."""
        if not selected_file_path:
            return

        # Show spinner during test execution
        spinner_row.set_visibility(True)

        try:
            all_tests_passed, report_name = await run.io_bound(
                test_runner.run_test,
                selected_file_path
            )

            if report_name:
                report = await reports_service.create_report(
                    report_name,
                    'Passed' if all_tests_passed else 'Not Passed',
                    selected_file_path.name
                )
                if report:
                    ui.notify('Test completed successfully!', color='positive')
                    # Redirect to the specific report view
                    ui.navigate.to(f'/view/{report.id}')
                    return

            ui.notify('Test execution failed', color='negative')
        except Exception as e:
            ui.notify(f'Error: {e}', color='negative')
        finally:
            # Hide spinner when done
            spinner_row.set_visibility(False)

    # Main UI - Single step interface
    with ui.column().classes('w-full max-w-5xl mx-auto items-center justify-center gap-4 p-8'):
        # Header section
        with ui.column().classes('items-center text-center gap-2'):
            ui.icon('description', color='primary', size='xl')
            ui.label('Run Labgrid Pytests').classes('text-2xl font-bold')
            ui.label('Start by selecting a pytest file and tests will run automatically').classes(
                'text-lg text-gray-600 mb-4')

        # File selection card
        with ui.card().classes('w-full max-w-md items-center'):
            with ui.column().classes('p-6 gap-4 items-center'):
                ui.label('Select File').classes(
                    'text-lg font-semibold text-center w-full')
                ui.button(
                    'Choose .py file...',
                    icon='upload',
                    on_click=handle_file_selection
                ).classes('w-full')

                ui.separator().classes('w-full')

                ui.label('Selected File:').classes(
                    'font-semibold text-center w-full')
                file_info = ui.label('None selected').classes(
                    'text-gray-600 text-center w-full')

        # Spinner for test execution (hidden by default)
        spinner_row = ui.row().classes('items-center justify-center gap-2 mt-4')
        with spinner_row:
            ui.spinner(size='lg', color='primary')
            ui.label('Running tests, please wait...').classes('text-lg')

        # Hide spinner row initially
        spinner_row.set_visibility(False)
