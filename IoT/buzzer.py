from machine import Pin, PWM
from time import sleep_ms

class Note:
    # Note durations as fractions of a whole note
    WHOLE = 1.0
    HALF = 0.5
    QUARTER = 0.25
    EIGHTH = 0.125
    SIXTEENTH = 0.0625
    
    # Play modes
    LEGATO = 1.0    # Play full duration
    STACCATO = 0.7  # Play 70% of duration, 30% silence
    
    def __init__(self, frequency, duration, mode=LEGATO):
        """
        Create a musical note or rest.
        
        :param frequency: Frequency in Hz (0 for a rest)
        :param duration: Duration as a fraction of whole note
        :param mode: LEGATO (full duration) or STACCATO (shortened play)
        """
        self.frequency = frequency
        self.duration = duration  # Keep original duration for timing
        self.mode = mode
    
    @staticmethod
    def rest(duration):
        """Convenience method to create a rest"""
        return Note(0, duration)

class Buzzer:
    # Note frequencies
    
    # 3rd Octave frequencies
    C3 = 131
    C3_SHARP = D3_FLAT = 139
    D3 = 147
    D3_SHARP = E3_FLAT = 156
    E3 = 165
    F3 = 175
    F3_SHARP = G3_FLAT = 185
    G3 = 196
    G3_SHARP = A3_FLAT = 208
    A3 = 220
    A3_SHARP = B3_FLAT = 233
    B3 = 247
    
    # 4th octave
    C4 = 262
    C4_SHARP = D4_FLAT = 277
    D4 = 294
    D4_SHARP = E4_FLAT = 311
    E4 = 330
    F4 = 349
    F4_SHARP = G4_FLAT = 370
    G4 = 392
    G4_SHARP = A4_FLAT = 415
    A4 = 440
    A4_SHARP = B4_FLAT = 466
    B4 = 494
    
    # 5th octave
    C5 = 523
    C5_SHARP = D5_FLAT = 554
    D5 = 587
    D5_SHARP = E5_FLAT = 622
    E5 = 659
    F5 = 698
    F5_SHARP = G5_FLAT = 740
    G5 = 784
    G5_SHARP = A5_FLAT = 831
    A5 = 880
    A5_SHARP = B5_FLAT = 932
    B5 = 988
    
    # Aliases for convenience
    C3s = C3_SHARP
    Db3 = D3_FLAT
    D3s = D3_SHARP
    Eb3 = E3_FLAT
    F3s = F3_SHARP
    Gb3 = G3_FLAT
    G3s = G3_SHARP
    Ab3 = A3_FLAT
    A3s = A3_SHARP
    Bb3 = B3_FLAT
    
    C4s = C4_SHARP
    Db4 = D4_FLAT
    D4s = D4_SHARP
    Eb4 = E4_FLAT
    F4s = F4_SHARP
    Gb4 = G4_FLAT
    G4s = G4_SHARP
    Ab4 = A4_FLAT
    A4s = A4_SHARP
    Bb4 = B4_FLAT
    
    C5s = C5_SHARP
    Db5 = D5_FLAT
    D5s = D5_SHARP
    Eb5 = E5_FLAT
    F5s = F5_SHARP
    Gb5 = G5_FLAT
    G5s = G5_SHARP
    Ab5 = A5_FLAT
    A5s = A5_SHARP
    Bb5 = B5_FLAT
    
    def __init__(self, pin_num):
        self.pin = PWM(Pin(pin_num))
        self.tune = []
        self.set_tempo(120)  # Initialize with default tempo
    
    def set_tune(self, tune):
        self.tune = tune
    
    def set_tempo(self, tempo=120):
        """
        Set tempo in BPM (beats per minute)
        Whole note duration = (60,000 ms/min) / (tempo beats/min) = ms/beat
        """
        self.tempo = tempo
        self.whole_note_duration = 60000 / tempo * 4
    
    def play_tone(self, frequency, total_duration, mode=Note.LEGATO):
        """
        Play a tone with proper staccato/legato handling
        """
        if frequency > 0:
            # Calculate actual play time based on mode
            play_time = int(total_duration * mode)
            silence_time = total_duration - play_time
            
            # Play the note
            self.pin.freq(frequency)
            self.pin.duty(512)
            sleep_ms(play_time)
            self.pin.duty(0)
            
            # Add silence if in staccato mode
            if silence_time > 0:
                sleep_ms(silence_time)
        else:
            # Rest - full duration silence
            sleep_ms(total_duration)
    
    def play_tune(self):
        if not self.tune:
            return
        
        for note in self.tune:
            note_duration = int(self.whole_note_duration * note.duration)
            self.play_tone(note.frequency, note_duration, note.mode)
    
    def stop(self):
        self.pin.duty(0)
    
    def deinit(self):
        self.stop()
        self.pin.deinit()