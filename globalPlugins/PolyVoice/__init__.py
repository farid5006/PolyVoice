# -*- coding: UTF-8 -*-
"""PolyVoice Global Plugin: Register settings panel, menu items, and shortcuts."""

import wx
import globalPluginHandler
import gui
from gui.settingsDialogs import NVDASettingsDialog
from scriptHandler import script
from logHandler import log
import config
from configobj import ConfigObj
import addonHandler

addonHandler.initTranslation()

from .settingsPanel import PolyVoiceSettingsPanel


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """Global plugin component for PolyVoice."""

    def __init__(self):
        super().__init__()
        
        # Inject config schema for PolyVoice settings
        try:
            spec_dict = {
                "PolyVoice": {
                    "enableAutoSwitch": "boolean(default=True)",
                    "bindings": {
                        "__many__": "string(default='')"
                    }
                }
            }
            config.conf.spec.merge(ConfigObj(spec_dict))
        except Exception:
            log.exception("PolyVoice: Failed to merge config spec")
            
        # Register settings panel class in standard NVDA Settings Dialog
        try:
            if PolyVoiceSettingsPanel not in NVDASettingsDialog.categoryClasses:
                NVDASettingsDialog.categoryClasses.append(PolyVoiceSettingsPanel)
                log.info("PolyVoice: Settings panel registered successfully")
        except Exception:
            log.exception("PolyVoice: Failed to register settings panel")

        # Safely add menu item after GUI is ready
        try:
            wx.CallAfter(self._addMenuItem)
        except Exception:
            pass

    def _addMenuItem(self):
        try:
            if hasattr(gui, "mainFrame") and gui.mainFrame and getattr(gui.mainFrame, "sysTrayIcon", None):
                self.prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
                self.polyVoiceMenuItem = self.prefsMenu.Append(
                    wx.ID_ANY,
                    _("PolyVoice Settings..."),
                    _("Open PolyVoice settings and configure language synthesizers")
                )
                gui.mainFrame.sysTrayIcon.Bind(
                    wx.EVT_MENU,
                    self.onOpenPolyVoiceSettings,
                    self.polyVoiceMenuItem
                )
                log.info("PolyVoice: Added menu item to Preferences menu successfully")
        except Exception:
            log.exception("PolyVoice: Failed to add menu item")

    def onOpenPolyVoiceSettings(self, evt):
        """Open standard NVDA Settings Dialog focusing on PolyVoice category."""
        try:
            gui.mainFrame._popupSettingsDialog(
                NVDASettingsDialog, PolyVoiceSettingsPanel
            )
        except Exception:
            log.exception("PolyVoice: Failed to open settings dialog")

    def terminate(self):
        try:
            if PolyVoiceSettingsPanel in NVDASettingsDialog.categoryClasses:
                NVDASettingsDialog.categoryClasses.remove(PolyVoiceSettingsPanel)
        except Exception:
            pass
        try:
            if hasattr(self, "prefsMenu") and hasattr(self, "polyVoiceMenuItem"):
                self.prefsMenu.Remove(self.polyVoiceMenuItem)
        except Exception:
            pass
        super().terminate()

    @script(
        description=_("Open PolyVoice settings"),
        category="PolyVoice",
        gesture="kb:NVDA+ctrl+shift+v",
    )
    def script_openSettings(self, gesture):
        """Opens standard NVDA Settings Dialog and navigates to PolyVoice category."""
        try:
            gui.mainFrame._popupSettingsDialog(
                NVDASettingsDialog, PolyVoiceSettingsPanel
            )
        except Exception:
            log.exception("PolyVoice: Failed to open settings via shortcut")
