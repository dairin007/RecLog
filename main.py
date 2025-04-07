import argparse
import atexit

from app_config import AppConfig
from tmux_recorder import TmuxAsciinemaRecorder


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

    # Start the recording process
    recorder.run()


if __name__ == "__main__":
    main()