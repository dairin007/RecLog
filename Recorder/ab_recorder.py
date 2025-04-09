from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class AbstractRecorder(ABC):
    """
    @brief Abstract base class for all recorders.

    Defines the common interface that all recorder implementations must adhere to.
    This ensures consistency across different types of recorders.
    """

    def __init__(self):
        """
        @brief Initialize a new recorder instance.

        @param project_name Name of the project being recorded.
        """
        pass

    @abstractmethod
    def get_output_path(self) -> Path:
        """
        @brief Get the path where the recording will be saved.

        @return Path to the output file or directory.
        """
        pass

    @abstractmethod
    def setup(self) -> None:
        """
        @brief Perform any necessary setup before recording can begin.

        This may include creating directories, generating config files, etc.
        """
        pass

    @abstractmethod
    def start_recording(self) -> None:
        """
        @brief Start the recording process.

        @throws RuntimeError If recording fails to start.
        """
        pass

    @abstractmethod
    def stop_recording(self) -> Dict[str, Any]:
        """
        @brief Stop the ongoing recording.

        @return Path to the recorded output, or None if no recording was in progress.
        """
        pass

    @abstractmethod
    def get_session_info(self) -> Dict[str, Any]:
        """
        @brief Get information about the current recording session.

        @return Dictionary containing session details.
        """
        pass

    @abstractmethod
    def wait_for_completion(self) -> None:
        """
        @brief Wait for the recording to complete.

        This is a blocking call that returns when the recording is logically complete.
        Different recorder implementations may define completion differently.
        """
        pass

    @property
    def is_recording(self) -> bool:
        """
        @brief Check if recording is currently in progress.

        @return True if recording is in progress, False otherwise.
        """
        return self._is_recording

    @property
    def output_file(self) -> Optional[Path]:
        """
        @brief Get the path to the output file if available.

        @return Path to the output file or None if not available.
        """
        return self._output_file
