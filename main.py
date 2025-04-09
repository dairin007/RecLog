import argparse
import atexit
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys
sys.dont_write_bytecode = True

from settingcode.app_config import AppConfig
from Recorder.Recorder import AbstractRecorder
from Recorder.n_asciinema_recorder import TmuxAsciinemaRecorder
from Recorder.n_video_recorder import VideoRecorder
from Recorder.Comb_Recorder import CompositeRecorder
from Reporter.reporter import Reporter, TmuxSessionReporter, VideoReporter
from misc.resource_cleaner import ResourceCleaner


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
    composite_recorder = CompositeRecorder(project_name=args.project)

    # Add tmux recorder
    tmux_recorder = TmuxAsciinemaRecorder(
        project_name=args.project, 
        tmux_session_name=args.session,
        config=config
    )
    composite_recorder.add_recorder(tmux_recorder)

    # Add video recorder if enabled
    video_recorder: Optional[VideoRecorder] = None
    if args.video:
        video_recorder = VideoRecorder(
            project_name=args.project,
            video_quality=args.video_quality,
            framerate=args.video_framerate
        )
        composite_recorder.add_recorder(video_recorder)

    # Initialize reporters using the abstract class
    tmux_reporter: Reporter = TmuxSessionReporter()
    video_reporter: Reporter = VideoReporter()
    
    # Get session information
    session_info = composite_recorder.get_session_info()

    # Display start information (unless quiet mode is enabled)
    if not args.quiet:
        tmux_reporter.print_session_start(session_info["TmuxAsciinemaRecorder"])
        
        # Print video recording info if enabled
        if args.video:
            video_reporter.print_session_start(session_info["VideoRecorder"])

    # Setup recorders
    composite_recorder.setup()
    
    # Start all recorders
    if not args.quiet:
        if args.video:
            video_reporter.print_recording_start()
        tmux_reporter.print_recording_start()

    # Start recording processes
    composite_recorder.start_recording()

    # Wait for recordings to complete (blocking until tmux session ends)
    composite_recorder.wait_for_completion()    

    # Stop all recorders and collect results
    results = composite_recorder.stop_recording()

    composite_recorder.print_results(results, quiet=args.quiet)

    print("=" * 60)

    # Clean up temporary resources
    if not args.keep_tmp:
        ResourceCleaner(config.tmp_dir).cleanup()


if __name__ == "__main__":
    main()