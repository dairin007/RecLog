import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import time
from typing import Optional
import shutil
import atexit
import argparse


@dataclass
class AppConfig:
    """
    @brief Configuration class for the application.
    
    Holds paths to various directories and files used by the application.
    """
    base_dir: Path
    settings_dir: Path
    tmp_dir: Path
    tmux_dynamic_conf: Path
    default_zshrc: Path
    default_tmux_conf: Path
    
    @classmethod
    def from_defaults(cls, base_dir: Optional[Path] = None) -> 'AppConfig':
        """
        @brief Create an AppConfig instance with default values.
        
        @param base_dir Optional base directory path. If None, uses the parent directory of the current file.
        @return AppConfig instance initialized with default paths.
        """
        if base_dir is None:
            base_dir = Path(__file__).parent
            
        settings_dir: Path = base_dir / "settings"
        tmp_dir: Path = base_dir / "tmp"
        
        # Ensure temporary directory exists
        tmp_dir.mkdir(parents=True, exist_ok=True)
        
        return cls(
            base_dir=base_dir,
            settings_dir=settings_dir,
            tmp_dir=tmp_dir,
            tmux_dynamic_conf=tmp_dir / "generated_tmux.conf",
            default_zshrc=Path.home() / ".zshrc",
            default_tmux_conf=Path.home() / ".tmux.conf"
        )


@dataclass
class SessionPaths:
    """
    @brief Class for organizing session-related file paths.
    
    Stores paths to various files and directories used during a recording session.
    """
    project_name: str
    date_str: str
    time_str: str
    base_dir: Path
    asciinema_file: Path
    zsh_history_file: Path
    tmux_log_dir: Path


class TmuxAsciinemaRecorder:
    """
    @brief Main class for recording tmux sessions with asciinema.

    Handles the creation of tmux sessions, configuration of logging,
    and recording of terminal sessions using asciinema.
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
        self.paths: SessionPaths = self._generate_paths()

        # Register cleanup to ensure tmux sessions and tmp settings don't remain after program exit
        atexit.register(self.cleanup_resources)


    def _generate_paths(self) -> SessionPaths:
        """
        @brief Generate all required paths for the recording session.
        
        Creates directories for asciinema recordings, zsh history, and tmux logs.
        
        @return SessionPaths object containing all generated paths.
        """
        # Organize logs by project and date for better discoverability
        base_dir: Path = Path.home() / "project" / self.project_name / "Log" / self.date_str
        asciinema_dir: Path = base_dir / "asciinema"
        zsh_dir: Path = base_dir / "zsh"
        tmux_dir: Path = base_dir / "tmux"

        # Create all required directories to avoid runtime errors
        asciinema_dir.mkdir(parents=True, exist_ok=True)
        zsh_dir.mkdir(parents=True, exist_ok=True)
        tmux_dir.mkdir(parents=True, exist_ok=True)

        # Use timestamp in filenames to allow multiple sessions on the same day
        asciinema_file: Path = asciinema_dir / f"{self.time_str}.cast"
        zsh_history_file: Path = zsh_dir / f"{self.time_str}.zsh_history"

        return SessionPaths(
            project_name=self.project_name,
            date_str=self.date_str,
            time_str=self.time_str,
            base_dir=base_dir,
            asciinema_file=asciinema_file,
            zsh_history_file=zsh_history_file,
            tmux_log_dir=tmux_dir
        )

    def _generate_tmux_conf(self) -> None:
        """
        @brief Generate a dynamic tmux configuration file.
        
        Creates a tmux configuration that includes the default settings
        plus additional hooks for logging pane output.
        """
        default_tmux_conf: Path = self.config.default_tmux_conf
        tmux_dynamic_path: Path = self.config.tmux_dynamic_conf

        # Read default tmux configuration if it exists
        default_content: str = ""
        if default_tmux_conf.exists():
            with open(default_tmux_conf, 'r') as default_file:
                default_content = default_file.read()
        else:
            print(f"Warning: Default tmux config not found at {default_tmux_conf}")
            print("Using minimal configuration.")

        # Add hooks to automatically log all pane output for complete session captures
        # Add zshrc Path for Logging zsh_history
        logdir: Path = self.paths.tmux_log_dir
        add_setting: str = f"""
set-hook -g after-split-window 'pipe-pane -o "cat >> {logdir}/#{{session_name}}-#{{window_index}}-#{{pane_index}}-%Y%m%d-%H%M%S.log"'
set-hook -g after-new-window 'pipe-pane -o "cat >> {logdir}/#{{session_name}}-#{{window_index}}-#{{pane_index}}-%Y%m%d-%H%M%S.log"'
set-hook -g session-created 'pipe-pane -o "cat >> {logdir}/#{{session_name}}-#{{window_index}}-#{{pane_index}}-%Y%m%d-%H%M%S.log"'
set-environment -g ZDOTDIR {self.config.tmp_dir}
"""
        full_conf: str = default_content + "\n" + add_setting

        # Write to a separate file to avoid modifying user's original configuration
        with open(tmux_dynamic_path, 'w') as f:
            f.write(full_conf)

    def _generate_zdotdir(self) -> None:
        """
        @brief Generate a temporary zsh configuration.
        
        Creates a .zshrc file in the temporary directory that sources
        the user's default configuration and sets up history logging.
        """
        tmp_zshrc: Path = self.config.tmp_dir / ".zshrc"
        default_zshrc: Path = self.config.default_zshrc

        # Configure zsh to use a separate history file for this session
        # while preserving the user's original zsh configuration
        content: str = f"""
