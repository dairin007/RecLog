from pathlib import Path
from typing import Optional


class VideoReporter:
    """
    @brief Class for reporting video recording progress and results to the user.
    
    Separates video recording display/reporting concerns from other components.
    """
    
    @staticmethod
    def print_recording_start() -> None:
        """
        @brief Print information about starting video recording.
        """
        print("[+] Starting video recording...")
    
    @staticmethod
    def print_recording_complete(output_file: Optional[Path]) -> None:
        """
        @brief Print information about completed video recording.
        
        @param output_file Path to the recorded video file
        """
        print("[+] Video recording stopped.")
        
        if output_file:
            print(f"[+] Video file created: {output_file}")
    
    @staticmethod
    def print_output_location(output_file: Path) -> None:
        """
        @brief Print information about the video output location.
        
        @param output_file Path to the video output file.
        """
        print(f"- Video recording: {output_file}")
    
    @staticmethod
    def print_recording_enabled() -> None:
        """
        @brief Print information that video recording is enabled.
        """
        print("-" * 60)
        print("Video recording: Enabled")
        print("-" * 60)