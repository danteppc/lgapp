"""Test execution service."""
import datetime as dt
import sys
from pathlib import Path

import pytest
from nicegui import ui

from ..util.paths import REPORTS_DIR, LABGRID_CONFIG, ReportFilename
from junit2htmlreport import runner
import xml.etree.ElementTree as ET

# TODO: notify per test, thread-safe
# class MyPlugin:
#     @pytest.hookimpl(hookwrapper=True)
#     def pytest_runtest_logreport(self, report):
#         outcome = yield
#         if getattr(report, "when", "") == "call" and report.passed:
#             pass


class TestRunnerService:
    """Service for executing pytest tests."""

    def __init__(self):
        self.reports_dir = REPORTS_DIR
        self.labgrid_config = LABGRID_CONFIG

    def run_test(self, selected_file_path: Path) -> tuple[bool, str | None]:
        """Execute a test file and return exit code and report path.

        :param selected_file_path: Path to the test file to execute
        :returns: Tuple of (exit_code, report_name_stem or None if failed)
        """
        try:
            timestamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            base_name = selected_file_path.stem
            report_name = f'report-{timestamp[:15]}'

            report_path_pytest_html = self.reports_dir / \
                ReportFilename.pytest_html(report_name)
            report_path_junit_html = self.reports_dir / \
                ReportFilename.junit_html(report_name)
            report_path_xml = self.reports_dir / f"{report_name}.xml"

            # Clear module cache
            self._clear_module_cache(base_name)

            args = [
                '--lg-env', str(self.labgrid_config),
                str(selected_file_path),
                f'--html={report_path_pytest_html}',
                '--self-contained-html',
                '--verbose',
                '--cache-clear',
                '-o', 'log_cli_level=INFO',
                '--disable-warnings',
                f'--junit-xml={report_path_xml}'
            ]

            try:
                code = pytest.main(args)
            except Exception as e:
                ui.notify(f'Test execution failed: {e}', color='negative')
                return False, None

            all_tests_passed = code == 0
            try:
                runner.run([str(report_path_xml), str(report_path_junit_html)])
                root = ET.parse(report_path_xml).getroot()
                passed = 0
                for testcase in root.findall('.//testcase'):
                    if None is testcase.find('failure') is testcase.find('error') is testcase.find('skipped'):
                        passed += 1
                all_tests_passed &= passed > 0
            except Exception as e:
                ui.notify(
                    f'Warning: JUnit report conversion failed: {e}', color='warning')
                # Continue anyway as we have the main report

            return all_tests_passed, report_name

        except Exception as e:
            ui.notify(f'Test execution failed: {e}', color='negative')
            return False, None

    def _clear_module_cache(self, base_name: str) -> None:
        """Clear Python module cache for test isolation.

        :param base_name: Base name of the module to clear from cache
        """
        try:
            if base_name in sys.modules:
                del sys.modules[base_name]

            modules_to_remove = [mod for mod in sys.modules.keys()
                                 if mod.startswith(f'{base_name}_')]
            for mod in modules_to_remove:
                del sys.modules[mod]
        except Exception as e:
            # Don't notify user as this is not critical
            pass
