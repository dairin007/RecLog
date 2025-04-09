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
    def print_recorder_results(self, results: Dict[str, Any]) -> None:
        """
        @brief Print recording results.
        
        @param results Dictionary containing recording outputs and metadata.
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

    def print_recorder_results(self, results: Dict[str, Any]) -> None:
        """
        @brief Print video recording results.
        """
        outputs = results.get("outputs", {})
        
        if "video" in outputs:
            video_path = outputs["video"]
            print(f"- Video recording: {video_path}")