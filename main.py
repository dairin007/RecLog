import argparse
import atexit
from pathlib import Path
from datetime import datetime
from typing import Optional

from app_config import AppConfig
from tmux_recorder import TmuxAsciinemaRecorder
from video_record import VideoRecorder
from reporter import Reporter, TmuxSessionReporter, VideoReporter
from resource_cleaner import ResourceCleaner


def get_video_dir(project_name: str) -> Path:
    """
    @brief Generate the video output directory path
    
    @param project_name Name of the project
    @return Path to the video directory
    """
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    
    video_dir = Path.home() / "project" / project_name / "Log" / date_str / "video"
    video_dir.mkdir(parents=True, exist_ok=True)
    
    return video_dir

def main() -> None:
    """
    @brief Entry point for the application.
    
    Parses command-line arguments and initializes the recording process.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Record a tmux session with asciinema, zsh logging, and optional video recording.")
    parser.add_argument("project", help="Project name (used to create directory structure)")
    parser.add_argument("--session", help="tmux session name (default: project_name_date)")
    parser.add_argument("--keep_tmp", action="store_true", help="save tmp dir")
    parser.add_argument("--quiet", action="store_true", help="minimize output messages")
    
    # Video recording options
    video_group = parser.add_argument_group("Video Recording Options")
    video_group.add_argument("--video", action="store_true", help="enable video recording")
    video_group.add_argument("--video-quality", choices=["low", "medium", "high"], default="medium",
                            help="video recording quality (default: medium)")
    video_group.add_argument("--video-framerate", type=int, default=15,
                            help="video recording framerate (default: 15)")
    
    args = parser.parse_args()

    # Initialize configuration
    config = AppConfig.from_defaults()
    
    # Initialize the tmux recorder
    recorder = TmuxAsciinemaRecorder(
        project_name=args.project, 
        tmux_session_name=args.session,
        config=config
    )
    
    # Initialize reporters using the abstract class
    session_reporter: Reporter = TmuxSessionReporter()
    video_reporter: Reporter = VideoReporter()
    
    # For debugging: optionally retain temporary files
    if args.keep_tmp:
        atexit.unregister(recorder.cleanup_resources)
        print("[DEBUG]: Disable Cleanup Tmp_Dir")

    # Get session information
    session_info = recorder.get_session_info()
    
    # Check if video recording is enabled
    video_enabled = args.video
    
    # Display start information (unless quiet mode is enabled)
    if not args.quiet:
        session_reporter.print_session_start(session_info)
        
        # Print video recording info if enabled
        if video_enabled:
            video_reporter.print_session_start(session_info)
    
    # Initialize and start video recorder if enabled
    video_recorder: Optional[VideoRecorder] = None
    output_video: Optional[Path] = None
    
    if video_enabled:
        video_dir = get_video_dir(args.project)
        
        video_recorder = VideoRecorder(
            output_dir=video_dir,
            project_name=args.project,
            video_quality=args.video_quality,
            framerate=args.video_framerate
        )
        
        # Start video recording before tmux session
        if not args.quiet:
            video_reporter.print_recording_start()
        video_recorder.start_recording()
    
    # Display recording start information for tmux session
    if not args.quiet:
        session_reporter.print_recording_start()
    
    # Perform the tmux recording
    recorder.run()
    
    # Stop video recording after tmux session ends
    if video_enabled and video_recorder:
        if not args.quiet:
            print("[+] Stopping video recording...")
        output_video = video_recorder.stop_recording()
        if not args.quiet and output_video:
            video_reporter.print_recording_complete(output_video)
    
    # Display completion information
    if not args.quiet:
        session_reporter.print_recording_complete()
        
        # Print output locations for tmux session
        if isinstance(session_reporter, TmuxSessionReporter):
            session_reporter.print_output_locations(session_info)
            
        # Print video output location if video was recorded
        if video_enabled and output_video:
            video_reporter.print_output_location(output_video)
            
        print("=" * 60)

    ResourceCleaner(config.tmp_dir).cleanup()


if __name__ == "__main__":
    main()