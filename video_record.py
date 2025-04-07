import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List


class VideoRecorder:
    """
    @brief Class for handling full-screen recording functionality
    
    Uses ffmpeg to record the screen, with options for time-based segmentation
    and storage optimization.
    """
    
    def __init__(self, output_dir: Path, project_name: str, 
                 segment_duration: int = 3600, 
                 video_quality: str = "medium",
                 framerate: int = 15):
        """
        @brief Initialize the video recorder
        
        @param output_dir Directory to save recordings
        @param project_name Project name (used in filenames)
        @param segment_duration Duration of each segment in seconds (default: 3600 = 1 hour)
        @param video_quality Encoder quality setting (low, medium, high)
        @param framerate Capture framerate (lower means smaller file size)
        """
        self.output_dir = output_dir
        self.project_name = project_name
        self.segment_duration = segment_duration
        self.video_quality = video_quality
        self.framerate = framerate
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Internal state
        self._recording = False
        self._process: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._segment_count = 0
        self._start_time = datetime.now()
        self._segments: List[Path] = []
    
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
        @brief Generate output filename for the current segment
        
        @return Path to the output file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        segment_suffix = f"_part{self._segment_count}" if self._segment_count > 0 else ""
        return self.output_dir / f"{self.project_name}_{timestamp}{segment_suffix}.mp4"
    
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
        self._segment_count = 0
        self._segments = []
        
        # Start recording in a separate thread
        self._thread = threading.Thread(target=self._recording_thread)
        self._thread.daemon = True
        self._thread.start()
        
        print(f"Screen recording started. Output directory: {self.output_dir}")
    
    def _recording_thread(self) -> None:
        """
        @brief Thread function that handles the recording process
        
        Manages ffmpeg processes and implements segment rotation
        """
        while self._recording:
            output_file = self._get_output_filename()
            self._segments.append(output_file)
            
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
                    "-f", "alsa",         # Audio source
                    "-i", "default",      # Default audio device
                    "-r", str(self.framerate),
                    *video_settings,
                    "-pix_fmt", "yuv420p",  # Ensure compatibility
                    "-t", str(self.segment_duration),  # Segment duration
                    str(output_file)
                ]
                
                print(f"Starting new video segment: {output_file}")
                self._process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                
                # Wait for the process to complete (either by timeout or stop_recording call)
                self._process.wait()
                
                # Increment counter for next segment
                if self._recording:  # Only increment if still recording
                    self._segment_count += 1
                
            except Exception as e:
                print(f"Error during video recording: {e}")
                self._recording = False
                break
                
            # Check if we should continue recording
            if not self._recording:
                break
    
    def stop_recording(self) -> List[Path]:
        """
        @brief Stop the ongoing recording
        
        @return List of recorded segment paths
        """
        if not self._recording:
            print("No recording in progress")
            return []
        
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
        print(f"Recorded {len(self._segments)} segment(s)")
        
        return self._segments