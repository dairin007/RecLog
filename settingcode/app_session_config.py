from dataclasses import dataclass
from pathlib import Path
import datetime
from settingcode.app_static_config import AppStaticSettings

@dataclass
class AppSessionConfig:
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
    video_dir: Path
    video_file: Path
    timestamp: datetime
    
    def __init__(self, project_name: str):
        """
        @brief Initialize session configuration with current timestamp.
        
        @param project_name Name of the project being recorded.
        """
        self.project_name = project_name
        self.timestamp = datetime.datetime.now()
        self.date_str = self.timestamp.strftime("%Y%m%d")
        self.time_str = self.timestamp.strftime("%H%M%S")
        
        self.base_dir = Path.home() / "project" / project_name / "Log" / self.date_str
        asciinema_dir = self.base_dir / "asciinema"
        zsh_dir = self.base_dir / "zsh"
        tmux_dir = self.base_dir / "tmux"
        video_dir = self.base_dir / "video"
        
        asciinema_dir.mkdir(parents=True, exist_ok=True)
        zsh_dir.mkdir(parents=True, exist_ok=True)
        tmux_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)
        
        self.asciinema_file = asciinema_dir / f"{self.time_str}.cast"
        self.zsh_history_file = zsh_dir / f"{self.time_str}.zsh_history"
        self.tmux_log_dir = tmux_dir
        self.video_dir = video_dir
        self.video_file = video_dir / f"{project_name}_{self.date_str}_{self.time_str}.mp4"