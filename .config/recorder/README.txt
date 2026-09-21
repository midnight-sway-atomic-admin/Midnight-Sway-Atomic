Recorder

A simple screen and audio, screen-only, or audio-only recorder for Fedora Sway Atomic.

To use it:

1. Use the updated Firefox "policies.json" file. It keeps microphone and screen-sharing requests blocked and locked for ordinary websites while allowing them only for the Recorder at http://127.0.0.1:27391.
2. Open the app either by typing "python3 [absolute path to the recorder.py file]" in your terminal, or place recorder.py in .config/recorder and launch it via rofi (see the updated "rofi-apps" bin file).
3. For screen recording, select your display when Firefox asks.
4. For system audio, choose the “Monitor of …” audio source.
5. Click Stop when finished. The recording downloads automatically.

Recordings are saved as WebM files.

Security and privacy:

Recorder works entirely on your computer. It does not require an Internet connection, upload recordings, or send audio or video to any remote service.

The app communicates only through the fixed local address http://127.0.0.1:27391 on your own machine. Recordings are captured by Firefox, processed locally, and saved directly to your computer.

Firefox policy permits microphone and screen-sharing access only for this local Recorder address; new requests from ordinary websites remain blocked and locked. Camera access is disabled.

Temporary recording data is stored privately and removed after use or when the app closes. The local Recorder interface is protected by a random access token and restrictive browser security settings.

Closing the Recorder tab normally shuts down its local background helper immediately. If Firefox does not deliver the close notification, the helper detects that the page is gone and shuts itself down automatically within about three seconds. Reopening the Recorder during that brief interval will wait for the previous helper to release its local port rather than failing immediately.
