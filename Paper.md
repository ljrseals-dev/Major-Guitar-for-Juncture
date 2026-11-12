MajorGuitar: A Physics-Grounded Browser Guitar Synthesizer (Revised)

A technical report on architecture, DSP, and the retirement of celebrity branding

Revision note: §6 has been corrected following review. The earlier draft claimed the files "contained no Williams-derived information." That was wrong. The accurate statement is below: the naming, motivation, and conceptual framing were Williams-derived throughout; the runtime DSP computed nothing from her serve physics. The distinction matters and the paper now states it precisely.

---

Abstract

MajorGuitar is a single-file browser instrument that synthesizes guitar tones using Karplus-Strong physical modeling, exports Standard MIDI Files with verified note correctness, and derives its original design parameters from published tennis-serve biomechanics. This paper documents the system architecture, the DSP implementation, the corrections applied to earlier prototypes, and the decision to retire the "Venus Williams Edition" branding in favor of a physics-first identity. The instrument is evaluated against three criteria — tuning accuracy, MIDI correctness, and tonal target — and all three are shown to pass.

---

1. Introduction

MajorGuitar began as a conceptual exercise: could the physics of a professional tennis serve be mapped onto the excitation of a plucked string? The original prototypes (2024–2025) used Venus Williams' 129 mph serve record as a velocity input to a guitar synthesizer, with the racket's string bed modeled as the vibrating element.

That framing produced a real intellectual lineage and a working instrument. It also produced a branding problem: the celebrity name became the identity, rather than the physics. This paper documents the technical state of the instrument and the pivot away from that branding.

The claim here is narrow. The instrument plays in tune, exports correct MIDI, and produces a coherent Fender-clean target. It does not sound indistinguishable from a real guitar. It sounds like a good physical model, which is a different and honest thing.

---

2. Background

2.1 Karplus-Strong physical modeling

The Karplus-Strong algorithm (Karplus & Strong, 1983) synthesizes a plucked string by circulating an excitation burst through a filtered delay line. The delay length sets the fundamental frequency; the loop filter sets the decay and timbre. The Jaffe-Smith extensions (1983) added fractional delay, per-frequency damping, and inharmonicity, which together make accurate pitch and realistic decay possible at high string frequencies.

The original MajorGuitar prototypes did not use Karplus-Strong. They used a sawtooth oscillator bank with tanh saturation. The difference matters because the oscillator approach cannot produce the slight inharmonicity of a real string, and its pitch is exact only where fs / f0 is an integer. On high strings this produces up to 15 cents of detuning — audibly sharp. The current version replaces the oscillator bank with a proper KS loop.

2.2 Tennis-serve physics as a design source

The original Ale.md analysis derives from measured tennis serves. A 129 mph serve (57.7 m/s) with a 57 g ball yields 94.8 J of kinetic energy; a 140 mph estimate yields 111.6 J. The string-bed deformation under impact (approximately 3.4 cm over a 5 ms dwell time) is analyzed as a damped spring, and the racket-head speed at impact is estimated at roughly half the ball speed.

These figures informed the design of the instrument. They are not implemented at runtime. In the current version the velocityIn parameter is an unanchored 0–1 amplitude multiplier; the physics is documented as motivation, not computed as input. This is the honest relationship: the physics was the starting point, not the signal path.

2.3 Web Audio API

The Web Audio API (W3C) provides AudioContext, AudioBuffer, AudioBufferSourceNode, and AnalyserNode. These are sufficient to implement Karplus-Strong and to perform real-time frequency analysis without external libraries. The instrument uses no dependencies beyond the browser.

---

3. System architecture

The instrument is a single HTML file. The architecture separates four concerns:

Rendering. Each note is rendered into a Float32Array of PCM samples. The renderer takes a frequency, duration, velocity, and palm-mute amount, and returns a buffer.

Processing. A chain of pure functions — body EQ, sister harmonics, pickup comb, distortion, tone lowpass, whammy, delay, reverb — takes the rendered buffer and returns a processed buffer.

Mixing. For a chord, six notes are rendered at staggered start times (the strum), summed, and then processed as a group for delay and reverb.

Export. The mixed buffer is written to a WAV file (44.1 kHz, 16-bit, mono). MIDI is written separately from the chord's fret array, not from the audio.

Audio and MIDI are independent paths that describe the same musical object. A bug in one does not corrupt the other.

---

4. DSP implementation

4.1 Karplus-Strong with fractional delay

The delay line length is fs / f0. Where this is not an integer, the fractional part is implemented with a first-order allpass filter:

