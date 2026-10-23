# Blueman replacement meters

Thin SVG replacements for the battery, received signal strength (RSSI), and transmit power (TPL) meters in Blueman's Bluetooth Manager, made for my Fedora Sway Atomic rice. Both options use the same battery icons: `#8a97bf` outlines with `#c7d0ea` fill.

| Folder | Appearance |
| --- | --- |
| `blueman-pixmaps-replacement-icons-transparent-option-1` | Battery visible; RSSI and TPL replaced with narrow, transparent placeholders for a simpler display. Some layout spacing may remain. |
| `blueman-pixmaps-replacement-icons-option-2` | All three meters visible: battery and TPL in `#8a97bf`, RSSI in `#bfb28a`. |

The two options offer a choice between a battery-only appearance and additional connection readings. Each folder is self-contained and includes ten states per meter. Install one option at a time; installing the other replaces the current option.

## Install

Requires the system Blueman package and its SVG loader. Open a terminal inside the chosen option's folder and run as your normal user, without `sudo`:

```sh
/usr/bin/python3 setup.py
```

Quit Bluetooth Manager completely, then reopen it from the application menu or tray. Installation uses `~/.local/share/blueman-midnight/` and user-local menu, D-Bus, and systemd overrides. It respects `XDG_DATA_HOME` and `XDG_CONFIG_HOME`; system package files aren't edited.

For a shell launcher or Sway binding that otherwise calls `blueman-manager` directly, use:

```sh
/usr/bin/python3 "${XDG_DATA_HOME:-$HOME/.local/share}/blueman-midnight/launcher.py"
```

## Remove

Quit Bluetooth Manager, then run:

```sh
/usr/bin/python3 "${XDG_DATA_HOME:-$HOME/.local/share}/blueman-midnight/setup.py" --remove
```

Removal restores backed-up user files and preserves subsequent edits. This launcher adapts Blueman's internal image loading and may need adjustment after Blueman updates.
