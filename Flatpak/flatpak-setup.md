# Flatpak setup

Install Firefox, GIMP and Showtime from Flathub's verified-only selection for the current user only.

Flatpak is already included in Fedora Sway Atomic. Run these commands as the intended user, **without `sudo`**.

## Set up and install

For a new user-level Flathub repository:

```bash
flatpak remote-add --user --if-not-exists --subset=verified flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub org.mozilla.firefox org.gimp.GIMP org.gnome.Showtime
```

The `--user` option applies to both the Flathub repository and the installed apps.

If a user-level Flathub repository already exists, apply the verified-only filter with:

```bash
flatpak remote-modify --user --subset=verified flathub
```

`--if-not-exists` doesn't change an existing repository. The filter restricts this user-level Flathub repository; it doesn't remove previously installed unverified apps or change other repositories.

## Remove the default Firefox

After installing the Flatpak version, remove Fedora Sway Atomic's image-provided Firefox from the active deployment:

```bash
sudo rpm-ostree override remove firefox firefox-langpacks
```

Reboot to enter the new deployment:

```bash
systemctl reboot
```

This removes Firefox and its language-pack package from the deployed system. Because they are part of the Fedora base image, `rpm-ostree` implements this as a base-package override rather than modifying the underlying OSTree image itself.

## Update and clean up

Update first, then remove runtimes and extensions that installed apps no longer need:

```bash
flatpak update --user
flatpak uninstall --user --unused
```

Review the proposed removals before confirming. Run this after updates or app removals as needed. Flatpak keeps runtime versions still required by installed apps, even when newer versions are also installed.

Pinned runtimes are retained even when unused. To list pins:

```bash
flatpak pin --user
```

If a listed pin is no longer intentional, replace `PATTERN` below with that exact listed pattern, keeping the quotes, then repeat cleanup:

```bash
flatpak pin --user --remove 'PATTERN'
flatpak uninstall --user --unused
```

Cleanup doesn't choose which apps you still want or delete their saved data. Runtimes contain bundles of libraries; Flatpak removes unused runtimes, not individual unused libraries inside a required runtime.

These cleanup commands cover your user installation. If you also have system-wide Flatpaks, an administrator can clean their unused dependencies separately:

```bash
sudo flatpak uninstall --system --unused
```
