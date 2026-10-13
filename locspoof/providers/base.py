"""
Abstract Base Provider interface for locspoof.
All spoofing and location probing mechanisms must implement this contract.
"""

from abc import ABC, abstractmethod
from typing import Optional

from locspoof.core.models import Location, LocationSignal, OperationResult, ProviderCapability


class BaseProvider(ABC):
    """
    Abstract interface for all locspoof location providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the provider (e.g. 'android', 'browser', 'network')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short human-readable description of what this provider targets."""
        pass

    @abstractmethod
    def check_capability(self) -> ProviderCapability:
        """
        Check if the current host/environment satisfies all requirements
        to operate this provider (e.g. adb installed, emulator running, browser available).
        """
        pass

    @abstractmethod
    def apply_location(self, location: Location) -> OperationResult:
        """
        Apply simulated coordinates to the target environment.
        """
        pass

    @abstractmethod
    def get_current_signal(self) -> LocationSignal:
        """
        Read or probe current active location signal from the target environment.
        """
        pass

    @abstractmethod
    def reset(self) -> OperationResult:
        """
        Clear or reset simulated location back to default.
        """
        pass
