from pathlib import Path
from typing import List, Dict, Any, Optional

from Recorder.Recorder import AbstractRecorder
from Reporter.reporter import Reporter


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
            return {}
            
        self._is_recording = False
        
        # Stop each recorder and collect output paths
        results = {}
        for recorder in self.recorders:
            recorder_result = recorder.stop_recording()
            if recorder_result:
                # Use the class name as the key
                recorder_type = type(recorder).__name__
                results[recorder_type] = recorder_result
        
        return results
    
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

    def wait_for_completion(self) -> None:
        """
        @brief Wait for all managed recorders to complete.
        
        Calls wait_for_completion() on all managed recorders.
        """
        for recorder in self.recorders:
            recorder.wait_for_completion()

    def print_completion_status(self, results: Dict[str, Path], quiet: bool = False) -> None:
        if quiet:
            return
            
        for recorder in self.recorders:
            recorder_type = type(recorder).__name__
            reporter = self._get_reporter_for_recorder(recorder)
            
            if reporter:
                output_path = results.get(recorder_type, None)
                reporter.print_recording_complete(output_path)

    def _get_reporter_for_recorder(self, recorder) -> Optional['Reporter']:
        recorder_type = type(recorder).__name__
        if recorder_type == "TmuxAsciinemaRecorder":
            from Reporter.reporter import TmuxSessionReporter
            return TmuxSessionReporter()
        elif recorder_type == "VideoRecorder":
            from Reporter.reporter import VideoReporter
            return VideoReporter()
        return None
    
    def print_results(self, results: Dict[str, Dict[str, Any]], quiet: bool = False) -> None:
        """
        @brief Print results from all recorders.
        
        @param results Results dictionary from stop_recording
        @param quiet Flag to minimize output
        """
        if quiet:
            return
            
        for recorder in self.recorders:
            recorder_type = type(recorder).__name__
            
            if recorder_type in results:
                # Get reporter for this recorder
                reporter = self._get_reporter_for_recorder(recorder)
                if reporter:
                    # Print completion status
                    reporter.print_recording_complete()
                    # Print detailed results
                    reporter.print_recorder_results(results[recorder_type])