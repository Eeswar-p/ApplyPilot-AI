import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page
from flask import current_app

DEFAULT_CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

class BrowserManager:
    """Manages Playwright browser instances, persistent user data directories, and safe profile-lock recovery."""

    def __init__(self, headless: Optional[bool] = None, user_data_dir: Optional[str] = None):
        if headless is None:
            headless_env = os.getenv("AUTOMATION_HEADLESS", "true").lower()
            self.headless = headless_env in ("true", "1", "yes")
        else:
            self.headless = headless

        self.user_data_dir = user_data_dir
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._temp_dir: Optional[str] = None

    def _resolve_executable_path(self) -> Optional[str]:
        """Locate Google Chrome or return None to let Playwright use its bundled browser."""
        if os.path.exists(DEFAULT_CHROME_PATH):
            return DEFAULT_CHROME_PATH
        return None

    def _is_profile_locked(self, profile_dir: Path) -> bool:
        """Check if profile directory has active Chrome locks (SingletonLock, lockfile)."""
        lock_files = ["SingletonLock", "lockfile", "parent.lock"]
        for lock in lock_files:
            target = profile_dir / lock
            if target.exists():
                return True
        return False

    def start(self) -> BrowserContext:
        """Initialize Playwright and launch browser context with lock recovery."""
        self.playwright = sync_playwright().start()
        chrome_exe = self._resolve_executable_path()

        launch_args = [
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-extensions",
        ]

        # Handle persistent user data directory and profile locking
        if self.user_data_dir:
            profile_path = Path(self.user_data_dir)
            if self._is_profile_locked(profile_path):
                # Fallback to an isolated cloned session to prevent lock conflict crashes
                self._temp_dir = tempfile.mkdtemp(prefix="applypilot_browser_")
                context_dir = self._temp_dir
            else:
                context_dir = str(profile_path)

            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=context_dir,
                executable_path=chrome_exe,
                headless=self.headless,
                args=launch_args,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            )
        else:
            launch_kwargs = {
                "headless": self.headless,
                "args": launch_args,
            }
            if chrome_exe:
                launch_kwargs["executable_path"] = chrome_exe

            self.browser = self.playwright.chromium.launch(**launch_kwargs)
            self.context = self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            )

        return self.context

    def new_page(self) -> Page:
        """Create a new page in the active context."""
        if not self.context:
            self.start()
        return self.context.new_page()

    def close(self):
        """Safely close context, browser, and playwright instance."""
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass

        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass

        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir, ignore_errors=True)
            except Exception:
                pass

        self.context = None
        self.browser = None
        self.playwright = None
        self._temp_dir = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
