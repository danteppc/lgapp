"""Path configuration and directory management for LGApp.

This module manages application directories following platform conventions
for user data, configuration, and cache directories. This ensures proper
multi-user support and avoids conflicts when the application is installed
system-wide.
"""
from pathlib import Path
from platformdirs import user_data_dir, user_config_dir, user_cache_dir

# Application name for directory creation
APP_NAME = "lgapp"
APP_AUTHOR = "lgapp"

# User-specific directories following platform conventions
# e.g., ~/.local/share/lgapp on Linux, ~/Library/Application Support/lgapp on macOS
DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))

# e.g., ~/.config/lgapp on Linux, ~/Library/Preferences/lgapp on macOS  
CONFIG_DIR = Path(user_config_dir(APP_NAME, APP_AUTHOR))

# e.g., ~/.cache/lgapp on Linux, ~/Library/Caches/lgapp on macOS
CACHE_DIR = Path(user_cache_dir(APP_NAME, APP_AUTHOR))

# Application-specific subdirectories
REPORTS_DIR = DATA_DIR / 'reports'
UPLOADS_DIR = DATA_DIR / 'uploads'
LOGS_DIR = CACHE_DIR / 'logs'

# Configuration files in user config directory
LABGRID_CONFIG = CONFIG_DIR / 'lgconfig.yaml'

# Database location in user data directory
DATABASE_FILE = REPORTS_DIR / 'reports.sqlite3'
DATABASE_URL = f'sqlite://{DATABASE_FILE}'


def get_labgrid_config_template() -> str:
    """Get the default Labgrid configuration template.
    
    :returns: YAML configuration as string
    """
    return '''targets:
  main:
    resources:
      NetworkService:
        address: 'ADDR_HERE' 
        username: 'root'
      RawSerialPort:
        port: '/dev/ttyS0'
        speed: 115200
    drivers:
      ManualPowerDriver:
        name: "example"
      SSHDriver:
        connection_timeout: 2.0
      SerialDriver:
        timeout: 2.0
      ShellDriver:
        prompt: 'root@[\\w-]+:[^ ]+ '
        login_prompt: ' login: '
        username: 'root'
        password: 'PASS_HERE'
        login_timeout: 2'''


def ensure_dirs_and_files() -> None:
    """Ensure all required directories exist.
    
    This function creates user-specific directories and creates default config file if needed.
    """
    # Create all required user directories
    for directory in [DATA_DIR, CONFIG_DIR, CACHE_DIR, REPORTS_DIR, UPLOADS_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create default labgrid config if it doesn't exist
    if not LABGRID_CONFIG.exists():
        LABGRID_CONFIG.write_text(get_labgrid_config_template(), encoding='utf-8')
        print(f"Created default Labgrid configuration: {LABGRID_CONFIG}")


def get_app_info() -> dict:
    """Get application directory information for debugging.

    :returns: Dictionary containing all configured directory paths
    """
    return {
        'app_name': APP_NAME,
        'data_dir': str(DATA_DIR),
        'config_dir': str(CONFIG_DIR),
        'cache_dir': str(CACHE_DIR),
        'reports_dir': str(REPORTS_DIR),
        'uploads_dir': str(UPLOADS_DIR),
        'logs_dir': str(LOGS_DIR),
        'labgrid_config': str(LABGRID_CONFIG),
        'database_file': str(DATABASE_FILE),
        'database_url': DATABASE_URL,
    }


class ReportFilename:
    """Utility class for generating report filenames with proper extensions.

    Handles the naming convention where database stores only the stem
    and extensions like '_pytest.html' are appended programmatically.
    """
    EXT_HTML = 'html'
    EXT_PDF = 'pdf'
    LIB_PYTEST = 'pytest'
    LIB_JUNIT = 'junit'

    def __init__(self, filename: str, extension: str, lib: str):
        """Initialize ReportFilename.

        :param filename: Base filename stem
        :param extension: File extension (html, pdf)
        :param lib: Library type (pytest, junit)
        """
        self.filename = filename
        self.extension = extension
        self.lib = lib

    def __str__(self) -> str:
        """Generate the full filename with library suffix and extension.

        :returns: Formatted filename like 'stem_pytest.html'
        """
        return f"{self.filename}_{self.lib}.{self.extension}"

    @classmethod
    def pytest_html(cls, filename: str) -> str:
        """Generate pytest HTML filename.

        :param filename: Base filename stem
        :returns: Filename with '_pytest.html' suffix
        """
        return str(cls(filename, cls.EXT_HTML, cls.LIB_PYTEST))

    @classmethod
    def junit_html(cls, filename: str) -> str:
        """Generate JUnit HTML filename.

        :param filename: Base filename stem
        :returns: Filename with '_junit.html' suffix
        """
        return str(cls(filename, cls.EXT_HTML, cls.LIB_JUNIT))

    @classmethod
    def pytest_pdf(cls, filename: str) -> str:
        """Generate pytest PDF filename.

        :param filename: Base filename stem
        :returns: Filename with '_pytest.pdf' suffix
        """
        return str(cls(filename, cls.EXT_PDF, cls.LIB_PYTEST))

    @classmethod
    def junit_pdf(cls, filename: str) -> str:
        """Generate JUnit PDF filename.

        :param filename: Base filename stem
        :returns: Filename with '_junit.pdf' suffix
        """
        return str(cls(filename, cls.EXT_PDF, cls.LIB_JUNIT))
