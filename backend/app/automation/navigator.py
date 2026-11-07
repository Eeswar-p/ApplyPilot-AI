import time
from typing import Dict, Any, Optional
from playwright.sync_api import Page, TimeoutError

class JobNavigator:
    """Handles platform navigation, dismisses cookie/consent dialogs, and detects application forms."""

    def __init__(self, page: Page):
        self.page = page

    def navigate_safely(self, url: str, timeout_ms: int = 15000) -> bool:
        """Navigate to URL with fallback strategies."""
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            self.dismiss_overlays()
            return True
        except TimeoutError:
            try:
                self.page.goto(url, wait_until="commit", timeout=timeout_ms)
                return True
            except Exception:
                return False
        except Exception:
            return False

    def dismiss_overlays(self):
        """Dismiss common cookie banners, login walls, and marketing dialogs."""
        dismiss_selectors = [
            "button:has-text('Accept')",
            "button:has-text('I Agree')",
            "button:has-text('Allow all')",
            "button:has-text('Accept all cookies')",
            "button:has-text('Dismiss')",
            "button:has-text('Got it')",
            "button[aria-label='Dismiss']",
            "button[aria-label='Close']",
            ".artdeco-modal__dismiss",
            "[data-test-modal-close-btn]",
        ]

        for selector in dismiss_selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=500):
                    locator.click(timeout=1000)
                    time.sleep(0.3)
                    break
            except Exception:
                continue

    def detect_application_entry(self) -> Dict[str, Any]:
        """Detect whether the page has an inline form, an Easy Apply button, or an external redirect button."""
        # 1. Check for Easy Apply buttons
        easy_apply_selectors = [
            "button.jobs-apply-button",
            "button:has-text('Easy Apply')",
            "button:has-text('Quick Apply')",
            "button:has-text('Apply Now')",
            "a:has-text('Apply Now')",
        ]

        for selector in easy_apply_selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=800):
                    text = locator.inner_text().strip()
                    is_easy = "easy" in text.lower() or "quick" in text.lower()
                    return {
                        "type": "easy_apply" if is_easy else "apply_button",
                        "selector": selector,
                        "button_text": text,
                        "requires_click": True,
                    }
            except Exception:
                continue

        # 2. Check for inline form
        form_elements = self.page.locator("form")
        if form_elements.count() > 0:
            inputs = self.page.locator("form input:not([type='hidden'])")
            if inputs.count() >= 2:
                return {
                    "type": "inline_form",
                    "selector": "form",
                    "requires_click": False,
                }

        return {
            "type": "external_or_unsupported",
            "selector": None,
            "requires_click": False,
        }

    def open_application_modal(self) -> bool:
        """Click apply button to open application dialog or multi-step modal."""
        entry = self.detect_application_entry()
        if entry["requires_click"] and entry["selector"]:
            try:
                self.page.locator(entry["selector"]).first.click(timeout=3000)
                time.sleep(1)
                self.dismiss_overlays()
                return True
            except Exception:
                return False
        return entry["type"] == "inline_form"
