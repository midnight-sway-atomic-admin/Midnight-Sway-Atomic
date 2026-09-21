Recorder

A simple screen and audio, or screen, or audio recorder for Fedora Sway Atomic.

To use it:

1. Open the app either by typing "python [absolute path to the recorder.py file]" in your terminal; or place recorder.py in .config/recorder and launch it via rofi (see the updated "rofi-apps" bin file).
2. For screen recording, select your display when Firefox asks.
3. For system audio, choose the “Monitor of …” audio source.
4. Click Stop when finished. The recording downloads automatically.

Recordings are saved as WebM files.

Security and privacy:

Recorder works entirely on your computer. It does not require an Internet connection, upload recordings, or send audio or video to any remote service.

The app communicates only through a local address on your own machine. Recordings are captured by Firefox, processed locally, and saved directly to your computer.

Temporary recording data is stored privately and removed after use or when the app closes. The local recorder interface is protected by a random access token and restrictive browser security settings. Camera access is disabled.

Closing the Recorder tab also closes the background helper.
