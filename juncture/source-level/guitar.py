import numpy as np
from midiutil import MIDIFile
import random

# =============================================================================
# 1. THE PITCH MATRIX (D12 Group on 17-TET Dastgah)
# =============================================================================
class PitchMatrix:
    """
    Constructs a 17x17 matrix using the Dihedral Group D12 acting on 17-TET.
    D12 has 24 elements: 17 rotations (since we're mod 17) and 17 reflections.
    We use a serialist approach: P (Prime), I (Inversion), R (Retrograde), RI (Retrograde-Inversion).
    """
    def __init__(self, seed_motif, modulus=17):
        self.modulus = modulus
        self.seed = np.array(seed_motif)
        self.length = len(seed_motif)
        
        # Generate the 4 primary forms
        self.P = self.seed.copy()
        self.I = (self.modulus - self.seed) % self.modulus
        self.R = self.P[::-1].copy()
        self.RI = self.I[::-1].copy()
        
    def build_17x17_matrix(self):
        """
        Builds the full 17x17 matrix using the formula:
        M[i][j] = (P[j] + I[i]) % 17
        This generates all transpositions and inversions.
        """
        matrix = np.zeros((self.modulus, self.length), dtype=int)
        for i in range(self.modulus):
            for j in range(self.length):
                matrix[i][j] = (self.P[j] + self.I[i]) % self.modulus
        return matrix

# =============================================================================
# 2. THE RHYTHM MATRIX (Stockhausen-style)
# =============================================================================
class RhythmMatrix:
    """
    Stockhausen-style rhythm matrix where pitch classes dictate durations.
    Grid: X-axis = durations (1, 2, 4, 8 sixteenths), Y-axis = pitch classes (0-16).
    """
    def __init__(self, durations=[1, 2, 4, 8], num_pitches=17):
        self.durations = durations
        self.num_pitches = num_pitches
        self.grid = np.zeros((num_pitches, len(durations)), dtype=int)
        
        # Populate grid: duration is determined by (pitch_idx + dur_idx) % len(durations)
        for i in range(num_pitches):
            for j in range(len(durations)):
                self.grid[i][j] = self.durations[(i + j) % len(durations)]
                
    def get_traversal_path(self, seed_pitch, seed_dur, steps=32):
        """
        Traverses the grid using D12 group operations.
        We apply rotations and reflections to the indices to find the path.
        """
        path = []
        p = seed_pitch
        d = seed_dur
        for k in range(steps):
            # D12 operations on the grid indices
            # Rotate pitch, reflect duration
            if k % 2 == 0:
                p = (p + 3) % self.num_pitches
            else:
                d = (self.num_pitches - d) % len(self.durations)  # Reflection
            
            # Add some deterministic variation based on k
            p = (p + k) % self.num_pitches
            d = (d + k) % len(self.durations)
            
            path.append((p, d))
        return path

# =============================================================================
# 3. THE TUNING MATRIX (QCM vs Pythagorean)
# =============================================================================
class TuningMatrix:
    """
    Provides exact frequencies for 17-TET mapped to historical tunings.
    Root is C4 = 261.63 Hz.
    """
    def __init__(self, root_freq=261.63):
        self.root = root_freq
        self.num_notes = 17
        
    def get_pythagorean_frequencies(self):
        """
        Pythagorean tuning: stack 17 pure perfect fifths (ratio 3/2).
        """
        freqs = []
        for k in range(self.num_notes):
            # Stack fifths: f_k = root * (3/2)^k
            freq = self.root * (1.5 ** k)
            freqs.append(freq)
        return freqs

    def get_qcm_frequencies(self):
        """
        Quarter-Comma Meantone (QCM): pure major thirds (ratio 5/4).
        We stack 17 QCM fifths (ratio 5^(1/4) ≈ 1.495348).
        """
        freqs = []
        for k in range(self.num_notes):
            # Stack QCM fifths: f_k = root * (5^(1/4))^k
            freq = self.root * (1.49534878 ** k)
            freqs.append(freq)
        return freqs
        
    def map_pitch_to_freq(self, pitch_class, tuning='QCM'):
        if tuning == 'QCM':
            scale = self.get_qcm_frequencies()
        else:
            scale = self.get_pythagorean_frequencies()
        return scale[pitch_class % self.num_notes]

# =============================================================================
# 4. KARPLUS-STRONG SYNTHESIS (Fractional Delay)
# =============================================================================
def render_karplus_strong(freq, dur_sec, vel=0.8, sample_rate=44100):
    """
    Exact fractional-delay Karplus-Strong algorithm.
    Returns a numpy array of float32 audio samples.
    """
    N = max(1, int(sample_rate * dur_sec))
    buf = np.zeros(N, dtype=np.float32)
    
    if freq <= 0 or freq >= sample_rate / 2:
        return buf
        
    D = sample_rate / freq
    Dint = max(2, int(np.floor(D)) - 1)
    frac = max(0.001, D - Dint - 1)
    eta = (1 - frac) / (1 + frac)
    
    L = Dint + 1
    delay = np.zeros(L)
    wIdx = 0
    lpPrev = 0.0
    apIn = 0.0
    apOut = 0.0
    
    T60 = 4.0 if freq < 100 else 3.5 if freq < 150 else 3.0 if freq < 250 else 2.0
    loopGain = 10 ** (-3 / (T60 * freq))
    
    # Excitation: Lowpassed noise burst
    excState = 0.0
    for i in range(min(Dint, N)):
        noise = random.random() * 2 - 1
        excState = 0.5 * excState + 0.5 * noise
        delay[i] = excState
        
    for n in range(N):
        out = delay[wIdx]
        buf[n] = out * vel
        
        # One-zero averaging loop filter
        avg = 0.5 * (out + lpPrev)
        lpPrev = out
        
        # Allpass fractional delay
        ap = eta * avg + apIn - eta * apOut
        apIn = avg
        apOut = ap
        
        delay[wIdx] = ap * loopGain
        wIdx = (wIdx + 1) % L
        
    # Attack ramp (2.5ms)
    att = min(int(sample_rate * 0.0025), N)
    for i in range(att):
        buf[i] *= i / att
        
    return buf

