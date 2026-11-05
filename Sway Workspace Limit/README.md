# Sway Workspace Limit

Limits each numbered workspace to two tiled windows. Additional windows move to
the next higher-numbered workspace with room, without switching your current
workspace. Existing workspaces on other outputs are skipped.

Floating windows, including dialogs made floating by Sway or your config, are
exempt. Scratchpad and unnumbered workspaces are ignored. Manual window moves are
also checked; windows aren't moved back automatically when space becomes available.

For Fedora Sway Atomic with Xwayland disabled. Uses the system Python and its
standard library; no additional Python modules are needed.

## Install

Download `sway-workspace-limit.py` and from its location run:

```sh
install -Dm755 sway-workspace-limit.py "$HOME/.local/bin/sway-workspace-limit.py"
```

Add this line to `~/.config/sway/config`:

```sway
exec_always ~/.local/bin/sway-workspace-limit.py
```

Start it from a Sway terminal:

```sh
swaymsg reload
```

## Workspace renumbering

Workspaces with plain numeric names are automatically kept consecutive. If
workspace 2 disappears from `1, 2, 3`, workspace 3 becomes 2. This keeps each
Waybar dot's position aligned with its workspace number on a single display.

Renumbering is enabled when the script runs. A custom numbered name such as
`2: web` disables automatic renumbering.

## Waybar dots

Copy the repository's updated `.config/waybar/config.jsonc` to
`~/.config/waybar/config.jsonc`. It already displays the focused workspace as a
filled dot and the others as hollow dots.

If you keep your own Waybar configuration, merge these settings into its
`sway/workspaces` section.

```jsonc
"sway/workspaces": {
    "format": "{icon}",
    "format-icons": {
        "focused": "●",
        "default": "○"
    }
}
```

Reload Waybar after updating its configuration.

```sh
pkill -SIGUSR2 -x waybar
```

## Change the limit

Edit `LIMIT = 2` near the top of `~/.local/bin/sway-workspace-limit.py`, using a
positive integer. Then restart it:

```sh
pkill -f '^/usr/bin/python3 .*[/]sway-workspace-limit[.]py$' || true
flock "${SWAYSOCK}.limit" true
swaymsg reload
```
