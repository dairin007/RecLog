import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from Recorder.ab_recorder import AbstractRecorder
from settingcode.app_static_config import AppStaticSettings
from settingcode.app_session_config import AppSessionConfig


class VideoRecorder(AbstractRecorder):
    """
    @brief Class for handling full-screen recording functionality

    Uses ffmpeg to record the screen as a single video file.
    """

    def __init__(self, static_config: AppStaticSettings, session_config: AppSessionConfig,output_dir: Optional[Path] = None):
        """
        @brief Initialize the video recorder

        @param project_name Project name (used in filenames)
        @param video_quality Encoder quality setting (low, medium, high)
        @param framerate Capture framerate (lower means smaller file size)
        @param output_dir Optional custom directory to save recordings
        """
        # Config
        self.static_config: AppStaticSettings = static_config
        self.session_config: AppSessionConfig = session_config

        self.video_quality = 'low'
        self.framerate = 15

        # Set output directory
        self.output_dir = output_dir or self.session_config.video_dir
        self._output_file=self.session_config.video_file

        # Internal state
        self._process: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._start_time = datetime.now()

        self._is_recording=False

    def _get_video_settings(self) -> List[str]:
        """
        @brief Get ffmpeg settings based on quality setting

        @return List of ffmpeg parameters
        """
        # Quality preset mapping
        quality_presets = {
            "low": ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28"],
            "medium": ["-c:v", "libx264", "-preset", "medium", "-crf", "23"],
            "high": ["-c:v", "libx264", "-preset", "slow", "-crf", "18"]
        }

        # Use medium quality if specified quality not found
        return quality_presets.get(self.video_quality, quality_presets["medium"])

    def setup(self) -> None:
        """
        @brief Perform any necessary setup before recording can begin.

        Creates the output directory if it doesn't exist.
        """
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def start_recording(self) -> None:
        """
        @brief Start the screen recording process

        Launches ffmpeg in a separate thread to record the screen
        """
        # if self.is_recording:
        #     print("video Recording is already in progress")
        #     return

        # Setup before recording
        self.setup()

        self._is_recording = True

        # Start recording in a separate thread
        self._thread = threading.Thread(target=self._recording_thread)
        self._thread.daemon = True
        self._thread.start()

    def _recording_thread(self) -> None:
        """
        @brief Thread function that handles the recording process

        Manages ffmpeg process for continuous recording
        """
        # Get quality settings
        video_settings = self._get_video_settings()

        # Build the ffmpeg command
        # This works on most Linux systems with X11
        cmd = [
            "ffmpeg",
            "-f", "x11grab",      # X11 display grabbing
            "-framerate", str(self.framerate),
            "-i", ":0.0",         # Display identifier
            "-r", str(self.framerate),
            "-vf", "crop=iw:floor(ih/2)*2",
            *video_settings,
            "-pix_fmt", "yuv420p",  # Ensure compatibility
            "-f", "mp4",
            "-loglevel", "error",   # Reduce ffmpeg output to errors only
            str(self._output_file)
        ]

        # Start ffmpeg process for screen recording
        try:
            # Using subprocess.PIPE for stderr to properly capture errors
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self._process.wait()

        except Exception as e:
            # Ensure proper line breaks in error messages
            print(f"\nError during video recording: {e}")
            self._is_recording = False

    def is_recording(self) -> bool:
        process_running = self._process is not None and self._process.poll() is None
        return self._is_recording and process_running

    def stop_recording(self):
        """
        @brief Stop the ongoing recording

        @return Path to the recorded video file, or None if no recording was in progress
        """
        if not self.is_recording():
            print("No recording in progress")
            self._process = None
            self._thread = None
            return {}

        self._is_recording = False
        recorded_file_path = self._output_file

        # Terminate the ffmpeg process
        try:
            if self._process.stdin and not self._process.stdin.closed:
                self._process.stdin.write('q\n')
                self._process.stdin.flush()
            else:
                print("stdin is already closed, cannot send 'q'")

            self._process.wait(timeout=10)

        except subprocess.TimeoutExpired:
            print("Timeout waiting for ffmpeg to stop. Forcing kill.")
            self._process.kill()
            self._process.wait()
        except Exception as e:
            print(f"Error stopping ffmpeg: {e}")

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        final_file_exists = recorded_file_path and recorded_file_path.exists()
        final_file_has_size = final_file_exists and recorded_file_path.stat().st_size > 0

        if final_file_has_size:
            # Calculate recording duration
            duration = datetime.now() - self._start_time
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            result = {
            "outputs": {
                "video": recorded_file_path
            },
            "metadata": {
                "project_name": self.session_config.project_name,
                "duration": str(datetime.now() - self._start_time),
                "time": f"{hours}h_{minutes}m_{seconds}s"
            }
        }
        elif final_file_exists:
            print(f"Recorded File '{recorded_file_path}' is Empty.")
            result = {}
        else:
            print("Recorded File is not Generated.")
            result = {}

        # Reset internal state for next recording
        self._process = None
        self._thread = None

        return result

    def get_session_info(self) -> Dict[str, Any]:
        """
        @brief Get information about the current recording session.

        @return Dictionary containing session details.
        """
        return {
            "project_name": self.session_config.project_name,
            "date": self.session_config.date_str,
            "time": self.session_config.time_str,
            "video_quality": self.video_quality,
            "framerate": self.framerate,
            "output_file": str(self._output_file) if self._output_file else None,
            "output_dir": str(self.output_dir)
        }

    def wait_for_completion(self) -> None:
        """
        @brief Wait for the video recording to complete.

        Since video recording runs in a separate thread, this method
        checks if the recording thread is still active and waits for it to finish.
        """
        # video recorder is not required this method
        if self._is_recording and self._thread and self._thread.is_alive():
            # タイムアウトを設定しない場合は、スレッドが完全に終了するまで待機
            self._thread.join()