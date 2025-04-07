import shutil
from pathlib import Path
from tmux_session import TmuxSessionManager


class ResourceCleaner:
    """
    @brief Handles cleanup of resources created during recording.
    
    Responsible for terminating tmux sessions and removing temporary files.
    """
    
    def __init__(self, tmux_manager: TmuxSessionManager, tmp_dir: Path):
        """
        @brief Initialize the resource cleaner.
        
        @param tmux_manager TmuxSessionManager instance for the session.
        @param tmp_dir Path to the temporary directory to clean up.
        """
        self.tmux_manager = tmux_manager
        self.tmp_dir = tmp_dir
        
    def cleanup(self) -> None:
        """
        @brief Clean up resources created during recording.
        
        Terminates the tmux session if it's still running and removes
        temporary directories created during the session.
        """
        print("Cleaning up resources...")
        
        # Terminate tmux session
        try:
            if self.tmux_manager.session_exists():
                self.tmux_manager.terminate_session()
        except Exception as e:
            print(f"Warning: Could not terminate tmux session: {e}")
        
        # Remove temporary directory
        try:
            if self.tmp_dir.exists():
                print(f"Removing temporary directory: {self.tmp_dir}")
                shutil.rmtree(self.tmp_dir)
                print("Temporary directory removed successfully.")
        except Exception as e:
            print(f"Warning: Could not remove temporary directory: {e}")
