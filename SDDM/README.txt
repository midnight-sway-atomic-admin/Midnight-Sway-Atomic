SDDM RICE 1.10 — FEDORA SWAY ATOMIC

Requires Fedora Sway Atomic's standard Wayland/Sway SDDM setup with the Qt 6 greeter. 
No additional runtime packages are needed.

INSTALL

Extract the archive. Open a terminal in the extracted sddm-rice directory.
Run this from an administrator account:

    sudo python3 install.py

Then reboot when ready. The installer does not restart SDDM or end your session.
An optional check without installation is:

    sudo python3 install.py --check

Replacing Main.qml alone is NOT enough to fix the post-login pointer flash.
The greeter compositor configuration must also be installed.

UNINSTALL / RESTORE

From the extracted sddm-rice directory, run:

    sudo python3 uninstall.py

This restores the files saved before the first installation made with these
installers, undoing subsequent updates as well. It removes only files that those
installs added. A theme that already existed before the first install is restored.
It does not reset Fedora or remove manually installed files outside that history.

Check without changing anything:

    sudo python3 uninstall.py --check

List the installation backups still available to undo:

    sudo python3 uninstall.py --list

To return to the setup just before a particular backup, pass its directory name
or full path from that list:

    sudo python3 uninstall.py --backup BACKUP-DIRECTORY

That command undoes the selected installation and every newer active install.
Without --backup, all active installs are undone. Successfully restored backups
are marked so that repeating the command does not apply old backups again.

The script supports backups from versions 1.8 and 1.9. Those older backups did
not record original ownership; for them it keeps each existing file's current
ownership, using the saved copy's ownership if the target no longer exists.
New backups record original ownership and permissions explicitly.

Before restoring, the script saves the files it will change under
/var/lib/sddm/rice-restore-backups/ and prints the path. Unrelated files are kept.
It restores SELinux labels and does not restart SDDM. Reboot when ready.
Keep install.py beside uninstall.py; the restore script reuses its file writer.

CURSOR FIX

The installer reads the installed SDDM defaults and configuration in precedence
order and verifies that the Wayland greeter uses /usr/libexec/sddm-compositor-sway.

It installs a fully transparent Xcursor theme under the SDDM user's home and
appends this setting to /etc/sway/sddm-greeter.config:

    seat * xcursor_theme sddm-rice-invisible 24

The compositor's pointer remains transparent after the greeter window closes.
This does not depend on mouse motion, an idle timeout, or a background process.
Xcursor is the cursor-image format used by Sway on Wayland.

Other greeter configurations are rejected before any writes.
If that happens, report the displayed compositor command so the fix can be
adapted to it. The installer also stops if a higher-priority SDDM configuration
would override its settings; the error identifies the files to check.

This fix targets the mouse pointer in SDDM and its greeter compositor, including
the interval after the login window closes. The logged-in desktop and the boot
console have separate cursor controls. The text insertion caret in the login
fields is retained.

OTHER CORRECTIONS

- Raw PAM messages are not displayed in the theme.
- Both fields are disabled while authentication is pending. A failed login
  clears the password, restores focus, and shows exactly "Authentication failure".
  Repeated failure signals or PAM messages cannot duplicate that text.
- Successful login clears the password field.
- Password characters are masked immediately; input-method prediction is disabled.
- Holding Enter or Ctrl+1 through Ctrl+9 cannot submit repeated login attempts.
- Enter does not interrupt an input method while it is composing text.
- Invalid remembered session indexes fall back to the first available session;
  an empty session list produces an error instead of an invalid login request.
- Status messages are rendered as plain text in a fixed-height area.
- Removed the unused SddmComponents import and duplicate cursor handler.

CONTROLS

Enter: username -> password -> login.
Ctrl+1 through Ctrl+9: same action as Enter.
Tab / Shift+Tab: switch fields.
Escape in the password field: clear it.
The last valid desktop session remains selected; there is no session chooser.

BACKUPS AND FILES

The installer prints its backup directory under /var/lib/sddm/rice-backups/.
Existing changed files are copied there with their original absolute paths
relative to that directory. new-files.txt lists files that did not exist before.
Use uninstall.py to restore them. Keep the backups if you want to undo an install.

Files installed:
    /var/lib/sddm/themes/sddm-rice/Main.qml
    /var/lib/sddm/themes/sddm-rice/metadata.desktop
    /etc/sddm.conf.d/99-sddm-rice.conf
    /var/lib/sddm/.icons/sddm-rice-invisible/
    /etc/sway/sddm-greeter.config (existing settings retained)

The installer restores SELinux labels. It does not change your personal Sway
configuration, switch display servers, or change the system's default target.

VALIDATION

The theme was loaded and exercised in Qt 6.11.2 with simulated SDDM objects:
keyboard navigation, shortcuts, repeat suppression, password masking, pending
authentication, informational messages, failure/retry/success, missing sessions,
and the blank pointer over the background and fields. Cursor files were decoded
by libXcursor at several requested sizes and verified to contain only transparent
pixels. Installer and restore checks cover configuration precedence, backups,
successive updates, earlier backup formats, repeated restores, and rollback.

A real SDDM-to-desktop transition on your machine has not been tested here.

REFERENCES

SDDM closes its greeter window on login success:
https://github.com/sddm/sddm/blob/v0.21.0/src/greeter/GreeterApp.cpp

Fedora's Sway greeter configuration and wrapper:
https://gitlab.com/fedora/sigs/sway/sway-config-fedora/-/tree/0.4.3/sddm

Sway cursor-theme configuration:
https://github.com/swaywm/sway/blob/1.11/sway/sway-input.5.scd
