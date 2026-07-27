# -*- coding: UTF-8 -*-
"""PolyVoice Settings Panel — Internationalized for NVDA 2026."""

import wx
import config
import gui
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel
from logHandler import log
import addonHandler

addonHandler.initTranslation()

WORLD_LANGUAGES = [
    ("ar", _("Arabic")),
    ("en", _("English")),
    ("fr", _("French")),
    ("es", _("Spanish")),
    ("de", _("German")),
    ("it", _("Italian")),
    ("tr", _("Turkish")),
    ("ru", _("Russian")),
    ("fa", _("Persian")),
    ("ur", _("Urdu")),
    ("zh", _("Chinese")),
    ("ja", _("Japanese")),
]


def _ensureConfig():
    if "PolyVoice" not in config.conf:
        config.conf["PolyVoice"] = {}
    if "bindings" not in config.conf["PolyVoice"]:
        config.conf["PolyVoice"]["bindings"] = {}
    if "enableAutoSwitch" not in config.conf["PolyVoice"]:
        config.conf["PolyVoice"]["enableAutoSwitch"] = True
    if "switchDelay" not in config.conf["PolyVoice"]:
        config.conf["PolyVoice"]["switchDelay"] = 50


class PolyVoiceSettingsPanel(SettingsPanel):
    title = "PolyVoice"

    def makeSettings(self, settingsSizer):
        _ensureConfig()
        sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

        # 1. Enable automatic switching
        self.autoSwitchCheckBox = sHelper.addItem(
            wx.CheckBox(self, label=_("Enable automatic language switching"))
        )
        try:
            self.autoSwitchCheckBox.Value = bool(
                config.conf["PolyVoice"].get("enableAutoSwitch", True)
            )
        except Exception:
            self.autoSwitchCheckBox.Value = True

        # 1.5 Switch Delay SpinCtrl
        self.switchDelaySpin = sHelper.addLabeledControl(
            _("Delay when switching synthesizers (in milliseconds):"),
            wx.SpinCtrl,
            min=0,
            max=1000
        )
        try:
            self.switchDelaySpin.Value = int(config.conf["PolyVoice"].get("switchDelay", 50))
        except Exception:
            self.switchDelaySpin.Value = 50

        # 2. Fetch installed engines
        try:
            import synthDriverHandler
            engines = [
                (name, desc or name)
                for name, desc in synthDriverHandler.getSynthList()
                if name.lower() != "polyvoice"
            ]
        except Exception:
            engines = [("sapi5", "Microsoft Speech API 5")]

        self._installedEngines = engines
        engineLabels = [
            "%s (%s)" % (desc, name) if desc != name else name
            for name, desc in self._installedEngines
        ]
        self._engineKeys = [name for name, _ in self._installedEngines]

        langLabels = [label for _, label in WORLD_LANGUAGES]
        self._langKeys = [code for code, _ in WORLD_LANGUAGES]

        # 3. Select language
        self.langChoice = sHelper.addLabeledControl(
            _("Select language:"),
            wx.Choice,
            choices=langLabels
        )
        if langLabels:
            self.langChoice.SetSelection(0)

        # 4. Select synthesizer engine
        self.engineChoice = sHelper.addLabeledControl(
            _("Select synthesizer engine for this language:"),
            wx.Choice,
            choices=engineLabels
        )
        if engineLabels:
            self.engineChoice.SetSelection(0)

        # 5. Assign button
        self.assignBtn = sHelper.addItem(
            wx.Button(self, label=_("Assign engine to language"))
        )
        self.assignBtn.Bind(wx.EVT_BUTTON, self._onAssignBinding)

        # 6. Current assignments list
        self.bindingsListBox = sHelper.addLabeledControl(
            _("Current language assignments:"),
            wx.ListBox,
            choices=[],
            style=wx.LB_SINGLE
        )
        self.bindingsListBox.SetMinSize((350, 120))

        # 7. Remove button
        self.removeBtn = sHelper.addItem(
            wx.Button(self, label=_("Remove assignment"))
        )
        self.removeBtn.Bind(wx.EVT_BUTTON, self._onRemoveBinding)

        self._tempBindings = {}
        self._loadTempBindings()
        self._updateBindingsList()

    def _loadTempBindings(self):
        try:
            rawBindings = config.conf["PolyVoice"]["bindings"]
            for lang, engine in rawBindings.items():
                if engine:
                    self._tempBindings[lang] = str(engine).split("|")[0]
        except Exception:
            pass

    def _updateBindingsList(self):
        self.bindingsListBox.Clear()
        self._listBindingKeys = []
        langDict = dict(WORLD_LANGUAGES)
        engineDict = dict(self._installedEngines)

        for langCode, engineName in self._tempBindings.items():
            langName = langDict.get(langCode, langCode)
            engineDesc = engineDict.get(engineName, engineName)
            displayStr = "%s ➔ %s (%s)" % (langName, engineDesc, engineName)
            self.bindingsListBox.Append(displayStr)
            self._listBindingKeys.append(langCode)

    def _onAssignBinding(self, evt):
        langIdx = self.langChoice.GetSelection()
        engineIdx = self.engineChoice.GetSelection()

        if 0 <= langIdx < len(self._langKeys) and 0 <= engineIdx < len(self._engineKeys):
            langCode = self._langKeys[langIdx]
            engineName = self._engineKeys[engineIdx]
            self._tempBindings[langCode] = engineName
            self._updateBindingsList()
            try:
                gui.messageBox(
                    _("Assigned engine (%s) to language (%s).\nClick OK in the settings dialog to save your changes.")
                    % (engineName, self._langKeys[langIdx]),
                    _("Assignment Added"),
                    wx.OK | wx.ICON_INFORMATION,
                    self
                )
            except Exception:
                pass

    def _onRemoveBinding(self, evt):
        sel = self.bindingsListBox.GetSelection()
        if 0 <= sel < len(self._listBindingKeys):
            langCode = self._listBindingKeys[sel]
            self._tempBindings.pop(langCode, None)
            self._updateBindingsList()

    def onSave(self):
        _ensureConfig()
        config.conf["PolyVoice"]["enableAutoSwitch"] = self.autoSwitchCheckBox.Value
        config.conf["PolyVoice"]["switchDelay"] = self.switchDelaySpin.Value
        
        config.conf["PolyVoice"]["bindings"] = dict(self._tempBindings)
        
        try:
            config.conf.save()
            log.info("PolyVoice: Language bindings saved successfully")
        except Exception:
            log.exception("PolyVoice: Failed to save settings")

        try:
            import synthDriverHandler
            synth = synthDriverHandler.getSynth()
            if synth and getattr(synth, "name", "").lower() == "polyvoice":
                synth._voiceManager.reloadBindings()
        except Exception:
            pass
