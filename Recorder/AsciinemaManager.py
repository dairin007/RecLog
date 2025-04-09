import subprocess
from pathlib import Path


class AsciinemaManager:
    """
    @brief Handles asciinema recording of tmux sessions.
    
    Manages the asciinema recording process for capturing terminal sessions.
    """
    
    def __init__(self, output_file: Path):
        """
        @brief Initialize the recorder.
        
        @param output_file Path where the recording will be saved.
        """
        self.output_file = output_file
        
    def start_recording(self, tmux_session: str) -> None:
        """
        @brief Start asciinema recording of the tmux session.
        
        Launches asciinema to record the tmux session and save the output
        to the configured file.
        
        @param tmux_session Name of the tmux session to record.
        @throws RuntimeError If recording fails to start.
        """

        # Use asciinema to record the tmux session interaction
        # This is a blocking call that returns when the session ends
        try:
            subprocess.run([
                "asciinema",
                "rec",
                "-c",
                f"tmux attach -t {tmux_session}",
                str(self.output_file)
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            raise RuntimeError(f"Failed to record with asciinema: {error_msg}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during recording: {e}") from e