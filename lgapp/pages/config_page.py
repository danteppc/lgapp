"""Configuration page for editing Labgrid settings."""
from nicegui import ui

from ..view.header import header
from ..util.paths import LABGRID_CONFIG


def read_config() -> str:
    return LABGRID_CONFIG.read_text(encoding='utf-8') if LABGRID_CONFIG.exists() else ''


def render_config_page() -> None:
    """Render the configuration management page."""
    header('/config')
    with ui.column().classes('w-full'):
        with ui.row().classes('items-center'):
            ui.icon('edit_note', color='primary', size='lg')
            ui.label('Edit Labgrid environment').classes('text-lg')
        ui.label(str(LABGRID_CONFIG))

        editor = ui.codemirror(
            value=read_config(),
            language='YAML',
            theme='basicDark'
        ).classes('w-full h-[60vh]')

        def save_cfg():
            """Save configuration to file."""
            try:
                LABGRID_CONFIG.write_text(editor.value or '', encoding='utf-8')
                ui.notify('Configuration saved', color='positive')
            except Exception as e:
                ui.notify(
                    f'Failed to save configuration: {e}', color='negative')

        def refresh_config():
            """Refresh editor with current config content."""
            editor.value = read_config()
            ui.notify('Configuration refreshed', color='info')

        with ui.row():
            ui.button('Refresh', icon='refresh',
                      on_click=refresh_config).props('flat')
            ui.button('Save', icon='save', on_click=save_cfg,
                      color='primary').props('flat')
