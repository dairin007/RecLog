from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class AppStaticSettings:
    """
    @brief Configuration class for the application.
    
    Holds paths to various directories and files used by the application.
    """
    base_dir: Path
    settings_dir: Path
    tmp_dir: Path
    tmux_dynamic_conf: Path
    default_zshrc: Path
    default_tmux_conf: Path
    
    @classmethod
    def from_defaults(cls, base_dir: Optional[Path] = None) -> 'AppStaticSettings':
        """
        @brief Create an AppConfig instance with default values.
        
        @param base_dir Optional base directory path. If None, uses the parent directory of the current file.
        @return AppConfig instance initialized with default paths.
        """
        if base_dir is None:
            base_dir = Path(__file__).parent
            
        settings_dir: Path = base_dir / "settings"
        tmp_dir: Path = base_dir / "tmp"
        
        # Ensure temporary directory exists
        tmp_dir.mkdir(parents=True, exist_ok=True)
        
        return cls(
            base_dir=base_dir,
            settings_dir=settings_dir,
            tmp_dir=tmp_dir,
            tmux_dynamic_conf=tmp_dir / "generated_tmux.conf",
            default_zshrc=Path.home() / ".zshrc",
            default_tmux_conf=Path.home() / ".tmux.conf"
        )
