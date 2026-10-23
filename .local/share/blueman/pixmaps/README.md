# Blueman replacement meters

Thin SVG replacements for the battery, received signal strength (RSSI), and transmit power (TPL) meters in Blueman's Bluetooth Manager. Both options use the same battery icons: `#8a97bf` outlines with `#c7d0ea` fill.

| Folder | Appearance |
| --- | --- |
| `blueman-pixmaps-replacement-icons-transparent-option-1` | Battery visible; RSSI and TPL replaced with narrow, transparent placeholders for a simpler display. Some layout spacing may remain. |
| `blueman-pixmaps-replacement-icons-option-2` | All three meters visible: battery and TPL in `#8a97bf`, RSSI in `#bfb28a`. |

The two options offer a choice between a battery-only appearance and additional connection readings. Each folder is self-contained and includes ten states per meter. Both can be installed; the most recently installed option becomes active.

Both folders include `the-hideous-originals.png` for comparison.

## Install

Requires the system Blueman package and its SVG loader. Extract the ZIP, open a terminal inside the chosen option's folder, and run as your normal user, without `sudo`:

```sh
/usr/bin/python3 setup.py
```

The installer copies that option's folder into `~/.local/share/themes/blueman/`, alongside your existing `gtk.css`. It preserves `gtk.css` and creates user-local menu, D-Bus, and systemd overrides. `XDG_DATA_HOME` and `XDG_CONFIG_HOME` are respected; no username is hard-coded.

Quit Bluetooth Manager completely, then reopen it from the application menu or tray. For a shell launcher, rofi script, or Sway binding, run the installed option's `launcher.py`. Keep `GTK_THEME=blueman` to select your Blueman GTK theme. For example, the transparent option uses:

```sh
GTK_THEME=blueman /usr/bin/python3 "${XDG_DATA_HOME:-$HOME/.local/share}/themes/blueman/blueman-pixmaps-replacement-icons-transparent-option-1/launcher.py"
```

## Remove

Quit Bluetooth Manager, then run this from either installed option's folder:

```sh
/usr/bin/python3 setup.py --remove
```

Removal removes the installed meter options, restores backed-up user files, and preserves subsequent edits and `gtk.css`. The private restoration record is kept at `~/.config/blueman-midnight/installation.json`, outside the theme directory.

If you installed an earlier ZIP under `~/.local/share/blueman-midnight/`, remove that installation before using this version:

```sh
/usr/bin/python3 "${XDG_DATA_HOME:-$HOME/.local/share}/blueman-midnight/setup.py" --remove
```

This launcher adapts Blueman's internal image loading and may need adjustment after Blueman updates.
