#!/usr/bin/python3
"""Local Firefox/PipeWire recorder; Python standard library only.

Firefox owns capture and A/V synchronization:
- Video comes from getDisplayMedia() through the Wayland/PipeWire portal.
- System audio comes from a Firefox audio-input selection; on Linux, choose the
  "Monitor of ..." source corresponding to the output device in use.
- A single MediaRecorder records the combined MediaStream, so the browser keeps
  the audio and video tracks on one media timeline.

FFmpeg is used only to remux the completed browser recording so the downloaded
WebM has conventional final container metadata. It does not shift, resample,
trim, decode, or re-encode either track.

Temporary captures are discarded on cancellation, failure, or helper shutdown.
Successful captures remain available for download until the next recording
after download or helper shutdown. No recovery copies are deliberately kept.
After an abnormal exit, this version's temporary captures are discarded on the
next launch. Older versions' unmarked cache directories are left untouched.
"""

import fcntl
import http.server
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from urllib.parse import parse_qs, urlsplit

FIREFOX_ID = "org.mozilla.firefox"
FFMPEG = "/usr/bin/ffmpeg"
FLATPAK = "/usr/bin/flatpak"
LOOPBACK = "127.0.0.1"
PORT = 27391
STATUS_FD_ENV = "RECORDER_STATUS_FD"
STARTUP_TIMEOUT = 30
HEARTBEAT_TIMEOUT = 10
MAX_CHUNK = 8 * 1024 * 1024

HTML_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recorder</title>
<style nonce="__CONTROL_TOKEN__">
:root {
    color-scheme: dark;
    --control: #8a97bf;
    --light: #a8b2d0;
    --muted: #aeb5c9;
    --border: #282d3a;
}
* { box-sizing: border-box; }
html, body { min-height: 100%; margin: 0; }
body {
    min-height: 100vh;
    display: grid;
    place-items: center;
    background: #000;
    color: #fff;
    font-family: system-ui, sans-serif;
}
.recorder {
    width: min(420px, calc(100vw - 40px));
    margin: 20px 0;
    padding: 28px;
    background: linear-gradient(145deg, #11141a, #0c0e13 55%, #090b0f);
    border: 1px solid var(--border);
    border-radius: 18px;
    box-shadow: 0 24px 80px #000a, inset 0 1px #ffffff06;
}
header { margin-bottom: 24px; text-align: center; }
h1 { margin: 0; font-size: 1.05rem; font-weight: 650; letter-spacing: .08em; }
.subtitle { margin: 7px 0 0; color: var(--muted); font-size: .82rem; }
fieldset { margin: 0 0 20px; padding: 0; border: 0; }
legend { margin-bottom: 10px; color: var(--muted); font-size: .78rem; }
.mode {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 9px 0;
    font-size: .85rem;
    cursor: pointer;
}
input { margin: 0; accent-color: var(--control); }
#audio-help {
    margin: 12px 0 0;
    padding-top: 14px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: .75rem;
    line-height: 1.5;
}
#audio-help[hidden] { display: none; }
fieldset:disabled { opacity: .5; }
fieldset:disabled .mode { cursor: default; }
.actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
button {
    font: inherit;
    font-size: .88rem;
    font-weight: 620;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 12px 10px;
    cursor: pointer;
}
#start { background: var(--control); color: #080a0e; }
#start:hover:not(:disabled) { background: var(--light); }
#stop { background: transparent; border-color: #69779f; color: var(--light); }
#stop:hover:not(:disabled) { background: #171b25; border-color: var(--control); }
button:disabled { opacity: .28; cursor: default; }
:focus-visible { outline: 2px solid var(--light); outline-offset: 4px; }
.status-wrap {
    display: flex;
    align-items: flex-start;
    gap: 9px;
    margin-top: 20px;
    padding-top: 18px;
    border-top: 1px solid var(--border);
}
#dot { flex: 0 0 7px; height: 7px; margin-top: 6px; background: #697083; border-radius: 50%; }
#dot.recording { background: var(--control); box-shadow: 0 0 10px #8a97bfa6; }
#status { margin: 0; color: var(--muted); font-size: .78rem; line-height: 1.55; white-space: pre-wrap; overflow-wrap: anywhere; }
#downloads a { display: block; margin-top: 12px; color: var(--light); font-size: .82rem; overflow-wrap: anywhere; }
</style>
</head>
<body>
<main class="recorder">
    <header><h1>Recorder</h1><p class="subtitle">Local screen and system audio capture</p></header>
    <fieldset id="modes" disabled>
        <legend>Capture</legend>
        <label class="mode"><input type="radio" name="mode" value="av" checked>Video and system audio</label>
        <label class="mode"><input type="radio" name="mode" value="video">Video only</label>
        <label class="mode"><input type="radio" name="mode" value="audio">Audio only</label>
        <p id="audio-help">For audio, choose the Firefox source named “Monitor of …” for the output device you are using.</p>
    </fieldset>
    <div class="actions">
        <button id="start" type="button" disabled>Start recording</button>
        <button id="stop" type="button" disabled>Stop</button>
    </div>
    <div class="status-wrap"><span id="dot" aria-hidden="true"></span><p id="status" role="status">Connecting to recorder...</p></div>
    <div id="downloads"></div>
