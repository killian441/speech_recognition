from enum import Enum
from nio import Signal
from nio.block.base import Block
from nio.util.discovery import discoverable
from nio.properties import VersionProperty, StringProperty, SelectProperty
from nio.util.threading import spawn
from threading import Event

import speech_recognition as sr

class Platform(Enum):
    LocalMachineSphinx = 0
    GoogleSpeech = 1
    WitAI = 2


@discoverable
class SpeechRecognition(Block):
    platform = SelectProperty(Platform,
                              title='Platform',
                              default=Platform.LocalMachineSphinx)
    key = StringProperty(title='Key', default='')
    attr_name = StringProperty(default='audio_text', title='Output Signal Name')
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
            if platform() == Platform.LocalMachineSphinx:
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
            elif platform() == Platform.GoogleSpeech:
                try:
                    # for testing purposes, we're just using the default API key
                    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                    # instead of `r.recognize_google(audio)`
                    self.audio_text = self.r.recognize_google(audio,key=self.key() if self.key() is not '' else None)
                    print("Google Speech Recognition thinks you said " + self.audio_text)
                except sr.UnknownValueError:
                    self.audio_text = None
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    self.audio_text = None
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
            elif platform() == Platform.WitAI:
                try:
                    self.audio_text = self.r.recognize_wit(audio,key=self.key())
                    print("Wit.ai thinks you said " + self.audio_text)
                except sr.UnknownValueError:
                    self.audio_text = None
                    print("Wit.ai could not understand audio")
                except sr.RequestError as e:
                    self.audio_text = None
                    print("Could not request results from Wit.ai service; {0}".format(e))

            if self.audio_text:
                sig = {self.attr_name():self.audio_text}
                self.notify_signals([Signal(sig)])

    def stop(self):
        """ Stop the simulator thread. """
        self._stop_event.set()
        super().stop()