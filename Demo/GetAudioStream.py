import sounddevice as sd
import pretty_errors
pretty_errors.activate()


# really? violation of PEP8?
sd.default.samplerate = 48000
# sd.default.device = 'di'


duration = 10.5
my_rec = sd.rec(int(duration * sd.default.samplerate), channels=2)
sd.wait()
