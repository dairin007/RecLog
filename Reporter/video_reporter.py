from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from Reporter.ab_reporter import AbstractReporter

class VideoReporter(AbstractReporter):
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
    def print_recording_end(self) -> None:
        """
        @brief Print information about the video recording end.
        """
        print("[✓] Video recording completed.")
