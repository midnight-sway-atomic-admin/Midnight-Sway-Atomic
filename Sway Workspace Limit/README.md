# Sway workspace limit

Limits each numbered workspace to two tiled windows. Additional windows move to
the next higher-numbered workspace with room, without switching your current
workspace. Existing workspaces on other outputs are skipped.

Floating windows, including dialogs made floating by Sway or your config, are
exempt. Scratchpad and unnumbered workspaces are ignored. Manual window moves are
also checked; windows aren't moved back automatically when space becomes available.

For Fedora Sway Atomic with Xwayland disabled. Uses the system Python and its
standard library; no additional Python modules are needed.

## Install

Extract the package, then run this from its `sway-workspace-limit` folder:

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

## Change the limit

Edit `LIMIT = 2` near the top of `~/.local/bin/sway-workspace-limit.py`, using a
positive integer. Then restart it:

```sh
pkill -f '^/usr/bin/python3 .*[/]sway-workspace-limit[.]py$' || true
flock "${SWAYSOCK}.limit" true
swaymsg reload
```
