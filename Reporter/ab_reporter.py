from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class AbstractReporter(ABC):
    """
    @brief Abstract base class for all reporters.

    Defines the common interface that all reporter classes must implement.
    """

    @abstractmethod
    def print_session_start(self, session_info: Dict[str, Any]) -> None:
        """
        @brief Print information about the starting session.

        @param session_info Dictionary containing session details.
        """
        pass

    @abstractmethod
    def print_recording_start(self) -> None:
        """
        @brief Print information about the recording start.
        """
        pass

    @abstractmethod
    def print_recorder_results(self, results: Dict[str, Any]) -> None:
        """
        @brief Print recording results.

        @param results Dictionary containing recording outputs and metadata.
        """
        pass

    @abstractmethod
    def print_recording_end(self) -> None:
        """
        @brief Print information about the recording end.
        """
        pass
