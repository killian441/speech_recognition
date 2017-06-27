from nio import Signal
from nio.block.base import Block
from nio.util.discovery import discoverable
from nio.properties import VersionProperty, StringProperty
from nio.util.threading import spawn
from threading import Event

import speech_recognition as sr


@discoverable
class SpeechRecognition(Block):
    attr_name = StringProperty(default='audio_text', title='Simulated Attribute')
    version = VersionProperty('0.1.0')

    def __init__(self):
        super().__init__()
        self._stop_event = Event()
        self.r = sr.Recognizer()

    def start(self):
        super().start()
        self.counter = 0
        self._stop_event.clear()
        spawn(self.run)

    def run(self):

        while not self._stop_event.is_set():
            with sr.Microphone() as source:
                audio = self.r.listen(source)

            try:
                self.audio_text = self.r.recognize_sphinx(audio)
                print("Sphinx thinks you said " + self.audio_text)
            except sr.UnknownValueError:
                self.audio_text = None
                print("Sphinx could not understand audio")
            except sr.RequestError as e:
                self.audio_text = None
                print("Sphinx error; {0}".format(e))

            if self.audio_text:
                sig = {self.attr_name():self.audio_text}
                self.notify_signals([Signal(sig)])

    def stop(self):
        """ Stop the simulator thread. """
        self._stop_event.set()
        super().stop()