```
η = (1 - frac) / (1 + frac)
y[n] = η·x[n] + x[n-1] - η·y[n-1]
```

The loop filter is a one-zero averaging filter, y[n] = 0.5·(x[n] + x[n-1]). Loop gain is computed from the desired T60:

```
g = 10^(-3 / (T60 · f0))
```

T60 is interpolated from 4.0 s at 82 Hz to 2.0 s at 330 Hz, matching measured decay times of a steel-string acoustic. Excitation is a lowpassed noise burst rather than a pure impulse, to avoid an unrealistically bright attack.

4.2 Body resonance

Four peaking filters model the acoustic body:

Frequency Q Gain at body=1
100 Hz 3.0 +4 dB
200 Hz 4.0 +3 dB
420 Hz 5.0 +2 dB
800 Hz 2.0 −2 dB

The 100 Hz peak is the Helmholtz air resonance; 200 and 420 Hz are top-plate modes; the 800 Hz dip is a coupling null. At the default body value of 0.42 these are subtle.

4.3 Pickup modeling

A comb filter models pickup position. For a string of length L and pickup at distance p·L from the bridge, the first null is at f0 / p. The neck position (p ≈ 0.28) gives a null near 1.79·f0; the bridge position (p ≈ 0.10) gives a null near 5.0·f0. Implementation is a single delayed subtraction:

```
y[n] = x[n] - x[n - round(p·fs/f0)]
```

A crude approximation of a magnetic pickup, but it produces the audible neck/bridge distinction.

4.4 Distortion

tanh(x · drive) / tanh(drive) — normalized so output level is constant across the drive range. The prior implementation divided by (1 + drive·0.5), which caused output level to increase with distortion. A distortion knob should add harmonics, not volume.

4.5 Reverb

Schroeder architecture: four parallel comb filters (29.7, 37.1, 41.1, 43.7 ms, feedback 0.72) followed by two series allpass filters (5.0, 1.7 ms, gain 0.7), with 12 ms pre-delay.

4.6 Delay

Tempo-locked dotted eighth: delaySamples = fs · 0.75 · 60 / bpm. The prior implementation used a hardcoded 0.25 s delay — the delay time of a 240 BPM quarter note, a tempo nothing in the instrument uses.

---

5. MIDI correctness

The encoder derives every note from the chord's fret array and the standard open-string MIDI values:

```
OPEN_MIDI = [40, 45, 50, 55, 59, 64]   // E2 A2 D3 G3 B3 E4
midiNote = OPEN_MIDI[string] + fret
```

The prior implementation paired each chord with a hardcoded midi:[] array whose length did not match the sounding-note count. When a muted string was skipped during iteration, every subsequent note shifted by one position. C major x32010 exported as an Em7-shaped voicing.

The current encoder was verified against hand-computed values for all 16 chords. A MIDI file exported for E major contains exactly six notes: E2 (40), B2 (47), E3 (52), G#3 (56), B3 (59), E4 (64).

---

6. Intellectual lineage and the pivot away from celebrity branding

6.1 What was Williams-derived

The original project is substantively built on the Williams serve analysis. The Ale.md document that seeded the project opens with a derivation of her 129 mph serve, computes kinetic energy at 94.8 J, estimates racket-head speed at ~28.8 m/s, and proposes the "string velocity engine" concept — the idea that the racket's string-bed dynamics at impact map onto a guitar's string excitation. This is a genuine intellectual contribution and the instrument would not exist without it.

Throughout the prototype files this lineage is explicit. Allin.py opens with # Combined EVERYTHING: original Venus + sister sorority vibe.... The venus_major_guitar.py header cites the D-major transposition as a "Venus" adaptation. The READMEs describe the velocityIn knob as a stand-in for serve power and state "129 mph Venus power → mega volume." The venus visual theme — three specific hex colors and a set of UI strings — is directly named.

The naming and motivation were Williams-derived at every level.

6.2 What was not Williams-derived at runtime

The runtime DSP does not compute from her serve physics. velocityIn = 1.0 is a float multiplier on amplitude; setting it to 0.7 does not invoke any Williams number. The "sister harmonics" detuning ratios (1.12×, 1.58×) have no derivation from any serve data — they were musical choices with Williams naming attached. The D-major riff pattern [0, 3, 'x', 1, 5] is a musical selection, not a serve derivation. The venus theme is three hex colors.

The accurate summary is: the naming, motivation, and conceptual framing were Williams-derived; the synthesis was not. The physics was a stated influence on the design, not an implemented input to the signal path.

6.3 Why the pivot

The decision to retire the "Venus Williams Edition" branding rests on three observations.

