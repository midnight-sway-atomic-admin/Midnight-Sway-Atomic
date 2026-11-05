#!/usr/bin/python3
import fcntl
import json
import os
import re
import signal
import socket
import struct
import sys
from collections import Counter

LIMIT = 2
MARK = "_sway_workspace_limit_stage"
EXEMPT_APP_IDS = {"scratchpad-terminal"}
HEADER = struct.Struct("=6sII")
MAX_WORKSPACE_NUMBER = 2**31 - 1


def read_exact(connection, size):
    data = bytearray()
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk:
            raise EOFError("Sway closed the IPC connection")
        data.extend(chunk)
    return data


def receive(connection):
    magic, size, kind = HEADER.unpack(read_exact(connection, HEADER.size))
    if magic != b"i3-ipc" or size > 64 * 1024 * 1024:
        raise RuntimeError("Invalid Sway IPC header")
    return kind, json.loads(read_exact(connection, size))


def request(connection, kind, message=""):
    data = message.encode("utf-8")
    connection.sendall(HEADER.pack(b"i3-ipc", len(data), kind) + data)
    actual, reply = receive(connection)
    if actual != kind:
        raise RuntimeError("Unexpected Sway IPC reply")
    return reply


def windows(node, managed_only=False):
    if node.get("shell") == "xdg_shell":
        if managed_only and (
                node.get("app_id") in EXEMPT_APP_IDS
                or node.get("scratchpad_state", "none") != "none"):
            return []
        return [node["id"]]
    return [ident for child in node.get("nodes", [])
            for ident in windows(child, managed_only)]


def workspaces(connection):
    tree = request(connection, 4)
    return [(output["name"], w) for output in tree["nodes"]
            for w in output.get("nodes", []) if w["type"] == "workspace"]


def snapshot(spaces):
    return {w["name"]: (output, w["num"], windows(w, managed_only=True))
            for output, w in spaces if w.get("num", -1) > 0}


def prefix(name):
    return re.match(r"[0-9]+", name)[0]


def destination(spaces, source):
    output, number, _ = spaces[source]
    occupied = {n for _, n, _ in spaces.values()}
    new = number + 1
    while new in occupied:
        new += 1
    prefixes = Counter(map(prefix, spaces))
    available = min(((n, prefix(name)) for name, (out, n, ids) in spaces.items()
                     if number < n < new and out == output and len(ids) < LIMIT
                     and prefixes[prefix(name)] == 1), default=None)
    if available is not None:
        return available[1]
    if new > MAX_WORKSPACE_NUMBER:
        new = 1
        while new in occupied:
            new += 1
    return str(new)


def successful(reply):
    return bool(reply) and all(item.get("success") for item in reply)


def warn(message):
    print(f"sway-workspace-limit: {message}", file=sys.stderr)


def install_rules(connection):
    exempt = "|".join(re.escape(app) for app in sorted(EXEMPT_APP_IDS))
    app = f' app_id="^(?!(?:{exempt})$)"' if exempt else ""
    reply = request(connection, 0, f'for_window [tiling shell="^xdg_shell$"{app}] '
                                  f"'mark --add {MARK}, unmark {MARK}'")
    if not successful(reply):
        raise RuntimeError(f"Could not install placement rules: {reply}")


def rule_variable(number):
    return f"${MARK}_{number}_full"


def sync_rules(connection, lock, registered, active, spaces):
    full, spare = set(), set()
    for name, (_, _, ids) in spaces.items():
        (full if len(ids) >= LIMIT else spare).add(prefix(name))
    full -= spare  # A rule must never float windows in an alias with room.
    new = full - registered
    if new:
        # Record rules before enabling them so a restart can clear stale flags.
        lock.write("".join(f"{number}\n" for number in sorted(new)))
        lock.flush()
        registered.update(new)
    commands = [f"set {rule_variable(n)} disable" for n in sorted(active - full)]
    for number in sorted(full - active):
        variable = rule_variable(number)
        # Keep the variable literal at registration. Sway expands it when the rule runs.
        commands.extend((f"set {variable} enable",
                         f'for_window [con_mark="^{MARK}$" tiling '
                         f'workspace="^{number}([^0-9]|$)"] floating ${variable}'))
    if commands:
        reply = request(connection, 0, "; ".join(commands))
        if not successful(reply):
            raise RuntimeError(f"Could not update placement rules: {reply}")
    active.clear()
    active.update(full)


