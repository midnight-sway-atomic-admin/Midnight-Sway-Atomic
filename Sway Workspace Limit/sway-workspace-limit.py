#!/usr/bin/python3
import fcntl
import json
import os
import signal
import socket
import struct
import sys

LIMIT = 2
MARK = "_sway_workspace_limit"
HEADER = struct.Struct("=6sII")


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


def windows(node):
    if node.get("shell") == "xdg_shell":
        return [node["id"]]
    return [ident for child in node.get("nodes", []) for ident in windows(child)]


def workspaces(connection):
    tree = request(connection, 4)
    return [(output["name"], w) for output in tree["nodes"]
            for w in output.get("nodes", []) if w["type"] == "workspace"]


def snapshot(connection, spaces=None):
    if spaces is None:
        spaces = workspaces(connection)
    return {w["num"]: (output, windows(w)) for output, w in spaces
            if w.get("num", -1) > 0}


def destination(spaces, number):
    output = spaces[number][0]
    while number in spaces and (spaces[number][0] != output
                                or len(spaces[number][1]) >= LIMIT):
        number += 1
    return number


def install_rules(connection):
    reply = request(connection, 0,
                    f"for_window [tiling] 'mark --add {MARK}, unmark {MARK}'")
    if not all(item.get("success") for item in reply):
        raise RuntimeError(f"Could not install placement rules: {reply}")


def sync_rules(connection, known, spaces):
    commands, changed = [], {}
    for number in spaces.keys() | known.keys():
        full = number in spaces and len(spaces[number][1]) >= LIMIT
        if known.get(number) == full or number not in known and not full:
            continue
        variable = f"${MARK}_{number}_full"
        commands.append(f"set {variable} {'enable' if full else 'disable'}")
        if number not in known:
            commands.append(f'for_window [con_mark="^{MARK}$" tiling '
                            f'workspace="^0*{number}([^0-9]|$)"] floating ${variable}')
        changed[number] = full
    if commands:
        reply = request(connection, 0, "; ".join(commands))
        if not all(item.get("success") for item in reply):
            raise RuntimeError(f"Could not update placement rules: {reply}")
        known.update(changed)


def place(connection, ident):
    spaces = workspaces(connection)
    source = next((w for _, w in spaces for node in w.get("floating_nodes", [])
                   if ident in windows(node)), None)
    if source is None or source["name"] == "__i3_scratch":
        return
    number = source.get("num", -1)
    target = destination(snapshot(connection, spaces), number) if number > 0 else number
    move = (f"move --no-auto-back-and-forth container to workspace number {target}; "
            f'[con_id={ident} workspace="^0*{target}([^0-9]|$)"] ' if target != number else "")
    reply = request(connection, 0, f"[con_id={ident}] {move}floating disable")
    if any(ident in windows(node) for _, w in workspaces(connection)
           if w["name"] != "__i3_scratch" for node in w.get("floating_nodes", [])):
        raise RuntimeError(f"Window placement failed or was reversed: {reply}")


def enforce(connection, preferred=()):
    spaces = snapshot(connection)
    while True:
        full = next(((n, ids) for n, (_, ids) in spaces.items()
                     if len(ids) > LIMIT), None)
        if full is None:
            return spaces
        number, ids = full
        ident = max(ids, key=lambda i: (i in preferred, i))
        target = destination(spaces, number)
        move = request(connection, 0, f"[con_id={ident}] move --no-auto-back-and-forth "
                       f"container to workspace number {target}")
        spaces = snapshot(connection)
        if ident in spaces.get(number, (None, ()))[1]:
            raise RuntimeError(f"Window move failed or was reversed: {move}")


def main():
    if LIMIT < 1:
        raise ValueError("LIMIT must be at least 1")
    with open(os.environ["SWAYSOCK"] + ".limit", "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        signal.signal(signal.SIGTERM, lambda *_: sys.exit())
        with (socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as command,
              socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as events):
            for connection in (command, events):
                connection.settimeout(3)
                connection.connect(os.environ["SWAYSOCK"])
            if not request(events, 2, '["window","workspace","shutdown"]').get("success"):
                raise RuntimeError("Sway event subscription failed")
            events.settimeout(None)
            known = {}
            install_rules(command)
            sync_rules(command, known, enforce(command))
            while True:
                kind, event = receive(events)
                if kind == 0x80000006:
                    return
                change = event.get("change")
                if kind == 0x80000000:
                    if change == "reload":
                        known.clear()
                        install_rules(command)
                    sync_rules(command, known, enforce(command))
                if kind == 0x80000003 and change in ("new", "close", "move", "floating"):
                    if change == "floating" and MARK in event["container"].get("marks", []):
                        place(command, event["container"]["id"])
                    sync_rules(command, known, enforce(command, windows(event["container"])))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except (KeyError, OSError, ValueError, EOFError, RuntimeError) as error:
        sys.exit(f"sway-workspace-limit: {error}")
