from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class Reporter(ABC):
    """
    @brief Abstract base class for all reporters.
    
    Defines the common interface that all reporter classes must implement.
    """
    
    @abstractmethod
    def print_session_start(self, session_info: Dict[str, Any]) -> None:
        """
        @brief Print information about the starting session.
        
        @param session_info Dictionary containing session details.
        """
        pass
    
    @abstractmethod
    def print_recording_start(self) -> None:
        """
        @brief Print information about the recording start.
        """
        pass
    
    @abstractmethod
    def print_recording_complete(self, output_file: Optional[Path] = None) -> None:
        """
        @brief Print information about the completed recording.
        
        @param output_file Optional path to the output file.
        """
        pass
    
    @abstractmethod
    def print_output_location(self, output_path: Path) -> None:
        """
        @brief Print information about the output location.
        
        @param output_path Path to the output.
        """
        pass


class TmuxSessionReporter(Reporter):
    """
    @brief Reporter for tmux session recording.
    
    Handles reporting of tmux session recording progress and results.
    """
    
    def print_session_start(self, session_info: Dict[str, Any]) -> None:
        """
        @brief Print information about the starting tmux session.
        
        @param session_info Dictionary containing session details.
        """
        print("=" * 60) 
        print(f"Recording session for project: {session_info['project_name']}")
        print(f"Date: {session_info['date']}, Time: {session_info['time']}")
        print("=" * 60)
        print(f"[+] Creating tmux session '{session_info['tmux_session']}'...")
    
    def print_recording_start(self) -> None:
        """
        @brief Print information about the recording session by asciinema.
        """
        print("[+] Starting asciinema recording.")
    
    def print_recording_complete(self, output_file: Optional[Path] = None) -> None:
        """
        @brief Print information about the stopping session.
        
        @param output_file Not used in this implementation.
        """
        print("[+] Recording session complete by asciinema.")
    
    def print_output_location(self, output_path: Path) -> None:
        """
        @brief Print information about a specific output location.
        
        @param output_path Path to the output file.
        """
        if output_path.name.endswith(".cast"):
            print(f"- Asciinema recording: {output_path}")
        elif output_path.name.endswith(".zsh_history"):
            print(f"- Zsh history: {output_path}")
        elif output_path.is_dir():
            print(f"- Tmux logs: {output_path}/*.log")
    
    def print_output_locations(self, session_info: Dict[str, Any]) -> None:
        """
        @brief Print information about all output directories.
        
        @param session_info Dictionary containing session paths.
        """
        print("\nRecording outputs:")
        self.print_output_location(session_info["asciinema_file"])
        self.print_output_location(session_info["zsh_history_file"])
        self.print_output_location(session_info["tmux_log_dir"])
        
        print("\nSession completed. Resources will be cleaned up on exit.")
        print("=" * 60)


class VideoReporter(Reporter):
    """
    @brief Reporter for video recording.
    
    Handles reporting of video recording progress and results.
    """
    
    def print_session_start(self, session_info: Dict[str, Any]) -> None:
        """
        @brief Print information about the starting video session.
        
        @param session_info Dictionary containing session details.
        """
        print("-" * 60)
        print("Video recording: Enabled")
        print("-" * 60)
    
    def print_recording_start(self) -> None:
        """
        @brief Print information about starting video recording.
        """
        print("[+] Starting video recording...")
    
    def print_recording_complete(self, output_file: Optional[Path] = None) -> None:
        """
        @brief Print information about completed video recording.
        
        @param output_file Path to the recorded video file
        """
        print("[+] Video recording stopped.")
        
        if output_file:
            print(f"[+] Video file created: {output_file}")
    
    def print_output_location(self, output_path: Path) -> None:
        """
        @brief Print information about the video output location.
        
        @param output_path Path to the video output file.
        """
        print(f"- Video recording: {output_path}")