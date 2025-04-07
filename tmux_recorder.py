from datetime import datetime
import atexit
from typing import Optional

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

    def run(self) -> None:
        """
        @brief Main method to execute the recording process.
        
        Creates the tmux session, starts asciinema recording,
        and waits for the session to complete.
        """
        # Visual session start informations
        print("=" * 60) 
        print(f"Recording session for project: {self.project_name}")
        print(f"Date: {self.paths.date_str}, Time: {self.paths.time_str}")
        print("=" * 60)

        # Create the tmux session with logging enabled
        print(f"[+] Creating tmux session '{self.tmux_session}'...")
        self.create_tmux_session()

        # Start recording with asciinema
        print(f"[+] Starting asciinema recording: {self.paths.asciinema_file}")
        self.start_recording()

        # Wait for the session to complete
        print("[+] Recording session complete.")
        self.wait_for_tmux_exit()

        # Display output locations for user reference
        print("\nRecording outputs:")
        print(f"- Asciinema recording: {self.paths.asciinema_file}")
        print(f"- Zsh history: {self.paths.zsh_history_file}")
        print(f"- Tmux logs: {self.paths.tmux_log_dir}/*.log")

        print("\nSession completed. Resources will be cleaned up on exit.")
        print("=" * 60)
