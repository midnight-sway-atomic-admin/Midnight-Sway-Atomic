#!/usr/bin/env python3
"""Print the selected SVG path for Waybar's single-image module."""

import argparse
from pathlib import Path
import sys


def read(path):
    try:
        return path.read_text(encoding='ascii').strip()
    except OSError:
        return None


def select_icon(root=Path('/sys/class/power_supply'), battery_name=None):
    supplies = list(root.iterdir())
    batteries = [s for s in supplies if read(s / 'type') == 'Battery'
                 and read(s / 'scope') != 'Device' and read(s / 'present') != '0']
    if battery_name is not None:
        batteries = [s for s in batteries if s.name == battery_name]
    if len(batteries) != 1:
        raise ValueError('Expected one system battery; select it with --battery BAT0 if needed.')
    battery = batteries[0]

    # Mains adapters describe the laptop's external power. USB/PD adapters are
    # a fallback for machines that do not expose a Mains supply.
    mains, other = [], []
    for supply in supplies:
        if read(supply / 'scope') == 'Device':
            continue
        kind = read(supply / 'type') or ''
        if kind != 'Mains' and kind != 'Wireless' and not kind.startswith('USB'):
            continue
        online = read(supply / 'online')
        if online in ('0', '1', '2'):
            (mains if kind == 'Mains' else other).append(int(online) > 0)
    states = mains or other
    if states:
        plugged_in = any(states)
    else:
        status = read(battery / 'status')
        if status not in ('Charging', 'Discharging'):
            raise ValueError('No readable adapter online state; charger connection is ambiguous.')
        plugged_in = status == 'Charging'
    if plugged_in:
        return 'battery-charging.svg'

    capacity = read(battery / 'capacity')
    if capacity is None or not capacity.isdigit() or not 0 <= int(capacity) <= 100:
        raise ValueError('Battery capacity is missing or outside 0–100 percent.')
    return f'battery-{int(capacity)}.svg'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--battery', metavar='BAT0', help='system battery name, if more than one exists')
    args = parser.parse_args()
    try:
        icon = Path(__file__).resolve().parent / 'battery-icons' / select_icon(battery_name=args.battery)
        if not icon.is_file():
            raise ValueError(f'Icon is missing: {icon}')
        print(icon)
    except (OSError, ValueError) as error:
        print(f'battery-icons: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