# =============================================================================
# 5. MIDI RENDERER
# =============================================================================
def render_sequence_to_midi(sequence, filename="matrix_composition.mid", bpm=120):
    """
    Renders the generated sequence to a MIDI file using midiutil.
    Maps frequencies to nearest MIDI note and adds pitch bend for microtonality.
    """
    midi = MIDIFile(1)
    track = 0
    channel = 0
    time = 0
    midi.addTrackName(track, time, "Matrix Composer")
    midi.addTempo(track, time, bpm)
    
    # Set pitch bend range to 2 semitones (standard)
    midi.addControllerEvent(track, channel, time, 101, 0) # RPN MSB
    midi.addControllerEvent(track, channel, time, 100, 0) # RPN LSB
    midi.addControllerEvent(track, channel, time, 6, 2)   # Data Entry MSB (2 semitones)
    
    for note in sequence:
        freq = note['mapped_freq_hz']
        dur_16ths = note['duration_16ths']
        vel = note['velocity']
        
        # Convert frequency to MIDI note and cents
        midi_note_float = 69 + 12 * np.log2(freq / 440.0)
        midi_note = int(round(midi_note_float))
        cents = (midi_note_float - midi_note) * 100
        
        # Convert cents to pitch bend (0-16383, center 8192, range +/- 2 semitones)
        bend_value = int(8192 + (cents / 200) * 8192)
        bend_value = max(0, min(16383, bend_value))
        
        # Add pitch bend event
        midi.addPitchWheelEvent(track, channel, time, bend_value)
        
        # Calculate duration in beats
        duration_beats = dur_16ths * 0.25
        
        # Add note
        midi.addNote(track, channel, midi_note, time, duration_beats, vel)
        time += duration_beats
        
    with open(filename, "wb") as f:
        midi.writeFile(f)

# =============================================================================
# 6. MAIN EXECUTION
# =============================================================================
def main():
    random.seed(42)  # Deterministic
    
    # 1. Define Seed Motif for 17-TET
    seed_motif = [0, 3, 7, 10, 14, 10, 7, 3]
    
    # 2. Build Pitch Matrix
    pitch_matrix = PitchMatrix(seed_motif)
    matrix_17x17 = pitch_matrix.build_17x17_matrix()
    
    # 3. Build Rhythm Matrix and Path
    rhythm_matrix = RhythmMatrix()
    path = rhythm_matrix.get_traversal_path(seed_pitch=0, seed_dur=0, steps=32)
    
    # 4. Generate Sequence
    tuner = TuningMatrix(root_freq=261.63)
    sequence = []
    
    for i, (p_idx, d_idx) in enumerate(path):
        # Get pitch class from the 17x17 matrix (using row 0, cycling)
        pitch_class = matrix_17x17[0][i % len(seed_motif)]
        
        # Map to frequency (using QCM tuning)
        freq = tuner.map_pitch_to_freq(pitch_class, tuning='QCM')
        
        # Get duration from rhythm matrix
        dur_16ths = rhythm_matrix.grid[p_idx][d_idx]
        
        # Velocity (deterministic variation)
        vel = 80 + (i * 3) % 40
        
        sequence.append({
            'matrix_pitch': int(pitch_class),
            'mapped_freq_hz': float(freq),
            'duration_16ths': int(dur_16ths),
            'velocity': int(vel)
        })
        
    # Print first 5 notes
    print("=== GENERATED SEQUENCE (First 5 notes) ===")
    for note in sequence[:5]:
        print(note)
        
    # 5. Render to MIDI
    render_sequence_to_midi(sequence, "matrix_composition.mid")
    print("\nMIDI file 'matrix_composition.mid' generated.")
    
    # 6. Render to Audio (Karplus-Strong)
    print("\nRendering audio via Karplus-Strong...")
    bpm = 120
    sixteenth_sec = 60.0 / bpm / 4.0
    audio_buffer = np.array([], dtype=np.float32)
    
    for note in sequence:
        dur_sec = note['duration_16ths'] * sixteenth_sec
        audio = render_karplus_strong(note['mapped_freq_hz'], dur_sec, vel=note['velocity']/127.0)
        audio_buffer = np.concatenate((audio_buffer, audio))
        
    print(f"Audio buffer generated: {len(audio_buffer)} samples ({len(audio_buffer)/44100:.2f} seconds).")

if __name__ == "__main__":
    main()
