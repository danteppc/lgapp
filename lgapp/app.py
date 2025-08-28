import argparse

from nicegui import ui, app
from tortoise import Tortoise

from .util.paths import REPORTS_DIR, DATABASE_URL, ensure_dirs_and_files


@ui.page('/')
def main_page() -> None:
    """Main page route handler."""
    from .pages.run_page import render_run_page
    render_run_page()


@ui.page('/reports')
async def reports_page() -> None:
    """Reports page route handler."""
    from .pages.reports_page import render_reports_page
    await render_reports_page()


@ui.page('/config')
def config_page() -> None:
    """Configuration page route handler."""
    from .pages.config_page import render_config_page
    render_config_page()


@ui.page('/view/{report_id}')
async def view_page(report_id: str) -> None:
    """View report page route handler."""
    from .pages.reports_page import render_view_page
    await render_view_page(report_id)


async def init_orm() -> None:
    """Initialize Tortoise ORM with SQLite database."""
    try:
        await Tortoise.init(
            db_url=DATABASE_URL,
            modules={"models": ["lgapp.core.report"]},
        )
        await Tortoise.generate_schemas()
    except Exception as e:
        ui.notify(f'Database initialization failed: {e}', color='negative')
        raise


def main(reload: bool = True) -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        'LGApp', description='NiceGUI web interface for pytest with Labgrid')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()

    # Setup application (directories, static files, database)
    try:
        ensure_dirs_and_files()
        app.add_static_files('/reports', str(REPORTS_DIR))
        app.on_startup(init_orm)
        app.on_shutdown(Tortoise.close_connections)
        app.native.settings['ALLOW_DOWNLOADS'] = True
    except Exception as e:
        print(f'Failed to setup application: {e}')
        raise

    app.on_startup(lambda: print(f'LGApp started on port {args.port}!'))

    ui.run(title='LGApp', favicon='🔬', port=args.port, reload=reload,
           native=False, show_welcome_message=False)


def main_without_reload() -> None:
    """Main entry point for production without reload."""
    main(reload=False)
