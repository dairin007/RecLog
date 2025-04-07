from datetime import datetime
import atexit
from typing import Optional, Dict, Any

from app_config import AppConfig
from session_paths import SessionPaths, generate_session_paths
from config_generator import ConfigGenerator
from tmux_session import TmuxSessionManager
from recorder import AsciinemaRecorder
from resource_cleaner import ResourceCleaner


class TmuxAsciinemaRecorder:
    """
    @brief Main class for recording tmux sessions with asciinema.

    Coordinates the components for tmux session management,
    configuration generation, and recording.
    """
    def __init__(self, project_name: str, tmux_session: Optional[str] = None, config: Optional[AppConfig] = None) -> None:
        """
        @brief Initialize a new recorder instance.
        
        @param project_name Name of the project being recorded.
        @param tmux_session Optional custom tmux session name. If None, auto-generated.
        @param config Optional AppConfig instance. If None, defaults are used.
        """
        self.project_name: str = project_name
        self.config: AppConfig = config or AppConfig.from_defaults()

        # Generate timestamps for organized file storage and unique session names
        now: datetime = datetime.now()
        self.date_str: str = now.strftime("%Y%m%d")
        self.time_str: str = now.strftime("%H%M%S")

        # Generate a unique session name to avoid conflicts with existing sessions if not provided
        self.tmux_session: str = tmux_session or f"{project_name}_{self.date_str}_{self.time_str}"

        # Initialize path structure for organized log storage
        self.paths: SessionPaths = generate_session_paths(
            project_name=self.project_name,
            date_str=self.date_str,
            time_str=self.time_str
        )

        # Initialize components
        self.config_generator = ConfigGenerator(self.config, self.paths)
        self.tmux_manager = TmuxSessionManager(self.tmux_session)
        self.recorder = AsciinemaRecorder(self.paths.asciinema_file)
        self.cleaner = ResourceCleaner(self.tmux_manager, self.config.tmp_dir)

        # Register cleanup to ensure tmux sessions and tmp settings don't remain after program exit
        atexit.register(self.cleanup_resources)

    def create_tmux_session(self) -> None:
        """
        @brief Create a new tmux session with the configured settings.
        
        Generates configuration files and starts a detached tmux session.
        """
        # Generate configs
        tmux_conf_path = self.config_generator.generate_tmux_conf()
        self.config_generator.generate_zdotdir()
        
        # Create tmux session
        self.tmux_manager.create_session(tmux_conf_path)

    def start_recording(self) -> None:
        """
        @brief Start asciinema recording of the tmux session.
        """
        self.recorder.start_recording(self.tmux_session)

    def wait_for_tmux_exit(self) -> None:
        """
        @brief Wait for the tmux session to terminate.
        """
        self.tmux_manager.wait_for_exit()

    def cleanup_resources(self) -> None:
        """
        @brief Clean up resources created during recording.
        """
        self.cleaner.cleanup()

    def get_session_info(self) -> Dict[str, Any]:
        """
        @brief Get informations on Current Recording Session
        
        @return Dictionary containing session details.
        """
        return {
            "project_name": self.project_name,
            "date": self.paths.date_str,
            "time": self.paths.time_str,
            "tmux_session": self.tmux_session,
            "asciinema_file": self.paths.asciinema_file,
            "zsh_history_file": self.paths.zsh_history_file,
            "tmux_log_dir": self.paths.tmux_log_dir
        }

    def run(self) -> None:
        """
        @brief Main method to execute the recording process.
        
        Creates the tmux session, starts asciinema recording,
        and waits for the session to complete.
        """
        # Core recording workflow
        self._setup_recording()
        self._perform_recording()
        self._finalize_recording()

    def _setup_recording(self) -> None:
        """
        @brief Setup Tmux Session
        """
        # Create the tmux session with logging enabled
        self.create_tmux_session()
        
    def _perform_recording(self) -> None:
        """
        @brief Recording start by asciinema
        """
        # Start recording with asciinema
        self.start_recording()
        
        # Wait for the session to complete
        self.wait_for_tmux_exit()
        
    def _finalize_recording(self) -> None:
        """
        @brief Finalize the recording process.
        """
        # Nothing special needed here as cleanup is handled by atexit
        pass