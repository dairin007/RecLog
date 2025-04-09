from dataclasses import dataclass
from pathlib import Path


@dataclass
class SessionPaths:
    """
    @brief Class for organizing session-related file paths.
    
    Stores paths to various files and directories used during a recording session.
    """
    project_name: str
    date_str: str
    time_str: str
    base_dir: Path
    asciinema_file: Path
    zsh_history_file: Path
    tmux_log_dir: Path


def generate_session_paths(project_name: str, date_str: str, time_str: str) -> SessionPaths:
    """
    @brief Generate all required paths for the recording session.
    
    Creates directories for asciinema recordings, zsh history, and tmux logs.
    
    @param project_name Name of the project being recorded.
    @param date_str Date string in YYYYMMDD format.
    @param time_str Time string in HHMMSS format.
    @return SessionPaths object containing all generated paths.
    """
    # Organize logs by project and date for better discoverability
    base_dir: Path = Path.home() / "project" / project_name / "Log" / date_str
    asciinema_dir: Path = base_dir / "asciinema"
    zsh_dir: Path = base_dir / "zsh"
    tmux_dir: Path = base_dir / "tmux"

    # Create all required directories to avoid runtime errors
    asciinema_dir.mkdir(parents=True, exist_ok=True)
    zsh_dir.mkdir(parents=True, exist_ok=True)
    tmux_dir.mkdir(parents=True, exist_ok=True)

    # Use timestamp in filenames to allow multiple sessions on the same day
    asciinema_file: Path = asciinema_dir / f"{time_str}.cast"
    zsh_history_file: Path = zsh_dir / f"{time_str}.zsh_history"

    return SessionPaths(
        project_name=project_name,
        date_str=date_str,
        time_str=time_str,
        base_dir=base_dir,
        asciinema_file=asciinema_file,
        zsh_history_file=zsh_history_file,
        tmux_log_dir=tmux_dir
    )