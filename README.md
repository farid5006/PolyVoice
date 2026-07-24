# PolyVoice 🎙️

**PolyVoice** is a hybrid virtual synthesizer driver and intelligent language router for the [NVDA screen reader](https://www.nvaccess.org/).

It dynamically detects all speech synthesizers installed on your system and seamlessly switches between them based on the language of the text being read, giving you a smooth, non-overlapping multi-language reading experience.

---

## 🌟 Key Features

* **Pure Router Architecture**: PolyVoice acts strictly as a router. It respects each synthesizer's own settings (speed, pitch, volume, voice variant) as configured in NVDA. It does not force or override your engine settings.
* **Character-Level Language Detection**: Precise Unicode script detection accurately isolates foreign words (e.g. English, French, German) embedded right in the middle of sentences, routing them instantly to the designated synthesizer.
* **Zero Audio Overlap**: Built-in buffer drain delay (150ms) and digital `IndexCommand` tracking prevent speech synthesizers from racing or talking over each other.
* **Dynamic Synthesizer Discovery**: Automatically recognizes all active NVDA speech engines (including IBMTTS, Microsoft SAPI5, Windows OneCore, eSpeak NG, RHVoice, Piper, and Acapela).
* **NVDA 2026 Ready**: Fully compatible with NVDA 2026.1+ (64-bit AMD64 architecture).

---

## ⚙️ Configuration & Setup

1. **Install the Add-on**: Download and install `PolyVoice-1.0.0-beta.nvda-addon` in NVDA.
2. **Configure Language Assignments**:
   * Open **NVDA Menu** ➔ **Preferences** ➔ **Settings...** (or press `NVDA + Control + G`).
   * Select **PolyVoice** from the categories list.
   * Make sure **Enable automatic language switching** is checked.
   * Select a **Language** from the drop-down menu (e.g., *English*).
   * Select your preferred **Synthesizer Engine** for that language.
   * Click **Assign engine to language**.
   * Repeat for any other languages you wish to customize.
   * Click **OK** to save your settings.
3. **Switch to PolyVoice**:
   * Press `NVDA + Control + S` to open the Synthesizer dialog.
   * Select **PolyVoice** and press **Enter**.

---

## 📥 Downloads & Beta Testing

Check out the latest [Beta Release](https://github.com/farid5006/PolyVoice/releases) to download the `.nvda-addon` file and provide feedback!

---

## 👤 Author

Developed with care by **Farid Muhammad**.
