# Recorder

A simple recorder for **Fedora Sway Atomic** supporting:

- Screen and system audio
- Screen only
- Audio only

Firefox captures the media. A local Python helper manages temporary files, finalizes the recording, and serves the finished file for download.

## Requirements

The Python helper uses only the standard library. Recorder also requires:

- Python 3
- Flatpak at `/usr/bin/flatpak`
- Firefox installed as `org.mozilla.firefox`
- FFmpeg at `/usr/bin/ffmpeg`
- Working PipeWire audio
- Working Wayland screen sharing through the desktop portals

Recorder does not install or configure these dependencies.

## Firefox Audio Note

If `privacy.resistFingerprinting` is set to `true` in `about:config`, Firefox can ignore Recorder's requests to disable:

- Echo cancellation
- Noise suppression
- Automatic gain control

This can noticeably distort recorded music. Speech can also be affected, although it has not been in my tests.

Mozilla tracks related behavior in [bug 2036218](https://bugzilla.mozilla.org/show_bug.cgi?id=2036218), particularly comment 8. The effect can depend on the Firefox version and audio setup.

If you encounter musical distortion when recording system audio:

1. Stop the recording.
2. Temporarily set `privacy.resistFingerprinting` to `false`.
3. Relaunch Recorder.
4. Make the recording.
5. Restore `privacy.resistFingerprinting` afterwards.

Disabling this setting reduces fingerprinting protection across that Firefox profile, including for other websites open in it.

## Usage

### 1. Check Firefox policies

If you use a restrictive `policies.json`, ensure that Firefox:

- Permits screen-sharing requests from `http://127.0.0.1:27391`
- Can display its normal audio-input chooser

The intended policy configuration blocks and locks new camera and screen-sharing requests, adds this local origin as a screen-sharing exception, and leaves microphone requests available.

Check the active policy configuration in `about:policies` in the Flatpak Firefox instance used by Recorder.

See the [Firefox permission policies documentation](https://firefox-admin-docs.mozilla.org/reference/policies/permissions/) for details.

Recorder does not install or modify Firefox policies.

### 2. Launch Recorder

Save the script as `recorder.py` and run:

```bash
python3 "/absolute/path/to/recorder.py"
```

For a rofi setup, place it at:

```text
~/.config/recorder/recorder.py
```

Then configure the Recorder entry in `rofi-apps` to run:

```bash
python3 "$HOME/.config/recorder/recorder.py"
```

Recorder opens its Firefox tab automatically.

Use the page that Recorder opens. Its full address contains a random token that changes on every launch. Opening only:

```text
http://127.0.0.1:27391
```

does not open the interface.

### 3. Choose a recording mode

Select one of:

- **Video and system audio**
- **Video only**
- **Audio only**

Then click **Start recording**.

### 4. Select the display

For a mode that includes video, select the display when Firefox prompts you.

### 5. Select the audio source

For a mode that includes audio, choose the **Monitor of ...** source corresponding to the output device you are using.

Selecting a microphone records that microphone instead.

The monitor source captures audio routed to that output, including sound from other applications and notifications.

### 6. Stop and save the recording

Click **Stop** when finished.

Recorder finalizes the file and starts a Firefox download. Firefox's own settings determine whether the file is saved automatically or Firefox asks for a destination.

A download link also remains on the Recorder page while the helper retains the completed file.

Wait for the download to finish and confirm that the file has been saved before:

- Closing the Recorder tab
- Starting another recording

## Recording Format

All recording modes produce **WebM** files, including audio-only mode.

FFmpeg finalizes the container without re-encoding the recorded audio or video.

Only one Recorder helper can run at a time, and local port `27391` must be available.

## Security and Privacy

Recorder works entirely locally and requires no Internet connection.

It does not:

- Upload recordings to a remote service
- Load remote resources
- Request camera access

The Firefox page sends captured media to the Python helper over:

```text
http://127.0.0.1:27391
```

Firefox downloads the completed file from the same local helper.

Any other Firefox network activity is controlled separately by Firefox and its settings.

### Local access

The helper listens only on `127.0.0.1`.

Access is protected by:

- A random per-launch token
- Request validation
- Restrictive page security headers

Restrictions on what other websites may request depend on your Firefox policies and existing permissions.

Leaving microphone requests enabled allows other websites to ask for microphone access. It does **not** automatically grant that access.

## Temporary Files and Cleanup

Temporary recordings are stored in:

```text
$XDG_CACHE_HOME/firefox-pipewire-recorder
```

or, when `XDG_CACHE_HOME` is unset or unsuitable:

```text
~/.cache/firefox-pipewire-recorder
```

Cancelled or failed captures are discarded.

Finished files remain available until either:

- The helper shuts down, or
- After download, the next recording begins

Normal shutdown removes the helper's temporary recording files.

If a crash leaves files behind, the next successful launch cleans up leftover captures created by this version of Recorder.

Files already downloaded and saved by Firefox are not removed.

## Shutdown Behavior

Closing the Recorder tab sends a shutdown request with a grace period of roughly two seconds.

If that notification is lost, the helper normally begins shutting down after about ten seconds without receiving a heartbeat from the page. Heartbeats are scheduled once per second.

Active downloads and cleanup can delay final exit.

Closing the tab while a recording is in progress or while Recorder is finalizing it can discard the unfinished recording.

## Development

The intended feature set is complete.

Future development is expected to focus primarily on:

- Bug fixes
- Firefox compatibility
- Fedora, PipeWire, Wayland, and portal compatibility

## References

1. [Mozilla bug 2036218](https://bugzilla.mozilla.org/show_bug.cgi?id=2036218) — particularly comment 8
2. [Firefox permission policies](https://firefox-admin-docs.mozilla.org/reference/policies/permissions/)
