from pathlib import Path
from settingcode.app_config import AppConfig
from settingcode.session_paths import SessionPaths


class ConfigGenerator:
    """
    @brief Handles generation of configuration files for tmux and zsh.
    
    Responsible for creating temporary configuration files that enable
    logging while preserving user settings.
    """
    
    def __init__(self, config: AppConfig, paths: SessionPaths):
        """
        @brief Initialize the configuration generator.
        
        @param config AppConfig instance with path information.
        @param paths SessionPaths instance with session-specific paths.
        """
        self.config = config
        self.paths = paths
        
    def generate_tmux_conf(self) -> Path:
        """
        @brief Generate a dynamic tmux configuration file.
        
        Creates a tmux configuration that includes the default settings
        plus additional hooks for logging pane output.
        
        @return Path to the generated configuration file.
        """
        default_tmux_conf: Path = self.config.default_tmux_conf
        tmux_dynamic_path: Path = self.config.tmux_dynamic_conf

        # Read default tmux configuration if it exists
        default_content: str = ""
        if default_tmux_conf.exists():
            with open(default_tmux_conf, 'r') as default_file:
                default_content = default_file.read()
        else:
            print(f"Warning: Default tmux config not found at {default_tmux_conf}")
            print("Using minimal configuration.")

        # Add hooks to automatically log all pane output for complete session captures
        # Add zshrc Path for Logging zsh_history
        logdir: Path = self.paths.tmux_log_dir
        add_setting: str = f"""
set-hook -g after-split-window 'pipe-pane -o "cat >> {logdir}/#{{session_name}}-#{{window_index}}-#{{pane_index}}-%Y%m%d-%H%M%S.log"'
set-hook -g after-new-window 'pipe-pane -o "cat >> {logdir}/#{{session_name}}-#{{window_index}}-#{{pane_index}}-%Y%m%d-%H%M%S.log"'
set-hook -g session-created 'pipe-pane -o "cat >> {logdir}/#{{session_name}}-#{{window_index}}-#{{pane_index}}-%Y%m%d-%H%M%S.log"'
set-environment -g ZDOTDIR {self.config.tmp_dir}
"""
        full_conf: str = default_content + "\n" + add_setting

        # Write to a separate file to avoid modifying user's original configuration
        with open(tmux_dynamic_path, 'w') as f:
            f.write(full_conf)
            
        return tmux_dynamic_path

    def generate_zdotdir(self) -> Path:
        """
        @brief Generate a temporary zsh configuration.
        
        Creates a .zshrc file in the temporary directory that sources
        the user's default configuration and sets up history logging.
        
        @return Path to the directory containing the generated zsh configuration.
        """
        tmp_zshrc: Path = self.config.tmp_dir / ".zshrc"
        default_zshrc: Path = self.config.default_zshrc

        # Configure zsh to use a separate history file for this session
        # while preserving the user's original zsh configuration
        content: str = f"""
source {default_zshrc}
export HISTFILE={self.paths.zsh_history_file}
export HISTSIZE=10000
export SAVEHIST=10000
setopt INC_APPEND_HISTORY
setopt SHARE_HISTORY
"""
        tmp_zshrc.write_text(content)
        
        return self.config.tmp_dir