"""
NeuroTrade Voice Output Module
Uses pyttsx3 for offline text-to-speech.
"""
import sys
import threading

try:
    import pyttsx3
    _TTS_AVAILABLE = True
except ImportError:
    _TTS_AVAILABLE = False
    print('[Voice] pyttsx3 not installed. Run: pip install pyttsx3')


ACTION_MESSAGES = {
    'BUY': 'BUY signal for {stock} at rupees {price}. Confidence {confidence} percent.',
    'SELL': 'SELL signal for {stock} at rupees {price}. Confidence {confidence} percent.',
    'HOLD': '{stock} — HOLD. No action required.',
}


class TradeSpeaker:
    """
    Thread-safe text-to-speech announcer for trading signals.
    """

    def __init__(self, rate: int = 175, volume: float = 0.9, announce_hold: bool = False):
        """
        Args:
            rate: Speech rate (words per minute). Default 175.
            volume: Volume 0.0 to 1.0. Default 0.9.
            announce_hold: If False, HOLD signals are not spoken aloud.
        """
        self.rate = rate
        self.volume = volume
        self.announce_hold = announce_hold
        self.enabled = _TTS_AVAILABLE
        self._lock = threading.Lock()
        self._engine = None

        if self.enabled:
            self._init_engine()

    def _init_engine(self):
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', self.rate)
            self._engine.setProperty('volume', self.volume)
        except Exception as e:
            print(f'[Voice] Engine init failed: {e}')
            self.enabled = False

    def _speak_sync(self, text: str):
        """Speak in the current thread (blocking)."""
        if not self.enabled or not self._engine:
            return
        try:
            with self._lock:
                self._engine.say(text)
                self._engine.runAndWait()
        except Exception as e:
            print(f'[Voice] Speech error: {e}')

    def speak(self, text: str, blocking: bool = False):
        """Speak text. Non-blocking by default (runs in thread)."""
        if not self.enabled:
            return
        if blocking:
            self._speak_sync(text)
        else:
            t = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
            t.start()

    def speak_signal(self, stock: str, action: str, price: float, confidence: float):
        """
        Announce a trading signal.

        Args:
            stock: Stock symbol e.g. 'RELIANCE'
            action: 'BUY', 'SELL', or 'HOLD'
            price: Current price
            confidence: Confidence 0.0 to 1.0
        """
        if action == 'HOLD' and not self.announce_hold:
            return

        template = ACTION_MESSAGES.get(action, '{stock} — {action}')
        text = template.format(
            stock=stock,
            price=f'{price:,.0f}',
            confidence=f'{confidence * 100:.0f}',
            action=action
        )
        print(f'[Voice] Speaking: {text}')
        self.speak(text)

    def speak_alert(self, message: str):
        """Speak an arbitrary alert message."""
        print(f'[Voice] Alert: {message}')
        self.speak(message)

    def set_enabled(self, enabled: bool):
        """Enable or disable voice output at runtime."""
        self.enabled = enabled and _TTS_AVAILABLE


# Module-level singleton
_speaker_instance = None


def get_speaker(announce_hold: bool = False) -> TradeSpeaker:
    global _speaker_instance
    if _speaker_instance is None:
        _speaker_instance = TradeSpeaker(announce_hold=announce_hold)
    return _speaker_instance
