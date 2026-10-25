# Flatpak security profiles

**Firefox · GIMP · Showtime**  
For Fedora Sway Atomic only · Wayland

Requires **Flatpak 1.16 or newer**. Close all three apps and run the commands as your normal user. Do not use `sudo`.

Run the reset block first, then apply the three profiles below before reopening the apps.

## Reset existing user overrides

The first command removes global user overrides shared by all your Flatpaks, so it can affect your other apps too. The remaining commands remove the individual user overrides for Firefox, GIMP and Showtime. App data and portal permissions remain intact.

```bash
flatpak override --user --reset
flatpak override --user --reset org.mozilla.firefox
flatpak override --user --reset org.gimp.GIMP
flatpak override --user --reset org.gnome.Showtime
```

## Firefox

Networking, GPU acceleration and audio allowed. Use file portals for uploads and Save As.

```bash
flatpak override --user \
  --nofilesystem=host:reset \
  --unshare=ipc \
  --socket=wayland \
  --nosocket=x11 \
  --nosocket=fallback-x11 \
  --nosocket=inherit-wayland-socket \
  --nosocket=session-bus \
  --nosocket=system-bus \
  --nosocket=cups \
  --nosocket=gpg-agent \
  --nosocket=pcsc \
  --nosocket=ssh-auth \
  --nodevice=all \
  --nodevice=kvm \
  --nodevice=shm \
  --nodevice=input \
  --nodevice=usb \
  --device=dri \
  --nousb=all \
  --disallow=devel \
  --disallow=multiarch \
  --disallow=bluetooth \
  --disallow=canbus \
  --disallow=per-app-dev-shm \
  --share=network \
  --socket=pulseaudio \
  --no-talk-name=org.freedesktop.Notifications \
  --no-talk-name=org.freedesktop.FileManager1 \
  --no-talk-name=org.a11y.Bus \
  '--no-talk-name=org.gtk.vfs.*' \
  --system-no-talk-name=org.freedesktop.NetworkManager \
  '--no-talk-name=org.mpris.MediaPlayer2.firefox.*' \
  org.mozilla.firefox
```

## GIMP

Direct network, GPU and audio access denied. Open, save and export files in `~/gimp`.

```bash
flatpak override --user \
  --nofilesystem=host:reset \
  --unshare=ipc \
  --socket=wayland \
  --nosocket=x11 \
  --nosocket=fallback-x11 \
  --nosocket=inherit-wayland-socket \
  --nosocket=session-bus \
  --nosocket=system-bus \
  --nosocket=cups \
  --nosocket=gpg-agent \
  --nosocket=pcsc \
  --nosocket=ssh-auth \
  --nodevice=all \
  --nodevice=kvm \
  --nodevice=shm \
  --nodevice=input \
  --nodevice=usb \
  --nodevice=dri \
  --nousb=all \
  --disallow=devel \
  --disallow=multiarch \
  --disallow=bluetooth \
  --disallow=canbus \
  --disallow=per-app-dev-shm \
  --unshare=network \
  --nosocket=pulseaudio \
  --filesystem=xdg-config/GIMP:create \
  --filesystem="$HOME/gimp:create" \
  '--no-talk-name=org.gtk.vfs.*' \
  --no-talk-name=org.freedesktop.FileManager1 \
  --no-talk-name=org.gnome.Shell.Screenshot \
  --no-talk-name=org.kde.kwin.Screenshot \
  --no-talk-name=com.canonical.AppMenu.Registrar \
  org.gimp.GIMP
```

## Showtime

GPU acceleration and audio allowed; direct network access denied. Open local videos through the file chooser.

```bash
flatpak override --user \
  --nofilesystem=host:reset \
  --unshare=ipc \
  --socket=wayland \
  --nosocket=x11 \
  --nosocket=fallback-x11 \
  --nosocket=inherit-wayland-socket \
  --nosocket=session-bus \
  --nosocket=system-bus \
  --nosocket=cups \
  --nosocket=gpg-agent \
  --nosocket=pcsc \
  --nosocket=ssh-auth \
  --nodevice=all \
  --nodevice=kvm \
  --nodevice=shm \
  --nodevice=input \
  --nodevice=usb \
  --device=dri \
  --nousb=all \
  --disallow=devel \
  --disallow=multiarch \
  --disallow=bluetooth \
  --disallow=canbus \
  --disallow=per-app-dev-shm \
  --unshare=network \
  --socket=pulseaudio \
  --no-talk-name=org.freedesktop.Notifications \
  org.gnome.Showtime
```

## Notes

- Restart the app after applying its command. These settings persist until changed or reset.
- Firefox and Showtime need a working FileChooser portal to select host files. GIMP's `~/gimp` folder is created on launch if necessary.
- Audio permission also allows microphone input. Portal access, existing document grants and the separate accessibility bus remain available.
- Firefox crash reporting, some profiling and desktop media controls may be affected. GIMP's host configuration is not shared, and GPU-dependent plug-ins are outside this profile.
- Firefox's network permission includes reachable local services and abstract Unix sockets. It does not filter destinations.
- These fixed lists cover the reviewed upstream permission declarations. Recheck permissions after updates or changes to custom/global overrides; repeating the commands does not detect new D-Bus grants.

To inspect an app, run `flatpak info --show-permissions APP_ID`.

To remove its user overrides, run `flatpak override --user --reset APP_ID`. This returns to inherited app/global/system permissions; it does not recover earlier custom overrides or reset portal decisions.

Replace `APP_ID` with `org.mozilla.firefox`, `org.gimp.GIMP` or `org.gnome.Showtime`.

**Validation:** checked with Flatpak 1.18.4 against local test packages carrying the reviewed upstream permission declarations. No live Fedora/Sway application session was tested.

[Flatpak permissions](https://docs.flatpak.org/en/latest/sandbox-permissions.html) · [Command reference](https://docs.flatpak.org/en/latest/flatpak-command-reference.html)
