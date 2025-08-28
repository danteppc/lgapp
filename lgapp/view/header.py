"""Header component for LGApp navigation."""
from nicegui import ui


class Header:
    """Application header with navigation tabs."""

    def __init__(self, active: str = '/'):
        """Initialize header component.
        
        :param active: Currently active path to highlight in navigation
        """
        self.active = active

    def render(self) -> None:
        """Render the header component."""
        ui.colors(primary="#294C4C")

        ui.query('body').style('background-color: #f8f4ed')

        with ui.header():
            labels_paths = [
                ('Run', '/', 'play_arrow'),
                ('Config', '/config', 'settings'),
                ('Reports', '/reports', 'assessment')
            ]
            label_to_path = {label: path for label, path, _ in labels_paths}

            def on_tab_change(e):
                """Handle tab change navigation."""
                target = None
                # e.value can be a label string or a Tab element
                if getattr(e, 'value', None) in label_to_path:
                    target = label_to_path[e.value]
                else:
                    tab_value = getattr(getattr(e, 'value', None), 'value', None)
                    target = next((p for (lbl, p, _) in labels_paths
                                  if lbl == tab_value), None)
                if target:
                    ui.navigate.to(target)

            with ui.row().classes('w-full items-center grid grid-cols-3'):
                # Left: app label with icon
                with ui.row().classes('col-span-1 items-center gap-2'):
                    ui.icon('biotech', color='white', size='lg')
                    ui.label('LGApp').classes('text-lg font-bold')

                # Center: tabs
                with ui.row().classes('col-span-1 justify-center'):
                    with ui.tabs(on_change=on_tab_change) as tabs:
                        tabs_map = {label: ui.tab(label, icon=icon)
                                    for label, _, icon in labels_paths}

                # Right: empty to balance the grid for proper centering
                ui.row().classes('col-span-1')

            # Set initially active tab
            current_label = next((lbl for lbl, path, _ in labels_paths
                                 if path == self.active), 'Run')
            tabs.set_value(tabs_map[current_label])


def header(active: str = '/') -> None:
    """Create application header with navigation tabs.
    
    :param active: Currently active path to highlight in navigation
    """
    header_component = Header(active)
    header_component.render()
