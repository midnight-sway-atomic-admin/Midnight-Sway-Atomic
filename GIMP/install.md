# Install the Midnight GIMP Theme

Place `midnight-gimp-theme.zip` in your `downloads` folder.

## 1. Extract the theme

```bash
cd ~/downloads
unzip -o midnight-gimp-theme.zip
```

Use `~/Downloads` instead if your folder name is capitalized.

## 2. Install the theme

Close GIMP first. With the included [Flatpak security profile](../Flatpak/flatpak-security-profiles.md#gimp), use GIMP's private configuration directory:

```bash
mkdir -p ~/.var/app/org.gimp.GIMP/config/GIMP/3.2/themes
cp -a midnight-gimp-theme ~/.var/app/org.gimp.GIMP/config/GIMP/3.2/themes/
```

If you haven't applied that profile and still use Flathub's default `xdg-config/GIMP` permission, use `~/.config/GIMP/3.2/themes/` instead. That permission shares the host configuration with GIMP; the included security profile removes it.

Reopen GIMP and select **midnight-gimp-theme** in **Edit → Preferences → Interface → Theme**, using the dark color scheme.