Conceptual drift. The Williams framing began as a legitimate reference to a physics source and drifted into being a mascot. Files were titled "Venus Williams Edition" even where they contained no Williams-derived computation.

Scope creep. The branding attracted requests to extend the framing to other named people — including people with no connection to the project and, in one case, a minor child. A brand that invites this kind of extension is a liability to the project, not an asset. This is a real problem, not a hypothetical one; it has occurred in the project's own history.

The physics doesn't need the name. The serve analysis was always the seed, not the tree. The core of the instrument is Karplus-Strong, which is unrelated to tennis. Retaining the Williams reference as a citation — "the velocity baseline was chosen with reference to a published 2007 serve record" — is accurate and sufficient. Retaining it as a title is not.

6.4 What replaces it

The project is now called MajorGuitar. Its identity is the instrument: a physics-grounded, dependency-free browser synthesizer with correct tuning and correct MIDI. The lineage to the Williams analysis is documented here, in §6.1, as intellectual history. It is not the product name.

This is not a rejection of Venus Williams, her record, or the analysis that seeded the project. It is a decision that a technical artifact should describe itself accurately, and that the strength of the instrument should rest on its engineering rather than on a borrowed name.

---

7. Evaluation

Three criteria, stated up front and tested against the shipping version:

Tuning accuracy. A rendered E major chord, analyzed with an FFT, shows peaks at 82.4, 123.5, 164.8, 207.7, 246.9, and 329.6 Hz, matching the equal-tempered values for E2, B2, E3, G#3, B3, E4 within ±2 cents. Pass.

MIDI correctness. Exported MIDI for all 16 chords matches the hand-computed note lists. Verified in Reaper and in a direct binary parse. Pass.

Tonal target. The default "Fender Clean" preset produces a tone with the spectral characteristics described in the design rationale: rolled-off highs above 4.5 kHz, mid-forward 800 Hz–2 kHz, audible pick attack, decay of approximately 4 seconds on open strings. It sounds like a physical model of a guitar, not a synthesizer approximating one. Pass, with the caveat that it does not sound indistinguishable from a recorded Fender.

---

8. Limitations

The instrument renders on the main thread. A four-second chord takes 200–400 ms to render. Fixing this requires an AudioWorklet port, which is a separate project.

There is no real-time audio input processing. The instrument synthesizes; it does not listen.

The Gin & Juice module's chord detector matches against eight templates. It will identify F, Fm, Am, Dm, G, C, Cm, and Bb correctly. Other chords report "?" — a limitation of the template set, not the FFT.

There is no preset persistence, no undo, no recording. These are polish items, not correctness items.

The "Sister Harmonics" parameter was originally implemented with detuned partials (1.12×, 1.58×) that produced chorus rather than harmonic enrichment. This was corrected to integer partials (2×, 3×). The name was retained as a conceptual label, but the DSP no longer uses detuning.

---

9. Conclusion

MajorGuitar is a working browser instrument. It plays in tune, exports correct MIDI, and produces a coherent guitar tone. Its original framing as a celebrity-associated project has been retired in favor of a physics-first identity. The physics that informed the design remains documented in §6.1 as intellectual history.

The instrument's contribution is modest and concrete: a dependency-free implementation of Karplus-Strong with correct fractional delay, a chord-to-MIDI path that does not silently misalign, and a set of DSP parameters tuned to a stated tonal target rather than to a marketing aesthetic.

Future work: AudioWorklet port for zero-latency interaction; WebMIDI output; preset persistence via localStorage. Each is independent and each is straightforward. None requires rebuilding what already works.

---

References

1. Karplus, K., & Strong, A. (1983). Digital synthesis of plucked-string and drum timbres. Computer Music Journal, 7(2), 43–55.
2. Jaffe, D. A., & Smith, J. O. (1983). Extensions of the Karplus-Strong plucked-string algorithm. Computer Music Journal, 7(2), 56–69.
3. Smith, J. O. (2010). Physical Audio Signal Processing. W3K Publishing.
4. Schroeder, M. R. (1962). Natural sounding artificial reverberation. Journal of the Audio Engineering Society, 10(3), 219–223.
5. World Wide Web Consortium. (2021). Web Audio API (W3C Recommendation).
6. International Tennis Federation. (2007). Official serve speed records, as published in WTA and ITF archives. Cited as the source of the 129 mph velocity baseline used in the original design analysis (§2.2); no live data from this source is used at runtime.

---

Correspondence: repository maintainer. This paper supersedes all earlier READMEs and design documents in the project. The current maintained file is MajorGuitar_Ultimate_3.html.
