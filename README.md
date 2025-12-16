# gaming-blinks
A game code with psygame that integrates electroencephalography for a more immersive experience

<img width="1080" height="1080" alt="Flyer_Game" src="https://github.com/user-attachments/assets/26e50f8d-262b-4844-8a9b-cb50fdc87bd4" />

This project was developed within the framework of the leveling course “Applications of Probability and Statistics for Time Series Data Processing”, part of the PhD program in Engineering at ITBA. The work was carried out at the Sleep and Memory Laboratory (https://www.labsuenoymemoria.com/), located within the same institution, and reflects the application of the concepts and procedures covered in the course. The project integrates core notions of programming and EEG signal processing.

Regarding the game design, a conservative approach was adopted, as the main objective was to rely exclusively on Python libraries that are better suited for 2D game development. To introduce movement, sprites were used. The game logic is intentionally simple: the player moves through the environment and must shoot at targets. To increase the level of difficulty, collision detection between the objects within the game environment was implemented. 

The blink detection algorithm operates with real-time (RT) EEG/EOG signal acquisition. Signals are typically measured in microvolts (µV), but in this implementation, all raw signals are internally converted to volts (V) for processing, including filtering and blink detection. This conversion is important because the detection algorithm relies on thresholds expressed in volts to identify significant changes in the signal. Accordingly, all amplitude thresholds, including those for blink detection, are defined in volts (V).

![EscalaVoltaje](https://github.com/user-attachments/assets/702b13ea-2401-4218-8ca4-14438bd19fde)

*Figure source: Mohammed et al. (2015), “A New EEG Acquisition Protocol for Biometric Identification Using Eye Blinking Signals”.

The sampling frequency (fs) is set based on the amplifier's configuration. In this case, at fs = 250 Hz, the signal is sampled every 4 ms, providing the temporal resolution required for detecting events like blinks. The signal is then processed in 100 ms blocks, corresponding to 25 samples at fs = 250 Hz, with each block being filtered and analyzed independently. This block-wise processing defines the RT latency, ensuring efficient detection without interfering with the graphical frame rate of the game. Filtered signals are stored in a rolling buffer with a 6-second window, providing context for visualization but not influencing the detection decision, which is based only on the most recent block. The algorithm detects blinks by identifying the maximum absolute value within each block and comparing it against a predefined voltage threshold. A refractory period ensures that multiple detections of the same blink are prevented, providing a robust and responsive detection system.
