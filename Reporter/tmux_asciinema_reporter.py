from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from Reporter.ab_reporter import AbstractReporter

class TmuxSessionReporter(AbstractReporter):
    """
    @brief Reporter for tmux session recording.
    
    Handles reporting of tmux session recording progress and results.
    """
    def print_recording_end(self) -> None:
        """
        @brief Print information about the tmux recording end.
        """
        print("[✓] Asciinema recording completed.")
    def print_session_start(self, session_info: Dict[str, Any]) -> None:
        """
        @brief Print information about the starting tmux session.
        
        @param session_info Dictionary containing session details.
        """
        print("=" * 60) 
        print(f"Recording session for project: {session_info['project_name']}")
        print(f"Date: {session_info['date']}, Time: {session_info['time']}")
    
    def print_recording_start(self) -> None:
        """
        @brief Print information about the recording session by asciinema.
        """
        print("[+] Starting asciinema recording.")

    def print_recorder_results(self, results: Dict[str, Any]) -> None:
        """
        @brief Print tmux recording results.
        """
        outputs = results.get("outputs", {})
        
        print("\nRecording outputs:")
        for output_type, path in outputs.items():
            if output_type == "asciinema":
                print(f"- Asciinema recording: {path}")
            elif output_type == "zsh_history":
                print(f"- Zsh history: {path}")
            elif output_type == "tmux_logs":
                print(f"- Tmux logs: {path}/*.log")
