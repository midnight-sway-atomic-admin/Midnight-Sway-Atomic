# USB whitelist

For a fresh Fedora Sway Atomic installation. USB stays blocked by default; you choose which devices to allow. The whitelist is `/etc/udev/rules.d/70-usb-whitelist.rules`, owned by root and edited with `sudo`. No custom script is needed.

Before rebooting, allow any USB keyboard, mouse and non-root hubs needed to log in. Devices needed earlier to boot or unlock an encrypted disk require separate initramfs configuration; this guide doesn't configure that.

## 1. List attached devices

```bash
lsusb
lsusb -t
```

To see each non-root device's current sysfs name, USB ID and authorization state:

```bash
for d in /sys/bus/usb/devices/[0-9]*; do
    [ -f "$d/idVendor" ] || continue
    printf '%s %s:%s authorized=%s\n' "${d##*/}" \
        "$(cat "$d/idVendor")" "$(cat "$d/idProduct")" \
        "$(cat "$d/authorized")"
done
```

For example, `1-4 8087:0032 authorized=1` identifies device `1-4`, vendor `8087`, product `0032`. `1` means authorized; `0` means blocked. Use your own current values, not the example. Root hubs don't need whitelist entries. An allowed device behind a non-root hub also needs that hub allowed.

## 2. Create your whitelist

Run the first command **once**, on the fresh installation; it creates an empty whitelist. Then edit it:

```bash
sudo install -Dm0644 /dev/null /etc/udev/rules.d/70-usb-whitelist.rules
sudoedit /etc/udev/rules.d/70-usb-whitelist.rules
```

Add one line per device ID you want to allow. This example allows an Intel AX210; replace both IDs for other hardware:

```udev
ACTION=="add", SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="8087", ATTR{idProduct}=="0032", ATTR{authorized}="1"
```

Check the file and load it. Continue only if verification succeeds:

```bash
sudo udevadm verify /etc/udev/rules.d/70-usb-whitelist.rules &&
    sudo udevadm control --reload-rules
```

## 3. Block USB by default

```bash
sudo rpm-ostree kargs --append-if-missing=usbcore.authorized_default=0
sudo systemctl reboot
```

After reboot, each value below should be `0`:

```bash
cat /sys/bus/usb/devices/usb*/authorized_default
```

Repeat step 1 and test the devices you allowed. For Bluetooth, `bluetoothctl show` should display a controller if its normal service is running.

## 4. Add a device later

Connect it, repeat step 1, and identify its current sysfs name and USB ID. Edit the whitelist and add its rule:

```bash
sudoedit /etc/udev/rules.d/70-usb-whitelist.rules
sudo udevadm verify /etc/udev/rules.d/70-usb-whitelist.rules &&
    sudo udevadm control --reload-rules
```

Continue only if verification succeeds. Reconnect the device, or authorize just that attached device now. Replace `1-4` with its current sysfs name:

```bash
echo 1 | sudo tee /sys/bus/usb/devices/1-4/authorized
```

The rule allows matching devices on future connections and boots. For **one-time access**, skip the whitelist edit and use only the authorization command; access ends on disconnection or reboot, provided no whitelist rule allows the device.

## 5. Remove a device

Safely unmount storage first, including storage attached through a hub you're blocking. Delete the corresponding line from the whitelist, verify and reload:

```bash
sudoedit /etc/udev/rules.d/70-usb-whitelist.rules
sudo udevadm verify /etc/udev/rules.d/70-usb-whitelist.rules &&
    sudo udevadm control --reload-rules
```

Continue only if verification succeeds. If the device is still connected, repeat step 1 to find its current sysfs name, then block it immediately. Replace `1-4` below:

```bash
echo 0 | sudo tee /sys/bus/usb/devices/1-4/authorized
```

Deleting a rule alone doesn't disconnect an already authorized device. After removal and blocking, it stays blocked on reconnection unless another rule allows it. No command here enables all USB devices at once.

## Limits

This simple whitelist matches vendor/product IDs, not unique physical devices: identical or spoofed IDs also match. It doesn't scan files, cut port power or prevent initial USB enumeration. Keep the default blocked; authorize only devices you intend to use.

## References

- [Linux USB authorization](https://docs.kernel.org/usb/authorization.html)
- [Udev rules](https://www.freedesktop.org/software/systemd/man/latest/udev.html)
- [Udev rule verification and reloading](https://www.freedesktop.org/software/systemd/man/latest/udevadm.html)
