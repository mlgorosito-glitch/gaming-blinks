# gaming-blinks
A game code with pygame that integrates electroencephalography for a more immersive experience

<img width="1080" height="1080" alt="Flyer_Game" src="https://github.com/user-attachments/assets/26e50f8d-262b-4844-8a9b-cb50fdc87bd4" />

## Project Context
This project was developed within the framework of the leveling course “Applications of Probability and Statistics for Time Series Data Processing”, part of the PhD program in Engineering at ITBA. The work was carried out at the Sleep and Memory Laboratory (https://www.labsuenoymemoria.com/), located within the same institution, and reflects the application of the concepts and procedures covered in the course. The project integrates core notions of programming and EEG signal processing.

## Game Design 
Regarding the game design, a conservative approach was adopted, as the main objective was to rely exclusively on Python libraries that are better suited for 2D game development. To introduce movement, sprites were used. The game logic is intentionally simple: the player moves through the environment and must shoot at targets. To increase the level of difficulty, collision detection between the objects within the game environment was implemented. 

<img width="1193" height="628" alt="Captura de pantalla 2025-12-16 161538" src="https://github.com/user-attachments/assets/c9537c77-dfaf-4fb7-8cce-80df864d66ff" />

## EEG/EOG Signal Acquisition
The blink detection algorithm operates with real-time (RT) EEG/EOG signal acquisition. Four electrodes were used: one reference electrode, one ground electrode, and two electrodes placed near the eyes to capture eye-related (EOG) activity associated with blink events. The left eye electrode was positioned approximately 1 cm above the left eye, while the right eye electrode was placed approximately 1 cm lateral to the right eye. This configuration allows the capture of both positive and negative components of blink-related activity from each eye. Due to the differential setup, the signal recorded from the electrode closer to the reference typically exhibits higher amplitude. The channel used for blink detection corresponds to an averaged signal derived from both periocular electrodes. Despite this averaging, the positive and negative components associated with each eye can still be observed in the resulting signal.

## Signal Scaling and Units
Signals are typically measured in microvolts (µV), but in this implementation, all raw signals are internally converted to volts (V) for processing, including filtering and blink detection. This conversion is important because the detection algorithm relies on thresholds expressed in volts to identify significant changes in the signal. Accordingly, all amplitude thresholds, including those for blink detection, are defined in volts (V).

![EscalaVoltaje](https://github.com/user-attachments/assets/702b13ea-2401-4218-8ca4-14438bd19fde)

*Figure source: Mohammed et al. (2015), “A New EEG Acquisition Protocol for Biometric Identification Using Eye Blinking Signals”.

## Real-Time Blink Detection Algorithm
The sampling frequency (fs) is determined by the amplifier configuration. In this implementation, with fs = 250 Hz, the signal is sampled every 4 ms, providing sufficient temporal resolution for detecting transient events such as eye blinks. Incoming EEG/EOG data are acquired continuously and accumulated in an internal buffer that stores only newly received samples. Signal processing is performed in block-wise segments of 100 ms, corresponding to 25 samples at fs = 250 Hz. Whenever enough new samples are available, a block is extracted, filtered, and analyzed sequentially. This block-based processing strategy defines the effective real-time (RT) latency of the system while remaining fully decoupled from the graphical frame rate of the game.

Filtered samples are stored in a rolling buffer spanning a 6-second window, which provides temporal context for visualization and inspection but does not influence the detection decision. Blink detection is performed exclusively on the most recent processed block by identifying the maximum absolute amplitude and comparing it against a predefined voltage threshold. A refractory period is applied to prevent multiple detections of the same physiological event, ensuring robust and stable blink detection during real-time interaction.

## Requirements

The project requires the following Python packages:

- numpy
- scipy
- matplotlib
- pygame
- brainflow

Dependencies can be installed using:
```bash
pip install -r requirements.txt

## Real-Time Blink Detection Algorithm