</main>
<script nonce="__CONTROL_TOKEN__">
"use strict";
const TOKEN = "__CONTROL_TOKEN__";
const start = document.getElementById("start");
const stop = document.getElementById("stop");
const modes = document.getElementById("modes");
const audioHelp = document.getElementById("audio-help");
const status = document.getElementById("status");
const dot = document.getElementById("dot");
const downloads = document.getElementById("downloads");
let current = null;
let heartbeatBusy = false;
let helperAvailable = false;
let initialized = false;
let initializing = false;
const HELPER_UNAVAILABLE = "Recorder helper is unavailable. Relaunch the app if it has closed.";

function updateControls() {
    start.disabled = modes.disabled = !!current || !helperAvailable || !initialized;
}

function addDownload(result) {
    const link = document.createElement("a");
    link.href = controlUrl(`/api/download/${result.id}`);
    link.download = result.filename;
    link.textContent = `Download ${result.filename}`;
    downloads.append(link);
    return link;
}

function showDownloads(exports) {
    downloads.replaceChildren();
    for (const result of exports) addDownload(result);
}

function selectedMode() {
    return document.querySelector('input[name="mode"]:checked').value;
}

modes.onchange = () => {
    audioHelp.hidden = selectedMode() === "video";
};
modes.onchange();

function controlUrl(path) {
    return `${path}?token=${encodeURIComponent(TOKEN)}`;
}

async function request(path, {session, json, body, timeout = 15000} = {}) {
    const controller = new AbortController();
    const timer = timeout ? setTimeout(() => controller.abort(), timeout) : null;
    const headers = {};
    if (session?.id) headers["X-Recording-ID"] = session.id;
    if (json !== undefined) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(json);
    }
    try {
        const response = await fetch(controlUrl(path), {
            method: "POST", cache: "no-store", credentials: "omit",
            headers, body, signal: controller.signal
        });
        if (!response.ok) throw new Error((await response.text()).trim() || `Recorder error (${response.status}).`);
        return response.status === 204 ? null : await response.json();
    } finally {
        clearTimeout(timer);
    }
}

function forgetRecording(id) {
    if (history.state?.recordingId === id) history.replaceState(null, "");
}

async function cancelAbandonedRecording() {
    const id = history.state?.recordingId;
    if (!id) return;
    await request("/api/cancel", {session: {id}});
    forgetRecording(id);
}

async function initialize() {
    if (initialized || initializing) return;
    initializing = true;
    try {
        await cancelAbandonedRecording();
        const result = await request("/api/exports");
        showDownloads(result.exports);
        initialized = true;
        if (helperAvailable) status.textContent = "Ready.";
    } catch (error) {
        if (helperAvailable) status.textContent = `Could not prepare recorder:\n${error.message}`;
    } finally {
        initializing = false;
        updateControls();
    }
}

