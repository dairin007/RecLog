import shutil
from pathlib import Path
from tmux.tmux_session import TmuxSessionManager


class ResourceCleaner:
    """
    @brief Handles cleanup of resources created during recording.
    
    Responsible for terminating tmux sessions and removing temporary files.
    """
    
    def __init__(self, tmp_dir: Path):
        """
        @brief Initialize the resource cleaner.
        
        @param tmux_manager TmuxSessionManager instance for the session.
        @param tmp_dir Path to the temporary directory to clean up.
        """
        self.tmp_dir = tmp_dir
        
    def cleanup(self) -> None:
        """
        @brief Clean up resources created during recording.
        
        Terminates the tmux session if it's still running and removes
        temporary directories created during the session.
        """
        # Remove temporary directory
        try:
            if self.tmp_dir.exists():
                shutil.rmtree(self.tmp_dir)
        except Exception as e:
            print(f"Warning: Could not remove temporary directory: {e}")
