"""Delete confirmation dialog component."""
import asyncio
from typing import Callable
from nicegui import ui


class DeleteConfirmationDialog:
    """Reusable delete confirmation dialog."""

    def __init__(self, on_confirm: Callable):
        """Initialize delete confirmation dialog.
        
        :param on_confirm: Callback function to execute when deletion is confirmed
        """
        self.on_confirm = on_confirm

    def show(self, item_identifier: str | int, item_type: str = "item",
             display_name: str | None = None):
        """Show confirmation dialog for deleting an item.
        
        :param item_identifier: Unique identifier for the item to delete
        :param item_type: Type description for the item (e.g., 'report', 'file')
        :param display_name: Optional display name for the item, defaults to identifier
        """
        # Use display_name if provided, otherwise use the identifier
        display_text = display_name or str(item_identifier)
        with ui.dialog() as dialog, ui.card():
            ui.label(f'Are you sure you want to delete {item_type} '
                     f'"{display_text}"?')
            with ui.row():
                ui.button('Cancel', on_click=dialog.close).props('flat')

                async def do_delete():
                    dialog.close()
                    try:
                        result = self.on_confirm(item_identifier)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        ui.notify(f'Error during deletion: {str(e)}',
                                  color='negative')

                ui.button('Delete', color='negative', on_click=do_delete)

        dialog.open()
