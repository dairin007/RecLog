from typing import Optional, Dict, Any
from pathlib import Path

from settingcode.app_static_config import AppStaticSettings
from settingcode.app_session_config import AppSessionConfig
from misc.config_generator import ConfigGenerator
from tool_manager.tmux_manager import TmuxSessionManager
from tool_manager.asciinema_manager import AsciinemaManager
from Recorder.ab_recorder import AbstractRecorder


class TmuxAsciinemaRecorder(AbstractRecorder):
    """
    @brief Main class for recording tmux sessions with asciinema.

    Coordinates the components for tmux session management,
    configuration generation, and recording.
    """
    def __init__(self, static_config: AppStaticSettings, session_config: AppSessionConfig, tmux_session_name: Optional[str] = None ) -> None:
        """
        @brief Initialize a new recorder instance.

        @param project_name Name of the project being recorded.
        @param tmux_session Optional custom tmux session name. If None, auto-generated.
        @param config Optional AppConfig instance. If None, defaults are used.
        """
        # Config
        self.static_config: AppStaticSettings = static_config
        self.session_config: AppSessionConfig = session_config

        # Generate a unique session name to avoid conflicts with existing sessions if not provided
        self.tmux_session_name: str = tmux_session_name or f"{session_config.project_name}_{session_config.date_str}_{session_config.time_str}"

        # Initialize components
        self.config_generator = ConfigGenerator(self.static_config, self.session_config)
        self.tmux_manager = TmuxSessionManager(self.tmux_session_name)
        self.asciinema_recorder = AsciinemaManager(self.session_config.asciinema_file)

        # Assign output file from paths
        self._output_file = self.session_config.asciinema_file

        self._is_recording=False


    def get_output_path(self) -> Path:
        """
        @brief Get the path where the recording will be saved.

        @return Path to the output file.
        """
        return self.session_config.asciinema_file

    def get_session_info(self) -> Dict[str, Any]:
        """
        @brief Get informations on Current Recording Session

        @return Dictionary containing session details.
        """
        return {
            "project_name": self.session_config.project_name,
            "date": self.session_config.date_str,
            "time": self.session_config.time_str,
            "tmux_session": self.tmux_session_name,
            "asciinema_file": self.session_config.asciinema_file,
            "zsh_history_file": self.session_config.zsh_history_file,
            "tmux_log_dir": self.session_config.tmux_log_dir
        }

    def setup(self) -> None:
        """
        @brief Setup Tmux Session for recording

        Generates necessary configuration and creates the tmux session.
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
        if self._is_recording:
            print("Recording is already in progress")
            return

        self._is_recording = True
        self.asciinema_recorder.start_recording(self.tmux_session_name)

    def stop_recording(self):
        """
        @brief Stop the ongoing recording

        For tmux asciinema recording, this method doesn't need to do much as
        the recording ends when the tmux session ends, but it's included for
        interface consistency.

        @return Path to the recorded asciinema file.
        """
        if not self._is_recording:
            return {}

        self._is_recording = False
        self._cleanup_tmux()

        return {
            "outputs": {
                "asciinema": self.session_config.asciinema_file,
                "zsh_history": self.session_config.zsh_history_file,
                "tmux_logs": self.session_config.tmux_log_dir
            },
            "metadata": {
                "project_name": self.session_config.project_name,
            }
        }

    def wait_for_completion(self) -> None:
        """
        @brief Wait for the tmux session to complete.

        For tmux sessions, completion means the tmux session has terminated.
        This is a blocking call.
        """
        if self._is_recording:
            self.tmux_manager.wait_for_exit()

    def _cleanup_tmux(self) -> None:
        """
        @brief Stop all processes and clean up resources.

        This method is called via atexit to ensure resources
        are released even if the program exits unexpectedly.
        """
        try:
            if self.tmux_manager.session_exists():
                self.tmux_manager.terminate_session()
        except Exception as e:
            print(f"Warning: Could not terminate tmux session: {e}")
