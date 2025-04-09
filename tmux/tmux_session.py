import subprocess
from pathlib import Path
import time


class TmuxSessionManager:
    """
    @brief Manages tmux session lifecycle.
    
    Handles creation, monitoring, and termination of tmux sessions.
    """
    
    def __init__(self, tmux_session_name: str):
        """
        @brief Initialize the tmux session manager.
        
        @param session_name Name of the tmux session to manage.
        """
        self.session_name = tmux_session_name
        
    def create_session(self, config_path: Path) -> None:
        """
        @brief Create a new tmux session with the provided configuration.
        
        @param config_path Path to the tmux configuration file to use.
        @throws RuntimeError If session creation fails.
        """
        try:
            # Create a detached session so we can attach to it with asciinema later
            subprocess.run([
                "tmux",
                "-f",
                str(config_path),
                "new-session",
                "-d",
                "-s",
                self.session_name,
                "zsh"
            ], check=True, capture_output=True, text=True)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Required configuration file not found: {e}") from e
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise RuntimeError(f"Failed to create tmux session: {error_msg}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error creating tmux session: {e}") from e
            
    def session_exists(self) -> bool:
        """
        @brief Check if the tmux session exists.
        
        @return True if the session exists, False otherwise.
        """
        # Check if the specified tmux session exists
        result: subprocess.CompletedProcess = subprocess.run([
            "tmux",
            "has-session",
            "-t",
            self.session_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Return code 0 means the session exists
        return result.returncode == 0
        
    def wait_for_exit(self) -> None:
        """
        @brief Wait for the tmux session to terminate.
        
        Polls the tmux session status at regular intervals until
        the session no longer exists.
        """
        # Poll until the session ends to ensure complete recording
        while True:
            if not self.session_exists():
                break
            time.sleep(1)
            
    def terminate_session(self) -> bool:
        """
        @brief Terminate the tmux session.
        
        @return True if the session was terminated, False if it did not exist.
        """
        if not self.session_exists():
            return False
            
        print(f"Terminating tmux session: {self.session_name}")
        subprocess.run([
            "tmux", 
            "kill-session", 
            "-t", 
            self.session_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        
        return True