import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List


class VideoRecorder:
    """
    @brief Class for handling full-screen recording functionality
    
    Uses ffmpeg to record the screen as a single video file.
    """
    
    def __init__(self, output_dir: Path, project_name: str, 
                 video_quality: str = "medium",
                 framerate: int = 15):
        """
        @brief Initialize the video recorder
        
        @param output_dir Directory to save recordings
        @param project_name Project name (used in filenames)
        @param video_quality Encoder quality setting (low, medium, high)
        @param framerate Capture framerate (lower means smaller file size)
        """
        self.output_dir = output_dir
        self.project_name = project_name
        self.video_quality = video_quality
        self.framerate = framerate
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Internal state
        self._recording = False
        self._process: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._start_time = datetime.now()
        self._output_file: Optional[Path] = None

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
    
    def _get_output_filename(self) -> Path:
        """
        @brief Generate output filename for the video
        
        @return Path to the output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{self.project_name}_{timestamp}.mp4"
    
    def start_recording(self) -> None:
        """
        @brief Start the screen recording process
        
        Launches ffmpeg in a separate thread to record the screen
        """
        if self._recording:
            print("Recording is already in progress")
            return
        
        self._recording = True
        self._start_time = datetime.now()
        self._output_file = self._get_output_filename()
        
        # Start recording in a separate thread
        self._thread = threading.Thread(target=self._recording_thread)
        self._thread.daemon = True
        self._thread.start()
        
        print(f"Screen recording started. Output directory: {self.output_dir}")
    
    def _recording_thread(self) -> None:
        """
        @brief Thread function that handles the recording process
        
        Manages ffmpeg process for continuous recording
        """
        # Get quality settings
        video_settings = self._get_video_settings()
        
        # Start ffmpeg process for screen recording
        try:
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
                str(self._output_file)
            ]
            
            print(f"Starting video recording: {self._output_file}")
            self._process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE, # stderrをパイプに接続
                text=True # エラー出力をテキストとして扱う
            )
            
            # Wait for the process to complete (when stop_recording is called)
            stdout, stderr = self._process.communicate() # wait()の代わりにcommunicate()を使う
            if stderr:
                print("--- FFmpeg Error Output ---")
                print(stderr)
                print("-------------------------")
            
        except Exception as e:
            print(f"Error during video recording: {e}")
            self._recording = False
    
    def stop_recording(self):
        """
        @brief Stop the ongoing recording
        
        @return Path to the recorded video file, or None if no recording was in progress
        """
        if not self._recording or not self._output_file:
            print("No recording in progress")
            return None
        
        self._recording = False
        
        # Terminate the ffmpeg process
        if self._process and self._process.poll() is None:
            try:
                # Send SIGTERM to ffmpeg (more graceful than kill)
                self._process.terminate()
                
                # Give it time to clean up
                time.sleep(1)
                
                # Force kill if still running
                if self._process.poll() is None:
                    self._process.kill()
            except Exception as e:
                print(f"Error stopping recording: {e}")
        
        # Wait for the thread to complete
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        
        # Calculate recording duration
        duration = datetime.now() - self._start_time
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f"Recording stopped. Total duration: {hours}h {minutes}m {seconds}s")
        print(f"Recorded video: {self._output_file}")
        
        return self._output_file