source {default_zshrc}
export HISTFILE={self.paths.zsh_history_file}
export HISTSIZE=10000
export SAVEHIST=10000
setopt INC_APPEND_HISTORY
setopt SHARE_HISTORY
"""
        tmp_zshrc.write_text(content)

    def create_tmux_session(self) -> None:
        """
        @brief Create a new tmux session with the configured settings.
        
        Generates configuration files and starts a detached tmux session.
        
        @throws FileNotFoundError If a required configuration file is missing.
        @throws RuntimeError If session creation fails.
        """
        try: 
            self._generate_tmux_conf()
            self._generate_zdotdir()

            # Create a detached session so we can attach to it with asciinema later
            subprocess.run([
                "tmux",
                "-f",
                str(self.config.tmux_dynamic_conf),
                "new-session",
                "-d",
                "-s",
                self.tmux_session,
                "zsh"
            ], check=True, capture_output=True, text=True)
            print(f"Created tmux session: {self.tmux_session}")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Required configuration file not found: {e}") from e
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise RuntimeError(f"Failed to create tmux session: {error_msg}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error creating tmux session: {e}") from e


    def start_recording(self) -> None:
        """
        @brief Start asciinema recording of the tmux session.
        
        Launches asciinema to record the tmux session and save the output
        to the configured file.
        
        @throws RuntimeError If recording fails to start.
        """
        print(f"Starting asciinema recording to: {self.paths.asciinema_file}")

        # Use asciinema to record the tmux session interaction
        # This is a blocking call that returns when the session ends
        subprocess.run([
            "asciinema",
            "rec",
            "-c",
            f"tmux attach -t {self.tmux_session}",
            str(self.paths.asciinema_file)
        ], check=True, capture_output=True, text=True)


    def wait_for_tmux_exit(self) -> None:
        """
        @brief Wait for the tmux session to terminate.
        
        Polls the tmux session status at regular intervals until
        the session no longer exists.
        """
        # Poll until the session ends to ensure complete recording
        while True:
            result = subprocess.run([
                "tmux", 
                "has-session", 
                "-t", 
                self.tmux_session
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                # Non-zero return code means the session no longer exists
                print("Tmux Session is closed.")
                break
            time.sleep(1)

    def _tmux_session_exists(self, session_name: str) -> bool:
        """
        @brief Check if a tmux session exists.
        
        @param session_name Name of the tmux session to check.
        @return True if the session exists, False otherwise.
        """
        # Check if the specified tmux session exists
        result: subprocess.CompletedProcess = subprocess.run([
            "tmux",
            "has-session",
            "-t",
            session_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Return code 0 means the session exists
        return result.returncode == 0
    

    def cleanup_resources(self) -> None:
        """
        @brief Clean up resources created during recording.
        
        Terminates the tmux session if it's still running and removes
        temporary directories created during the session.
        """
        print("Cleaning up resources...")
        try:
            # Ensure tmux session is terminated to avoid orphaned sessions
            if self._tmux_session_exists(self.tmux_session):
                print(f"Terminating tmux session: {self.tmux_session}")
                subprocess.run([
                    "tmux", 
                    "kill-session", 
                    "-t", 
                    self.tmux_session
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        except Exception as e:
            print(f"Warning: Could not terminate tmux session: {e}")
        
        try:
            # Remove temporary directory
            tmp_dir: Path = self.config.tmp_dir
            if tmp_dir.exists():
                print(f"Removing temporary directory: {tmp_dir}")
                shutil.rmtree(tmp_dir)
                print("Temporary directory removed successfully.")
        except Exception as e:
            print(f"Warning: Could not remove temporary directory: {e}")


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


def main() -> None:
    """
    @brief Entry point for the application.
    
    Parses command-line arguments and initializes the recording process.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Record a tmux session with asciinema and zsh logging.")
    parser.add_argument("project", help="Project name (used to create directory structure)")
    parser.add_argument("--session", help="tmux session name (default: project_name_date)")
    parser.add_argument("--keep_tmp", action="store_true", help="save tmp dir")
    args: argparse.Namespace = parser.parse_args()

    # Initialize configuration and recorder
    config: AppConfig = AppConfig.from_defaults()
    recorder: TmuxAsciinemaRecorder = TmuxAsciinemaRecorder(
        project_name=args.project, 
        tmux_session=args.session,
        config=config
    )

    # For debugging: optionally retain temporary files
    if args.keep_tmp:
        import atexit
        atexit.unregister(recorder.cleanup_resources)
        print("[DEBUG]: Disable Cleanup Tmp_Dir")

    # Start the recording process
    recorder.run()


if __name__ == "__main__":
    main()
