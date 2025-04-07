import argparse
import atexit

from app_config import AppConfig
from tmux_recorder import TmuxAsciinemaRecorder
from session_reporter import SessionReporter

def main() -> None:
    """
    @brief Entry point for the application.
    
    Parses command-line arguments and initializes the recording process.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Record a tmux session with asciinema and zsh logging.")
    parser.add_argument("project", help="Project name (used to create directory structure)")
    parser.add_argument("--session", help="tmux session name (default: project_name_date)")
    parser.add_argument("--keep_tmp", action="store_true", help="save tmp dir")
    parser.add_argument("--quiet", action="store_true", help="minimize output messages")
    args: argparse.Namespace = parser.parse_args()

    # Initialize configuration and recorder
    config: AppConfig = AppConfig.from_defaults()
    recorder: TmuxAsciinemaRecorder = TmuxAsciinemaRecorder(
        project_name=args.project, 
        tmux_session=args.session,
        config=config
    )

    # For debugging: optionally retain temporary files
    if args.keep_tmp:
        atexit.unregister(recorder.cleanup_resources)
        print("[DEBUG]: Disable Cleanup Tmp_Dir")

    # Get session information
    session_info = recorder.get_session_info()
    
    # Initialize logger
    reporter = SessionReporter()
    
    # Display start information (unless quiet mode is enabled)
    if not args.quiet:
        reporter.print_session_start(session_info)
    
    # Setup recording environment
    recorder._setup_recording()
    
    # Display recording start information
    if not args.quiet:
        reporter.print_recording_start()
    
    # Perform the recording
    recorder.run()
    
    # Display completion information
    if not args.quiet:
        reporter.print_recording_complete()
        reporter.print_output_locations(session_info)


if __name__ == "__main__":
    main()