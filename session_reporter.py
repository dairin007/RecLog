from typing import Dict, Any


class SessionReporter:
    """
    @brief Class for reporting session progress and results to the user.
    
    Separates display/reporting concerns from core functionality.
    """
    
    @staticmethod
    def print_session_start(session_info: Dict[str, Any]) -> None:
        """
        @brief Print information about the starting tmux session.
        
        @param session_info Dictionary containing session details.
        """
        print("=" * 60) 
        print(f"Recording session for project: {session_info['project_name']}")
        print(f"Date: {session_info['date']}, Time: {session_info['time']}")
        print("=" * 60)
        print(f"[+] Creating tmux session '{session_info['tmux_session']}'...")
    
    @staticmethod
    def print_recording_start() -> None:
        """
        @brief Print information about the recording session by asciinema.
        """
        print("[+] Starting asciinema recording.")
    
    @staticmethod
    def print_recording_complete() -> None:
        """
        @brief Print information about the stopping session.
        """
        print("[+] Recording session complete by asciinema.")
    
    @staticmethod
    def print_output_locations(session_info: Dict[str, Any]) -> None:
        """
        @brief Print information about the Output Directorys.
        
        @param session_info 
        """
        print("\nRecording outputs:")
        print(f"- Asciinema recording: {session_info['asciinema_file']}")
        print(f"- Zsh history: {session_info['zsh_history_file']}")
        print(f"- Tmux logs: {session_info['tmux_log_dir']}/*.log")
        print("\nSession completed. Resources will be cleaned up on exit.")
        print("=" * 60)