def workspace_match(name):
    return re.escape(name).replace('"', r'\"')


def move_command(ident, source, target, state):
    return (f'[con_id={ident} {state} workspace="^{workspace_match(source)}$"] '
            f"move --no-auto-back-and-forth container to workspace number {target}")


def place(connection, ident):
    for _ in range(2):
        tree = workspaces(connection)
        name = next((w["name"] for _, w in tree for node in w.get("floating_nodes", [])
                     if node["id"] == ident and windows(node, managed_only=True)
                     and w["name"] != "__i3_scratch"), None)
        if name is None:
            return
        spaces = snapshot(tree)
        tile = (f'[con_id={ident} floating workspace="^{workspace_match(name)}$"] '
                "floating disable")
        if name in spaces and len(spaces[name][2]) >= LIMIT:
            target = destination(spaces, name)
            move = move_command(ident, name, target, "floating")
            reply = request(connection, 0, f'{move}; [con_id={ident} floating '
                            f'workspace="^{target}([^0-9]|$)"] floating disable')
            if successful(reply):
                return
            # Restore tiling if Sway rejected the move and the window is still here.
        reply = request(connection, 0, tile)
        if successful(reply):
            return
    warn(f"Could not finish placing window {ident}: {reply}")


def enforce(connection, spaces, preferred):
    blocked = set()
    while True:
        for name, (_, _, ids) in spaces.items():
            if len(ids) > LIMIT:
                ident = max((i for i in ids if (name, i) not in blocked),
                            key=lambda i: (i in preferred, i), default=None)
                if ident is not None:
                    break
        else:
            return spaces
        target = destination(spaces, name)
        reply = request(connection, 0, move_command(ident, name, target, "tiling"))
        spaces = snapshot(workspaces(connection))
        if name in spaces and ident in spaces[name][2]:
            blocked.add((name, ident))
            warn(f"Could not move window {ident} from workspace {name!r}: {reply}")


def renumber(connection, spaces):
    if any(name != str(number) for name, (_, number, _) in spaces.items()):
        return spaces  # Leave custom-numbered workspace names untouched.
    numbered = sorted(number for _, number, _ in spaces.values())
    commands = [f"rename workspace {old} to {new}"
                for new, old in enumerate(numbered, 1) if old != new]
    if not commands:
        return spaces
    reply = request(connection, 0, "; ".join(commands))
    if not successful(reply):
        warn(f"Could not finish renumbering workspaces: {reply}")
    return snapshot(workspaces(connection))


def reconcile(connection, lock, registered, active, preferred=()):
    spaces = enforce(connection, snapshot(workspaces(connection)), preferred)
    sync_rules(connection, lock, registered, active, renumber(connection, spaces))


def main():
    if LIMIT < 1:
        raise ValueError("LIMIT must be at least 1")
    path = os.environ["SWAYSOCK"]
    with open(path + ".limit", "a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        lock.seek(0)
        registered = {line.strip() for line in lock if re.fullmatch(r"[0-9]+\n", line)}
        signal.signal(signal.SIGTERM, lambda *_: sys.exit())
        with (socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as command,
              socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as events):
            for connection in (command, events):
                connection.settimeout(3)
                connection.connect(path)
            if not request(events, 2, '["window","workspace","shutdown"]').get("success"):
                raise RuntimeError("Sway event subscription failed")
            events.settimeout(None)
            active = registered.copy()
            try:
                sync_rules(command, lock, registered, active, {})
                install_rules(command)
                reconcile(command, lock, registered, active)
                while True:
                    kind, event = receive(events)
                    if kind == 0x80000006:
                        return
                    change = event.get("change")
                    if kind == 0x80000000:
                        if change == "reload":
                            active.clear()
                            install_rules(command)
                        reconcile(command, lock, registered, active)
                    if kind == 0x80000003 and change in ("new", "close", "move", "floating"):
                        container = event["container"]
                        if change == "floating" and MARK in container.get("marks", []):
                            place(command, container["id"])
                        reconcile(command, lock, registered, active, windows(container))
            finally:
                try:
                    sync_rules(command, lock, registered, registered.copy(), {})
                except (OSError, EOFError, RuntimeError):
                    pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except (KeyError, OSError, ValueError, EOFError, RuntimeError) as error:
        sys.exit(f"sway-workspace-limit: {error}")