async function heartbeat() {
    if (heartbeatBusy) return;
    heartbeatBusy = true;
    try {
        await request("/api/heartbeat", {timeout: 3000});
        const recovered = !helperAvailable;
        helperAvailable = true;
        if (!initialized) void initialize();
        else if (recovered && !current) status.textContent = "Ready.";
    } catch (error) {
        helperAvailable = false;
        if (current?.phase === "starting" || current?.phase === "recording") {
            current.captureError = new Error(HELPER_UNAVAILABLE);
            stopRecording(current);
            stopTracks(current);
        }
        if (!current) status.textContent = HELPER_UNAVAILABLE;
    } finally {
        heartbeatBusy = false;
        updateControls();
    }
}

heartbeat();
const heartbeatTimer = setInterval(heartbeat, 1000);
window.addEventListener("pagehide", () => {
    clearInterval(heartbeatTimer);
    navigator.sendBeacon(controlUrl("/api/close"));
});
window.addEventListener("pageshow", event => { if (event.persisted) location.reload(); });
window.addEventListener("beforeunload", event => {
    if (current) { event.preventDefault(); event.returnValue = ""; }
});

function stopTracks(s) {
    s.stream?.getTracks().forEach(track => track.stop());
    s.stream = null;
    s.screenStream?.getTracks().forEach(track => track.stop());
    s.screenStream = null;
    s.audioStream?.getTracks().forEach(track => track.stop());
    s.audioStream = null;
}

function cleanup(s) {
    stopTracks(s);
    if (current === s) {
        current = null;
        updateControls();
        stop.disabled = true;
        dot.classList.remove("recording");
    }
}

function queueCapture(s, blob) {
    if (!blob.size || s.uploadError || s.startError) return;
    s.pendingBytes += blob.size;
    if (s.pendingBytes > 64 * 1024 * 1024) {
        // Stop capture, but preserve queued data if all uploads succeed.
        stopRecording(s);
    }
    s.uploads = s.uploads.then(async () => {
        if (s.uploadError) return;
        for (let offset = 0; offset < blob.size; offset += 8 * 1024 * 1024) {
            await request("/api/chunk", {session: s, body: blob.slice(offset, offset + 8 * 1024 * 1024), timeout: 60000});
        }
    }).catch(error => {
        s.uploadError = error;
        stopRecording(s);
    }).finally(() => { s.pendingBytes -= blob.size; });
}

function stopRecording(s = current) {
    if (!s || s.finishing) return;
    s.stopRequested = true;
    stop.disabled = true;
    if (s.recorder?.state === "recording") {
        s.phase = "stopping";
        s.recorder.stop();
    }
}

async function finish(s) {
    if (s.finishing) return;
    s.finishing = true;
    s.phase = "finishing";
    // The final blobs no longer need live screen or audio tracks.
    stopTracks(s);
    stop.disabled = true;
    dot.classList.remove("recording");
    status.textContent = "Finishing recording...";
    await s.ready;
    let failure = s.startError;
    try {
        await s.uploads;
        failure ||= s.uploadError || s.captureError;
        if (failure) throw failure;
        status.textContent = "Preparing download...";
        const result = await request("/api/finish", {session: s, timeout: 0});
        forgetRecording(s.id);
        addDownload(result).click();
        status.textContent = `Download started.\nFile size: ${(result.size / 1048576).toFixed(1)} MiB`;
    } catch (error) {
        await s.uploads;
        try {
            await request("/api/cancel", {session: s});
            forgetRecording(s.id);
        } catch (_) {}
        status.textContent = `${s.startError ? "Could not start recording" : "Could not finalize recording"}:\n${error.message}`;
    } finally {
        cleanup(s);
    }
}

function chooseMimeType(mode) {
    const candidates = mode === "audio"
        ? ["audio/webm;codecs=opus", "audio/webm"]
        : mode === "video"
            ? ["video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/webm"]
            : ["video/webm;codecs=vp9,opus", "video/webm;codecs=vp8,opus", "video/webm"];
    return candidates.find(type => MediaRecorder.isTypeSupported(type));
}

async function acquireAudio() {
    return await navigator.mediaDevices.getUserMedia({
        video: false,
        audio: {
            echoCancellation: false,
            noiseSuppression: false,
            autoGainControl: false,
            channelCount: {ideal: 2},
            sampleRate: {ideal: 48000}
        }
    });
}

