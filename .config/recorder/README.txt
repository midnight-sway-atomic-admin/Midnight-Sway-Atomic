Recorder

A simple screen-and-audio, or screen-only, or audio-only recorder for Fedora Sway Atomic.

Note: there is currently a Firefox bug -- not a bug in the app -- that occurs when privacy.resistFingerprinting in about:config is set to true: pure audio recorded by the app will be heavily distorted if it is music; speech audio is not affected. So when you need to record a song with the audio-only mode, you must temporarily set privacy.resistFingerprinting to false.  

To use the app:

1. Use the updated Firefox "policies.json" file. It keeps camera and screen-sharing requests blocked and locked for ordinary websites, while allowing screen sharing only for the Recorder at http://127.0.0.1:27391. Microphone requests remain enabled so Firefox can show its normal audio-device chooser.

2. Open the app either by typing "python3 [absolute path to the recorder.py file]" in your terminal, or place recorder.py in .config/recorder and launch it via rofi (see the updated "rofi-apps" bin file).

3. For screen recording, select your display when Firefox asks.

4. For system audio, choose the “Monitor of …” audio source in Firefox's audio-device popup.

5. Click Stop when finished. The recording downloads automatically.

Recordings are saved as WebM files.

Security and privacy:

Recorder works entirely on your computer. It does not require an Internet connection, upload recordings, or send audio or video to any remote service.

The app communicates only through the fixed local address http://127.0.0.1:27391 on your own machine. Recordings are captured by Firefox, processed locally, and saved directly to your computer.

Firefox policy permits screen sharing only for the local Recorder address; new screen-sharing requests from ordinary websites remain blocked and locked. Camera access is disabled. Microphone requests are not globally blocked or locked because Firefox must be allowed to show its normal audio-device chooser so you can select the “Monitor of …” system-audio source.

Temporary recording data is stored privately and removed after use or when the app closes. The local Recorder interface is protected by a random access token and restrictive browser security settings.

Closing the Recorder tab normally notifies the local background helper to shut down. If Firefox does not deliver that close notification, the helper detects the missing one-second heartbeats and shuts itself down automatically within about ten seconds.
