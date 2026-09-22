Recorder

A simple screen-and-system-audio, screen-only, or audio-only recorder for
Fedora Sway Atomic. Firefox captures the media; a local Python helper handles
temporary files and prepares the download.

Requirements

The Python helper uses only the standard library. The app also requires:

- Python 3.
- Flatpak at /usr/bin/flatpak and Firefox installed as org.mozilla.firefox.
- FFmpeg at /usr/bin/ffmpeg.
- Working PipeWire audio and Wayland screen sharing through the desktop
  portals.

These dependencies must be available; Recorder does not install them.

Firefox audio note

With privacy.resistFingerprinting set to true in about:config, Firefox can
ignore Recorder's requests to disable echo cancellation, noise suppression,
and automatic gain control. This can especially distort recorded music. Speech can also
be affected, but it has not been in my tests. Mozilla tracks related behavior in bug 2036218 [1]; its effects
can depend on the Firefox version and audio setup.

If you encounter musical distortion for screen-only or audio-only recording, stop recording, temporarily set
privacy.resistFingerprinting to false, and relaunch Recorder before recording
again. Restore the setting afterwards. Disabling it reduces fingerprinting
protection across that Firefox profile, including other websites open in it.

Development

The intended feature set is complete. Future maintenance is expected to focus
on bug fixes and compatibility.

To use the app

1. If you use a restrictive Firefox policies.json, ensure that it permits
   screen-sharing requests from http://127.0.0.1:27391 and lets Firefox show
   its normal audio-input chooser. The intended policy setup blocks and
   locks new camera and screen-sharing requests, adds this local origin as
   the screen-sharing exception, and leaves microphone requests available.
   Check the active configuration in about:policies in the Flatpak Firefox
   used by Recorder [2]. Recorder does not install or change these policies.

2. Save the script as recorder.py and run:

       python3 "/absolute/path/to/recorder.py"

   For your rofi setup, place it at ~/.config/recorder/recorder.py and make
   the Recorder entry in rofi-apps run:

       python3 "$HOME/.config/recorder/recorder.py"

   Recorder opens its Firefox tab automatically. Use the page it opens: the
   full address includes a random token that changes on each launch. Opening
   http://127.0.0.1:27391 alone does not open the interface.

3. Select "Video and system audio", "Video only", or "Audio only", then click
   "Start recording".

4. For a mode with video, select the display when prompted.

5. For a mode with audio, choose the "Monitor of ..." source corresponding
   to the output device you are using. Selecting a microphone records that
   microphone instead. The monitor source captures sound routed to that
   output, including other applications and notifications.

6. Click "Stop" when finished. Recorder prepares the file and starts a
   Firefox download. Firefox's settings determine whether it saves directly
   or asks for a destination. A download link also remains on the page while
   the helper retains the file. Wait for the download to finish and confirm
   the file is saved before closing the tab or starting another recording.

All modes save WebM files, including audio-only mode. FFmpeg finalizes the
container without re-encoding the recorded audio or video. Only one Recorder
helper can run at a time, and local port 27391 must be available.

Security and privacy

Recorder works locally and needs no Internet connection. It does not send
recordings to a remote service or load remote resources. The Firefox page
sends captured data to the Python helper over http://127.0.0.1:27391, and
Firefox downloads the finished file from that same local helper. Firefox's
other network activity is controlled separately by its browser settings.

The helper listens only on 127.0.0.1. Access uses a random token, request
checks, and restrictive page security headers. Recorder never requests a
camera. Restrictions on what other websites may request depend on your
Firefox policies and existing permissions. Leaving microphone requests
enabled lets other websites ask for access; it does not automatically grant
them access.

Temporary recordings are kept in a private directory under
$XDG_CACHE_HOME/firefox-pipewire-recorder, or under
~/.cache/firefox-pipewire-recorder when XDG_CACHE_HOME is unset or unsuitable.
Cancelled or failed captures are discarded. Finished files remain available
until helper shutdown or, after download, the start of the next recording.
Normal shutdown removes the helper's temporary recording files. If a crash
leaves files behind, the next successful launch cleans up this version's
leftover captures. Downloaded files saved by Firefox are retained.

Closing the tab sends a shutdown request with a roughly two-second grace
period. If that notification is lost, the helper normally initiates shutdown
after about ten seconds without a heartbeat from the page. Heartbeats are
scheduled once per second. Active downloads and cleanup can delay the final
exit. Closing the tab during recording or finalization can discard the
unfinished recording.

References

[1] Mozilla bug 2036218, especially comment 8:
    https://bugzilla.mozilla.org/show_bug.cgi?id=2036218

[2] Firefox permission policies:
    https://firefox-admin-docs.mozilla.org/reference/policies/permissions/
