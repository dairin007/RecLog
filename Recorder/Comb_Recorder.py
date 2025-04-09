from pathlib import Path
from typing import List, Dict, Any, Optional

from Recorder.Recorder import AbstractRecorder


class CompositeRecorder(AbstractRecorder):
    """
    @brief Composite recorder that coordinates multiple recorders.
    
    This class implements the Composite pattern to manage multiple recorders
    of different types as a single unit. This allows for flexible combinations
    of recording methods (e.g., tmux + video) with a unified interface.
    """
    
    def __init__(self, project_name: str, recorders: List[AbstractRecorder] = None):
        """
        @brief Initialize the composite recorder.
        
        @param project_name Name of the project being recorded.
        @param recorders List of recorder instances to be managed.
        """
        super().__init__(project_name)
        self.recorders: List[AbstractRecorder] = recorders or []
        
    def add_recorder(self, recorder: AbstractRecorder) -> None:
        """
        @brief Add a recorder to the composite.
        
        @param recorder The recorder instance to add.
        """
        if recorder not in self.recorders:
            self.recorders.append(recorder)
    
    def remove_recorder(self, recorder: AbstractRecorder) -> None:
        """
        @brief Remove a recorder from the composite.
        
        @param recorder The recorder instance to remove.
        """
        if recorder in self.recorders:
            self.recorders.remove(recorder)
    
    def get_output_path(self) -> Path:
        """
        @brief Get the path where the recording will be saved.
        
        In this case, returns the base project directory.
        
        @return Path to the output directory.
        """
        # By default, return the path to the main project directory
        return Path.home() / "project" / self.project_name / "Log" / self.date_str
    
    def setup(self) -> None:
        """
        @brief Set up all managed recorders.
        """
        for recorder in self.recorders:
            recorder.setup()
            
    def start_recording(self) -> None:
        """
        @brief Start recording on all managed recorders.
        """
        if self._is_recording:
            print("Recording is already in progress")
            return
            
        self._is_recording = True
        
        # Start each recorder
        for recorder in self.recorders:
            recorder.start_recording()
    
    def stop_recording(self) -> Optional[Dict[str, Path]]:
        """
        @brief Stop recording on all managed recorders.
        
        @return Dictionary mapping recorder type names to output paths.
        """
        if not self._is_recording:
            return None
            
        self._is_recording = False
        
        # Stop each recorder and collect output paths
        results = {}
        for recorder in self.recorders:
            output_path = recorder.stop_recording()
            if output_path:
                # Use the class name as the key
                recorder_type = type(recorder).__name__
                results[recorder_type] = output_path
        
        return results if results else None
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        @brief Get combined session information from all recorders.
        
        @return Dictionary containing combined session details.
        """
        # Start with basic session info
        info = {
            "project_name": self.project_name,
            "date": self.date_str,
            "time": self.time_str,
            "recorders": []
        }
        
        # Add info from each recorder
        for recorder in self.recorders:
            recorder_type = type(recorder).__name__
            recorder_info = recorder.get_session_info()
            info[recorder_type] = recorder_info
            info["recorders"].append(recorder_type)
            
        return info