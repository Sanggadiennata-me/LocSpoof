"""
Provider Manager and Registry for locspoof.
Coordinates and dispatches location changes to modular providers.
"""

from typing import Dict, List, Optional

from locspoof.core.exceptions import ProviderError
from locspoof.core.models import (
    Location,
    LocationSignal,
    OperationResult,
    ProviderCapability,
)
from locspoof.providers.android.provider import AndroidProvider
from locspoof.providers.base import BaseProvider
from locspoof.providers.browser.provider import BrowserProvider
from locspoof.providers.network.provider import NetworkProvider


class ProviderManager:
    """
    Central registry and dispatcher for all location providers.
    """

    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        # Register standard default providers
        self.register_provider(AndroidProvider())
        self.register_provider(BrowserProvider())
        self.register_provider(NetworkProvider())

    def register_provider(self, provider: BaseProvider) -> None:
        self._providers[provider.name.lower()] = provider

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        return self._providers.get(name.lower())

    def list_providers(self) -> List[BaseProvider]:
        return list(self._providers.values())

    def get_all_capabilities(self) -> List[ProviderCapability]:
        return [p.check_capability() for p in self._providers.values()]

    def apply_to_all(self, location: Location) -> Dict[str, OperationResult]:
        """Apply location to all registered providers."""
        results = {}
        for name, provider in self._providers.items():
            try:
                results[name] = provider.apply_location(location)
            except Exception as exc:
                results[name] = OperationResult(
                    success=False,
                    message=f"Provider {name} failed: {exc}",
                    error=str(exc),
                )
        return results

    def collect_all_signals(self) -> List[LocationSignal]:
        """Collect current location signals from all providers."""
        signals = []
        for provider in self._providers.values():
            try:
                sig = provider.get_current_signal()
                signals.append(sig)
            except Exception as exc:
                signals.append(
                    LocationSignal(
                        source=provider.name,  # type: ignore
                        source_name=provider.name.title(),
                        is_active=False,
                        error_message=str(exc),
                    )
                )
        return signals

    def reset_all(self) -> Dict[str, OperationResult]:
        results = {}
        for name, provider in self._providers.items():
            results[name] = provider.reset()
        return results