start.onclick = async () => {
    if (current || !helperAvailable || !initialized) return;
    const mode = selectedMode();
    let ready;
    const s = {
        id: crypto.randomUUID(), mode,
        phase: "starting", uploads: Promise.resolve(), pendingBytes: 0,
        ready: new Promise(resolve => { ready = resolve; })
    };
    current = s;
    start.disabled = modes.disabled = true;
    stop.disabled = true;
    try {
        // getDisplayMedia() must be called while the Start-button activation is
        // still live, so combined mode acquires the screen before awaiting audio.
        if (mode !== "audio") {
            status.textContent = "Choose the display to record.";
            s.screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: {width: {ideal: 2560}, height: {ideal: 1600}, frameRate: {ideal: 60}},
                audio: false
            });
            if (s.captureError) throw s.captureError;
            const videoTrack = s.screenStream.getVideoTracks()[0];
            if (!videoTrack || videoTrack.readyState !== "live") throw new Error("No live screen track was provided.");
        }

        if (mode !== "video") {
            status.textContent = "Choose the system-output ‘Monitor of …’ audio source.";
            s.audioStream = await acquireAudio();
            if (s.captureError) throw s.captureError;
            const audioTrack = s.audioStream.getAudioTracks()[0];
            if (!audioTrack || audioTrack.readyState !== "live") throw new Error("No live audio track was provided.");
        }

        const tracks = [];
        if (s.screenStream) tracks.push(...s.screenStream.getVideoTracks());
        if (s.audioStream) tracks.push(...s.audioStream.getAudioTracks());
        s.stream = new MediaStream(tracks);
        if ((mode !== "audio" && s.stream.getVideoTracks().length !== 1) ||
            (mode !== "video" && s.stream.getAudioTracks().length !== 1)) {
            throw new Error("Firefox did not provide the expected recording tracks.");
        }

        for (const track of s.stream.getTracks()) {
            track.addEventListener("ended", () => {
                if (s.phase === "recording") {
                    if (track.kind === "audio" && !s.stopRequested) {
                        s.captureError = new Error("System-audio capture ended unexpectedly.");
                    }
                    stopRecording(s);
                } else if (s.phase === "starting") {
                    s.stopRequested = true;
                }
            }, {once: true});
        }

        status.textContent = "Starting capture...";
        await cancelAbandonedRecording();
        if (s.captureError) throw s.captureError;
        // Keep the ID across reloads, including while /api/start is in flight.
        history.replaceState({recordingId: s.id}, "");
        const result = await request("/api/start", {json: {mode: s.mode, id: s.id}, timeout: 30000});
        showDownloads(result.exports);
        if (s.captureError) throw s.captureError;
        if (s.stopRequested || s.stream.getTracks().some(track => track.readyState !== "live")) {
            throw new Error("A capture source ended before recording started.");
        }

        const mimeType = chooseMimeType(mode);
        if (!mimeType) throw new Error("Firefox does not support the required WebM recording format.");
        const options = {mimeType};
        if (mode !== "audio") options.videoBitsPerSecond = 50_000_000;
        if (mode !== "video") options.audioBitsPerSecond = 256_000;
        s.recorder = new MediaRecorder(s.stream, options);
        s.recorder.ondataavailable = event => queueCapture(s, event.data);
        s.recorder.onerror = event => {
            s.captureError = event.error || new Error("Browser media capture failed.");
            stopRecording(s);
        };
        s.recorder.onstop = () => { void finish(s); };
        let startTimer;
        try {
            await new Promise((resolve, reject) => {
                startTimer = setTimeout(() => reject(new Error("Browser recording did not start.")), 5000);
                s.recorder.onstart = resolve;
                s.recorder.start(1000);
            });
        } finally {
            clearTimeout(startTimer);
            s.recorder.onstart = null;
        }
        if (s.captureError) throw s.captureError;
        if (s.stopRequested || s.recorder.state !== "recording") throw new Error("Capture ended during startup.");

        s.phase = "recording";
        stop.disabled = false;
        dot.classList.add("recording");
        const videoSettings = s.stream.getVideoTracks()[0]?.getSettings();
        const audioTrack = s.stream.getAudioTracks()[0];
        const videoInfo = videoSettings
            ? `\nVideo: ${videoSettings.width ?? "?"}×${videoSettings.height ?? "?"} @ ${Number(videoSettings.frameRate || 0).toFixed(2)} fps`
            : "";
        const audioInfo = audioTrack ? `\nAudio: ${audioTrack.label || "selected Firefox input"}` : "";
        status.textContent = `Recording.${videoInfo}${audioInfo}\nFormat: WebM`;
    } catch (error) {
        s.startError = error;
        if (s.recorder?.state === "recording") {
            s.recorder.stop();
        } else {
            void finish(s);
        }
    } finally {
        ready();
    }
};

