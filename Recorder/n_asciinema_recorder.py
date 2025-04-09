import atexit
from typing import Optional, Dict, Any
from pathlib import Path

from settingcode.app_config import AppConfig
from settingcode.session_paths import SessionPaths, generate_session_paths
from misc.config_generator import ConfigGenerator
from tmux.tmux_session import TmuxSessionManager
from Recorder.AsciinemaManager import AsciinemaManager
from Recorder.Recorder import AbstractRecorder


class TmuxAsciinemaRecorder(AbstractRecorder):
    """
    @brief Main class for recording tmux sessions with asciinema.

    Coordinates the components for tmux session management,
    configuration generation, and recording.
    """
    def __init__(self, project_name: str, tmux_session_name: Optional[str] = None, config: Optional[AppConfig] = None) -> None:
        """
        @brief Initialize a new recorder instance.
        
        @param project_name Name of the project being recorded.
        @param tmux_session Optional custom tmux session name. If None, auto-generated.
        @param config Optional AppConfig instance. If None, defaults are used.
        """
        super().__init__(project_name)
        
        # Config
        self.config: AppConfig = config or AppConfig.from_defaults()

        # Generate a unique session name to avoid conflicts with existing sessions if not provided
        self.tmux_session_name: str = tmux_session_name or f"{project_name}_{self.date_str}_{self.time_str}"

        # Initialize path structure for organized log storage
        self.paths: SessionPaths = generate_session_paths(
            project_name=self.project_name,
            date_str=self.date_str,
            time_str=self.time_str
        )

        # Initialize components
        self.config_generator = ConfigGenerator(self.config, self.paths)
        self.tmux_manager = TmuxSessionManager(self.tmux_session_name)
        self.asciinema_recorder = AsciinemaManager(self.paths.asciinema_file)
        
        # Assign output file from paths
        self._output_file = self.paths.asciinema_file


    def get_output_path(self) -> Path:
        """
        @brief Get the path where the recording will be saved.
        
        @return Path to the output file.
        """
        return self.paths.asciinema_file
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        @brief Get informations on Current Recording Session
        
        @return Dictionary containing session details.
        """
        return {
            "project_name": self.project_name,
            "date": self.paths.date_str,
            "time": self.paths.time_str,
            "tmux_session": self.tmux_session_name,
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
        self.setup()
        self.start_recording()
        self._wait_for_tmux_exit()
        self.stop_recording()

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

    def stop_recording(self) -> Optional[Path]:
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
                "asciinema": self.paths.asciinema_file,
                "zsh_history": self.paths.zsh_history_file,
                "tmux_logs": self.paths.tmux_log_dir
            },
            "metadata": {
                "project_name": self.project_name,
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