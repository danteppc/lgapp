"""Reports table component."""
from typing import Callable, List, Dict
from nicegui import ui


class ReportsTable:
    """Reusable reports table component."""

    def __init__(self, on_delete: Callable, on_download_pdf: Callable, on_view_report: Callable):
        """Initialize reports table component.

        :param on_delete: Callback function for delete actions
        :param on_download_pdf: Callback function for PDF download actions
        :param on_view_report: Callback function for viewing report (navigation)
        """
        self.on_delete = on_delete
        self.on_download_pdf = on_download_pdf
        self.on_view_report = on_view_report

    def _row(self, name: str, label: str, sortable: bool = True) -> Dict:
        """Transform a report item for the table row.

        :param name: Column name/field identifier
        :param label: Display label for the column
        :param sortable: Whether the column should be sortable
        :returns: Dictionary defining table column configuration
        """
        return {
            'name': name,
            'label': label,
            'field': name,
            'align': 'left',
            'sortable': sortable
        }

    def render(self, data: List[Dict]) -> ui.table:
        """Render the reports table.

        :param data: List of report dictionaries to display
        :returns: Configured NiceGUI table with custom slots and events
        """
        columns = [
            self._row('id', 'ID'),
            self._row('filename', 'Report Name'),
            self._row('test_filename', 'Test Filename'),
            self._row('status', 'Result'),
            self._row('actions', 'Actions', False),
        ]

        table = ui.table(
            columns=columns,
            rows=data,
            row_key='id',
            pagination=10
        ).classes('w-full')

        self._add_table_slots(table)
        self._setup_events(table)

        return table

    def _add_table_slots(self, table: ui.table):
        """Add custom slots for table columns.

        :param table: NiceGUI table component to add slots to
        """
        # ID column with numbered index
        table.add_slot('body-cell-id', r'''
            <q-td key="id" :props="props">
                    <span class="font-mono text-sm text-gray-600">
                        {{ props.value }}
                    </span>
            </q-td>
        ''')

        # Report name column with clickable navigation
        table.add_slot('body-cell-filename', r'''
            <q-td key="filename" :props="props">
                <div class="flex items-center gap-2">
                    <q-icon name="description" size="sm" color="primary" />
                    <q-btn flat dense no-caps color="primary" 
                           class="text-left p-0 underline"
                           :label="props.row.filename"
                           @click="() => $parent.$emit('view-report', props.row.id)" />
                </div>
            </q-td>
        ''')

        # Test filename column with icon
        table.add_slot('body-cell-test_filename', r'''
            <q-td key="test_filename" :props="props">
                <div class="flex items-center gap-2">
                    <q-icon name="code" size="sm" color="grey" />
                    <span class="font-mono text-sm">{{ props.value }}</span>
                </div>
            </q-td>
        ''')

        # Result column with colored badge
        table.add_slot('body-cell-status', r'''
            <q-td key="status" :props="props">
                <q-badge :color="props.value === 'Passed' ? 'green' :
                                (props.value === 'Not Passed' ? 'deep-orange' : 'grey')">
                    {{ props.value }}
                </q-badge>
            </q-td>
        ''')

        # Actions column with download and delete buttons
        table.add_slot('body-cell-actions', r'''
            <q-td key="actions" :props="props">
                <div class="flex gap-2">
                    <q-btn flat dense color="primary" size="sm" icon="download"
                           label="PDF"
                           @click="() => $parent.$emit('download-pdf',
                                     props.row.id)" />
                    <q-btn flat dense color="negative" size="sm" icon="delete"
                           label="Delete"
                           @click="() => $parent.$emit('delete-single',
                                     props.row.id)" />
                </div>
            </q-td>
        ''')

    def _setup_events(self, table: ui.table):
        """Setup table event handlers.

        :param table: NiceGUI table component to setup events for
        :returns: Configured table with event handlers
        """
        # Handle delete events
        async def handle_delete(e) -> None:
            try:
                report_id = e.args if e.args else None
                if report_id:
                    import asyncio
                    result = self.on_delete(report_id)
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as ex:
                ui.notify(f'Delete operation failed: {ex}', color='negative')

        table.on('delete-single', handle_delete)

        # Handle PDF download events
        async def handle_download_pdf(e) -> None:
            try:
                report_id = e.args if e.args else None
                if report_id:
                    import asyncio
                    result = self.on_download_pdf(report_id)
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as ex:
                ui.notify(f'PDF download failed: {ex}', color='negative')

        table.on('download-pdf', handle_download_pdf)

        # Handle view report events (navigation)
        async def handle_view_report(e) -> None:
            try:
                report_id = e.args if e.args else None
                if report_id and self.on_view_report:
                    import asyncio
                    result = self.on_view_report(report_id)
                    if asyncio.iscoroutine(result):
                        await result
            except Exception as ex:
                ui.notify(f'Navigation failed: {ex}', color='negative')

        table.on('view-report', handle_view_report)

        return table