stop.onclick = () => stopRecording();
</script>
</body>
</html>
'''


class CaptureStorage:
    """Own one private cache, and discard this version's stale captures safely."""

    def __init__(self):
        cache = Path(os.environ.get("XDG_CACHE_HOME", ""))
        if not cache.is_absolute():
            cache = Path.home() / ".cache"
        cache.mkdir(parents=True, exist_ok=True)
        self.directory = cache / "firefox-pipewire-recorder"
        self.directory.mkdir(mode=0o700, exist_ok=True)
        info = self.directory.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
                or info.st_mode & 0o077):
            raise RuntimeError("The recorder cache must be a private directory owned by this user.")
        self.lock_fd = os.open(self.directory / ".lock",
                               os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
        try:
            info = os.fstat(self.lock_fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1:
                raise RuntimeError("The recorder cache lock is not a private regular file.")
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError("Another recorder or finalization process is using the cache.") from None
            # Only this application's private namespace is swept. In particular,
            # never guess who owns older recorder-* directories in the main cache.
            for entry in self.directory.iterdir():
                if entry.name.startswith("recorder-") and stat.S_ISDIR(entry.lstat().st_mode):
                    shutil.rmtree(entry)
        except BaseException:
            os.close(self.lock_fd)
            raise

    def __enter__(self):
        return self

    def __exit__(self, *_):
        # Closing (rather than LOCK_UN) also respects an inherited FFmpeg lock.
        os.close(self.lock_fd)


class State:
    def __init__(self, token, storage):
        self.token = token
        self.storage = storage
        self.lock = threading.Lock()
        self.page_seen = False
        self.last_heartbeat = time.monotonic()
        self.close_deadline = None
        self.stop_requested = False
        self.recording = None
        self.cancelled_ids = set()
        self.exports = {}
        self.active_downloads = 0

    def heartbeat(self):
        self.page_seen = True
        self.last_heartbeat = time.monotonic()
        self.close_deadline = None


class Recording:
    def __init__(self, mode, recording_id, cache):
        self.directory = Path(tempfile.mkdtemp(prefix="recorder-", dir=cache))
        self.id = recording_id
        self.mode = mode
        self.capture = self.directory / "capture.webm"
        self.started = time.strftime("%Y-%m-%d-%H-%M-%S")


def require_executable(path):
    if not (os.path.isfile(path) and os.access(path, os.X_OK)):
        raise RuntimeError(f"Required executable not found: {path}")


def command_output(*argv):
    result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, timeout=5)
    if result.returncode:
        raise RuntimeError(result.stderr.strip()[:500] or f"{Path(argv[0]).name} failed.")
    return result.stdout.strip()


def stop_process(process):
    if process is None:
        return
    for signum, timeout in ((signal.SIGINT, 3), (signal.SIGTERM, 2), (signal.SIGKILL, 2)):
        if process.poll() is not None:
            return
        try:
            process.send_signal(signum)
            process.wait(timeout=timeout)
            return
        except ProcessLookupError:
            return
        except subprocess.TimeoutExpired:
            pass
    raise RuntimeError("A recording process could not be stopped.")


def release_recording(state):
    if state.recording is not None:
        shutil.rmtree(state.recording.directory, ignore_errors=True)
        state.recording = None


def available_exports(state):
    return [{"id": key, "filename": export["filename"]}
            for key, export in state.exports.items()]


def start_recording(state, mode, recording_id):
    if mode not in ("av", "video", "audio"):
        raise ValueError("Invalid capture mode.")
    if state.recording:
        raise ValueError("A recording is already active.")
    if not isinstance(recording_id, str) or str(uuid.UUID(recording_id)) != recording_id:
        raise ValueError("Invalid recording ID.")
    if recording_id in state.cancelled_ids:
        raise ValueError("This recording was cancelled.")
    if recording_id in state.exports:
        raise ValueError("Recording ID already used.")
    require_executable(FFMPEG)
    for key, export in list(state.exports.items()):
        if export["downloaded"]:
            shutil.rmtree(export["directory"], ignore_errors=True)
            del state.exports[key]
    recording = Recording(mode, recording_id, state.storage.directory)
    state.recording = recording
    return {"id": recording.id, "exports": available_exports(state)}


def encode_recording(state, recording):
    if not recording.capture.is_file() or not recording.capture.stat().st_size:
        raise RuntimeError("The browser recording is empty.")
    output = recording.directory / "recording.webm"
    command = [
        FFMPEG, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-protocol_whitelist", "file", "-f", "matroska", "-i", str(recording.capture),
    ]
    if recording.mode == "av":
        command += ["-map", "0:v:0", "-map", "0:a:0", "-c", "copy"]
    elif recording.mode == "video":
        command += ["-map", "0:v:0", "-c:v", "copy"]
    else:
        command += ["-map", "0:a:0", "-c:a", "copy"]
    command.append(str(output))

    size_mib = recording.capture.stat().st_size / (1024 * 1024)
    deadline = time.monotonic() + max(60, size_mib)
    log_path = recording.directory / "remux.log"
    with log_path.open("wb") as log:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=log, start_new_session=True,
                                   pass_fds=(state.storage.lock_fd,))
        try:
            while process.poll() is None:
                if state.stop_requested:
                    raise RuntimeError("Recorder closed during finalization.")
                if time.monotonic() > deadline:
                    raise RuntimeError("Finalization timed out.")
                time.sleep(.1)
        finally:
            stop_process(process)
    if process.returncode:
        detail = log_path.read_text(errors="replace").strip()
        raise RuntimeError("Could not finalize recording: " + (detail[-500:] or "FFmpeg failed."))
    if not output.is_file() or not output.stat().st_size:
        raise RuntimeError("The finished recording is empty.")
    recording.capture.unlink(missing_ok=True)
    return output


def finish_recording(state, recording):
    try:
        path = encode_recording(state, recording)
        size = path.stat().st_size
    except Exception:
        release_recording(state)
        raise
    filename = f"{recording.started}-{'audio' if recording.mode == 'audio' else 'screen'}-recording.webm"
    state.exports[recording.id] = {
        "path": path, "directory": recording.directory, "filename": filename,
        "content_type": "audio/webm" if recording.mode == "audio" else "video/webm",
        "downloaded": False,
    }
    state.recording = None
    return {"id": recording.id, "filename": filename, "size": size}


def body_length(handler, maximum):
    values = handler.headers.get_all("Content-Length", [])
    if handler.headers.get("Transfer-Encoding") or len(values) != 1:
        raise ValueError("A single Content-Length is required.")
    try:
        length = int(values[0])
    except ValueError:
        raise ValueError("Invalid request length.") from None
    if length < 1 or length > maximum:
        raise ValueError("Invalid request size.")
    return length


def read_json(handler):
    length = body_length(handler, 1024)
    raw = handler.rfile.read(length)
    if len(raw) != length:
        raise ValueError("Incomplete request body.")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, ValueError):
        raise ValueError("Invalid JSON request.") from None
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object.")
    return value


def write_chunk(handler, recording):
    remaining = body_length(handler, MAX_CHUNK)
    with recording.capture.open("ab") as output:
        while remaining:
            chunk = handler.rfile.read(min(remaining, 1024 * 1024))
            if not chunk:
                raise ValueError("Incomplete recording upload.")
            output.write(chunk)
            remaining -= len(chunk)


def make_handler(state):
    html = HTML_TEMPLATE.replace("__CONTROL_TOKEN__", state.token).encode()
    page_path = f"/{state.token}/"

    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "Recorder"
        sys_version = ""

        def setup(self):
            super().setup()
            self.connection.settimeout(30)

        def log_message(self, *_):
            pass

        def headers_for(self, code, content_type, length, filename=None):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header("Permissions-Policy", "camera=(), microphone=(self), display-capture=(self)")
            policy = "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
            if content_type == "text/html; charset=utf-8":
                policy += (f"; script-src 'nonce-{state.token}'; style-src 'nonce-{state.token}'; "
                           "connect-src 'self'")
            self.send_header("Content-Security-Policy", policy)
            if filename:
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.end_headers()

        def reply(self, value=None, code=200):
            data = json.dumps(value).encode() if value is not None else b""
            self.headers_for(code, "application/json", len(data))
            self.wfile.write(data)

        def error(self, code, message):
            data = message.encode("utf-8", "replace")
            self.headers_for(code, "text/plain; charset=utf-8", len(data))
            self.wfile.write(data)

        def authorized(self, require_token=True):
            expected = f"{LOOPBACK}:{self.server.server_port}"
            if self.headers.get_all("Host", []) != [expected]:
                return False
            if not require_token and urlsplit(self.path).path == page_path:
                return True  # Allow navigation to the private recorder page.
            origin = self.headers.get("Origin")
            if origin is not None and origin != "http://" + expected:
                return False
            if self.headers.get("Sec-Fetch-Site") == "cross-site":
                return False
            if not require_token:
                return True
            try:
                query = parse_qs(urlsplit(self.path).query, max_num_fields=8)
                supplied = query.get("token", [""])
                return len(supplied) == 1 and secrets.compare_digest(supplied[0].encode(), state.token.encode())
            except (ValueError, UnicodeError):
                return False

        def do_GET(self):
            try:
                if not self.authorized(require_token=False):
                    self.error(403, "Forbidden.")
                    return
                path = urlsplit(self.path).path
                if path == page_path:
                    self.headers_for(200, "text/html; charset=utf-8", len(html))
                    self.wfile.write(html)
                elif path.startswith("/api/download/") and self.authorized():
                    self.download(path.removeprefix("/api/download/"))
                else:
                    self.error(404, "Not found.")
            except (OSError, ValueError):
                pass

        def download(self, key):
            with state.lock:
                export = state.exports.get(key)
                if export is None:
                    self.error(404, "Recording is unavailable.")
                    return
                source = export["path"].open("rb")
                length = os.fstat(source.fileno()).st_size
                state.active_downloads += 1
            try:
                with source:
                    self.headers_for(200, export["content_type"], length, export["filename"])
                    shutil.copyfileobj(source, self.wfile, 1024 * 1024)
                    self.wfile.flush()
                with state.lock:
                    export["downloaded"] = True
            finally:
                with state.lock:
                    state.active_downloads -= 1

        def do_POST(self):
            try:
                if not self.authorized():
                    self.error(403, "Forbidden.")
                    return
                path = urlsplit(self.path).path
                if path == "/api/heartbeat":
                    if state.stop_requested:
                        self.error(409, "Recorder is closing.")
                        return
                    state.heartbeat()
                    self.reply({})
                    return
                if path == "/api/close":
                    state.close_deadline = time.monotonic() + 2
                    self.reply(code=204)
                    return
                if state.stop_requested:
                    self.error(409, "Recorder is closing.")
                    return
                if not state.lock.acquire(timeout=35):
                    self.error(409, "Recorder is busy; wait for the current operation.")
                    return
                try:
                    if state.stop_requested:
                        self.error(409, "Recorder is closing.")
                        return
                    state.heartbeat()
                    if path == "/api/exports":
                        self.reply({"exports": available_exports(state)})
                        return
                    if path == "/api/start":
                        payload = read_json(self)
                        self.reply(start_recording(state, payload.get("mode"), payload.get("id")))
                        return
                    recording = state.recording
                    if path == "/api/cancel":
                        recording_id = self.headers.get("X-Recording-ID")
                        if recording_id is None or str(uuid.UUID(recording_id)) != recording_id:
                            raise ValueError("Invalid recording ID.")
                        # Cancellation may arrive before an abandoned /api/start.
                        state.cancelled_ids.add(recording_id)
                        if recording is not None and recording.id == recording_id:
                            release_recording(state)
                        # Finalization may have completed while cancellation waited for the lock.
                        export = state.exports.pop(recording_id, None)
                        if export is not None:
                            shutil.rmtree(export["directory"], ignore_errors=True)
                        self.reply(code=204)
                        return
                    if recording is None or self.headers.get("X-Recording-ID") != recording.id:
                        self.error(409, "This recording is no longer active.")
                        return
                    if path == "/api/chunk":
                        write_chunk(self, recording)
                        self.reply(code=204)
                    elif path == "/api/finish":
                        self.reply(finish_recording(state, recording))
                    else:
                        self.error(404, "Not found.")
                finally:
                    state.lock.release()
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                pass
            except Exception as error:
                try:
                    self.error(400 if isinstance(error, ValueError) else 500, str(error))
                except OSError:
                    pass

    return Handler


def status_write(message):
    value = os.environ.pop(STATUS_FD_ENV, None)
    if value is None:
        return
    try:
        fd = int(value)
        with os.fdopen(fd, "wb") as output:
            output.write(message.encode("utf-8", "replace"))
    except (OSError, ValueError):
        pass


def serve():
    os.umask(0o077)
    require_executable(FLATPAK)
    command_output(FLATPAK, "info", FIREFOX_ID)
    with CaptureStorage() as storage:
        serve_with_storage(storage)


def serve_with_storage(storage):
    state = State(secrets.token_urlsafe(32), storage)
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: setattr(state, "stop_requested", True))
    httpd = http.server.ThreadingHTTPServer((LOOPBACK, PORT), make_handler(state))
    httpd.daemon_threads = False
    httpd.timeout = .5
    try:
        url = f"http://{LOOPBACK}:{httpd.server_port}/{state.token}/"
        launcher = subprocess.Popen(
            [FLATPAK, "run", FIREFOX_ID, "--new-tab", url],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        startup_reported = False
        started = time.monotonic()
        while True:
            launcher.poll()
            if state.stop_requested and not state.active_downloads:
                break
            httpd.handle_request()
            now = time.monotonic()
            if not startup_reported:
                if state.page_seen:
                    status_write("OK\t" + url)
                    startup_reported = True
                elif now - started > STARTUP_TIMEOUT:
                    raise RuntimeError("Firefox did not open the recorder page before startup timed out.")
            expired = state.page_seen and now - state.last_heartbeat > HEARTBEAT_TIMEOUT
            if expired or (state.close_deadline is not None and now >= state.close_deadline):
                state.stop_requested = True
    finally:
        state.stop_requested = True
        httpd.server_close()
        with state.lock:
            release_recording(state)
            for export in state.exports.values():
                shutil.rmtree(export["directory"], ignore_errors=True)


def launch_detached():
    parent, child = socket.socketpair()
    process = None
    try:
        env = os.environ.copy()
        env[STATUS_FD_ENV] = str(child.fileno())
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--serve"],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True,
                                   env=env, pass_fds=(child.fileno(),))
        child.close()
        parent.settimeout(STARTUP_TIMEOUT + 10)
        data = bytearray()
        while len(data) < 8192:
            part = parent.recv(8192 - len(data))
            if not part:
                break
            data.extend(part)
        message = data.decode("utf-8", "replace")
        if message.startswith("OK\t"):
            return 0
        raise RuntimeError(message.removeprefix("ERROR\t") or "Background helper exited during startup.")
    except (OSError, RuntimeError) as error:
        if process is not None:
            stop_process(process)
        print(f"recorder: {error}", file=sys.stderr)
        return 1
    finally:
        parent.close()
        child.close()


def main():
    if sys.argv[1:] == ["--serve"]:
        try:
            serve()
        except Exception as error:
            status_write("ERROR\t" + str(error))
            print(f"recorder: {error}", file=sys.stderr)
            return 1
        return 0
    if sys.argv[1:]:
        print(f"usage: {Path(sys.argv[0]).name} [--serve]", file=sys.stderr)
        return 2
    return launch_detached()


if __name__ == "__main__":
    raise SystemExit(main())
