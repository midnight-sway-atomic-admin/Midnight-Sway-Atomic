# SDDM Rice 1.10 — Fedora Sway Atomic

A custom SDDM theme and greeter setup for **Fedora Sway Atomic**, including a fix for the post-login mouse-pointer flash.

It requires Fedora Sway Atomic's standard **Wayland/Sway SDDM setup with the Qt 6 greeter**.

No additional runtime packages are required.

## Installation

Extract the archive, then open a terminal in the extracted `sddm-rice` directory.

Run:

```bash
sudo python3 install.py
```

Then reboot when ready.

The installer does **not** restart SDDM or end your current session.

To check compatibility without installing anything:

```bash
sudo python3 install.py --check
```

> Replacing `Main.qml` alone is **not** sufficient to fix the post-login pointer flash. The greeter compositor configuration must also be installed.

## Uninstall / Restore

From the extracted `sddm-rice` directory, run:

```bash
sudo python3 uninstall.py
```

This restores the files saved before the **first installation made with these installers**, thereby undoing subsequent updates as well.

It removes only files added by those installations. If the theme already existed before the first install, that original theme is restored.

It does not reset Fedora or remove manually installed files outside the recorded installation history.

### Check without changing anything

```bash
sudo python3 uninstall.py --check
```

### List available installation backups

```bash
sudo python3 uninstall.py --list
```

### Restore to a particular backup

To return to the state immediately before a particular backup, pass its directory name or full path from the list:

```bash
sudo python3 uninstall.py --backup BACKUP-DIRECTORY
```

This undoes the selected installation and every newer active installation.

Without `--backup`, all active installs are undone.

Successfully restored backups are marked so that repeating the command does not reapply old backups.

### Older backup compatibility

The restore script supports backups created by versions **1.8** and **1.9**.

Those older backups did not record original ownership. For them, the script:

- Keeps each existing target file's current ownership
- Uses the saved copy's ownership if the target no longer exists

New backups record original ownership and permissions explicitly.

### Restore safety

Before restoring anything, the script saves the files it is about to change under:

```text
/var/lib/sddm/rice-restore-backups/
```

It prints the exact backup path before proceeding.

Unrelated files are preserved.

The restore process also restores SELinux labels and does not restart SDDM. Reboot when ready.

Keep `install.py` beside `uninstall.py`; the restore script reuses the installer's file-writing code.

## Cursor Fix

The installer reads the installed SDDM defaults and configuration in precedence order and verifies that the Wayland greeter uses:

```text
/usr/libexec/sddm-compositor-sway
```

It then installs a fully transparent Xcursor theme under the SDDM user's home directory and appends:

```text
seat * xcursor_theme sddm-rice-invisible 24
```

to:

```text
/etc/sway/sddm-greeter.config
```

The compositor's pointer therefore remains transparent after the greeter window closes.

This fix does **not** depend on:

- Mouse movement
- An idle timeout
- A background process

Xcursor is the cursor-image format used by Sway on Wayland.

### Configuration checks

Other greeter configurations are rejected before any files are written.

If this happens, report the compositor command displayed by the installer so the fix can be adapted to that setup.

The installer also stops if a higher-priority SDDM configuration would override its settings. The error identifies the files that need to be checked.

### Scope of the fix

The cursor fix targets the mouse pointer in:

- SDDM
- The SDDM greeter compositor
- The interval after the login window closes

The logged-in desktop and boot console use separate cursor controls.

The text insertion caret inside the login fields is retained.

## Other Corrections

The theme also includes the following fixes and behavior changes:

- Raw PAM messages are not displayed.
- Both fields are disabled while authentication is pending.
- A failed login clears the password, restores focus, and displays exactly `Authentication failure`.
- Repeated failure signals or PAM messages cannot duplicate the failure message.
- Successful login clears the password field.
- Password characters are masked immediately.
- Input-method prediction is disabled.
- Holding `Enter` or `Ctrl+1` through `Ctrl+9` cannot submit repeated login attempts.
- `Enter` does not interrupt an input method while it is composing text.
- Invalid remembered session indexes fall back to the first available session.
- An empty session list produces an error rather than an invalid login request.
- Status messages are rendered as plain text in a fixed-height area.
- The unused `SddmComponents` import and duplicate cursor handler were removed.

## Controls

| Input | Action |
|---|---|
| `Enter` | Username → password → login |
| `Ctrl+1` through `Ctrl+9` | Same action as `Enter` |
| `Tab` / `Shift+Tab` | Switch fields |
| `Escape` in the password field | Clear the password |

The last valid desktop session remains selected.

There is no session chooser.

## Backups and Installed Files

The installer prints its backup directory under:

```text
/var/lib/sddm/rice-backups/
```

Existing files that are changed are copied there using their original absolute paths relative to the backup directory.

`new-files.txt` lists files that did not exist before installation.

Use `uninstall.py` to restore them.

Keep the backup directories if you want the ability to undo an installation.

### Files installed or modified

```text
/var/lib/sddm/themes/sddm-rice/Main.qml
/var/lib/sddm/themes/sddm-rice/metadata.desktop
/etc/sddm.conf.d/99-sddm-rice.conf
/var/lib/sddm/.icons/sddm-rice-invisible/
/etc/sway/sddm-greeter.config
```

Existing settings in `/etc/sway/sddm-greeter.config` are retained.

The installer restores SELinux labels.

It does **not**:

- Change your personal Sway configuration
- Switch display servers
- Change the system's default target

## Validation

The theme was loaded and exercised in **Qt 6.11.2** using simulated SDDM objects.

Testing covered:

- Keyboard navigation
- Login shortcuts
- Key-repeat suppression
- Password masking
- Pending authentication
- Informational messages
- Failure, retry, and success flows
- Missing sessions
- Transparent pointer behavior over the background and fields

The generated cursor files were decoded with `libXcursor` at several requested sizes and verified to contain only transparent pixels.

Installer and restore tests covered:

- SDDM configuration precedence
- Backup creation
- Successive updates
- Earlier backup formats
- Repeated restores
- Rollback behavior

A real SDDM-to-desktop transition on your machine has **not** been tested here.

## References

- [SDDM closes its greeter window on login success](https://github.com/sddm/sddm/blob/v0.21.0/src/greeter/GreeterApp.cpp)
- [Fedora Sway greeter configuration and wrapper](https://gitlab.com/fedora/sigs/sway/sway-config-fedora/-/tree/0.4.3/sddm)
- [Sway cursor-theme configuration](https://github.com/swaywm/sway/blob/1.11/sway/sway-input.5.scd)
