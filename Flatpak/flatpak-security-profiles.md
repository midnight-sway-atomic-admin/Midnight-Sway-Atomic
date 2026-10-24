# Flatpak security profiles

**Firefox · GIMP · Showtime**  
Fedora Sway Atomic / Wayland · Reviewed 24 October 2026

Apply all three audited profiles with one command block. This installs per-user permission overrides; the applications must already be installed.

| Application | Direct network | Direct GPU devices | Audio | Extra static host file access |
| :--- | :---: | :---: | :---: | :--- |
| Firefox | Allowed | Allowed | Allowed | None |
| GIMP | Denied | Denied | Denied | `~/gimp`, read/write |
| Showtime | Denied | Allowed | Allowed | None |

All three retain app-private storage and portal integration. They use Wayland and deny X11, shared host IPC, unrestricted D-Bus sockets, raw USB access and the other unnecessary permissions covered by the audit. Existing named session/system D-Bus grants are explicitly revoked, including inherited wildcard grants.

## Apply

Requires **Flatpak 1.16 or newer**, Bash, GNU file utilities and a working FileChooser portal. Close all three applications, then copy the entire block into a terminal as your normal desktop user. **Do not use `sudo`.**

Each app's current per-user override file is replaced. Global overrides, app data and portal decisions are left intact. Replacement is atomic for each app; the three-app sequence is not a single transaction. If a later step fails, earlier successful replacements remain applied.

```bash
bash <<'FLATPAK_POLICIES'
set -euo pipefail
umask 077

apps=(org.mozilla.firefox org.gimp.GIMP org.gnome.Showtime)

# Check that all three apps are installed before changing any override.
for app_id in "${apps[@]}"; do
  flatpak info --show-ref "$app_id" >/dev/null
done

common_policy=(
  --nofilesystem=host:reset
  --unshare=ipc
  --socket=wayland
  --nosocket=x11
  --nosocket=fallback-x11
  --nosocket=inherit-wayland-socket
  --nosocket=session-bus
  --nosocket=system-bus
  --nosocket=cups
  --nosocket=gpg-agent
  --nosocket=pcsc
  --nosocket=ssh-auth
  --nodevice=all
  --nodevice=kvm
  --nodevice=shm
  --nodevice=input
  --nodevice=usb
  --nousb=all
  --disallow=devel
  --disallow=multiarch
  --disallow=bluetooth
  --disallow=canbus
  --disallow=per-app-dev-shm
)

apply_policy() (
  app_id=$1
  policy=("${common_policy[@]}")

  case "$app_id" in
    org.mozilla.firefox)
      policy+=(
        --device=dri
        --share=network
        --socket=pulseaudio
        --no-talk-name=org.freedesktop.Notifications
        --no-talk-name=org.freedesktop.FileManager1
        --no-talk-name=org.a11y.Bus
        '--no-talk-name=org.gtk.vfs.*'
        --system-no-talk-name=org.freedesktop.NetworkManager
      )
      ;;
    org.gimp.GIMP)
      policy+=(
        --nodevice=dri
        --unshare=network
        --nosocket=pulseaudio
        --filesystem="$HOME/gimp:create"
        '--no-talk-name=org.gtk.vfs.*'
        --no-talk-name=org.freedesktop.FileManager1
        --no-talk-name=org.gnome.Shell.Screenshot
        --no-talk-name=org.kde.kwin.Screenshot
        --no-talk-name=com.canonical.AppMenu.Registrar
      )
      ;;
    org.gnome.Showtime)
      policy+=(
        --device=dri
        --unshare=network
        --socket=pulseaudio
        --no-talk-name=org.freedesktop.Notifications
      )
      ;;
  esac

  # Include inherited wildcard grants. A denial for one service does not
  # cancel a broader grant under a different D-Bus policy key.
  # The current override is included because --show-permissions omits denials;
  # those denials must survive when this file replaces the old override.
  effective_permissions=$(flatpak info --show-permissions "$app_id")
  current_overrides=$(flatpak override --user --show "$app_id")
  bus_scope=''
  while IFS= read -r line; do
    case "$line" in
      '[Session Bus Policy]') bus_scope='session' ;;
      '[System Bus Policy]') bus_scope='system' ;;
      '['*']') bus_scope='' ;;
      ''|'#'*) ;;
      *=*)
        bus_name=${line%%=*}
        case "$bus_scope" in
          session) policy+=("--no-talk-name=$bus_name") ;;
          system) policy+=("--system-no-talk-name=$bus_name") ;;
        esac
        ;;
    esac
  done <<< "$effective_permissions
$current_overrides"

  # Ask Flatpak to generate a fresh, validated override in a private staging
  # directory on the same filesystem. The live override is never reset first.
  flatpak_user_dir=${FLATPAK_USER_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/flatpak}
  case "$flatpak_user_dir" in
    /*) ;;
    *) printf 'Flatpak user directory must be an absolute path.\n' >&2; exit 1 ;;
  esac
  override_dir="$flatpak_user_dir/overrides"
  mkdir -p -- "$override_dir"
  stage_dir=$(mktemp -d "$override_dir/.${app_id}.XXXXXX")
  trap 'rm -rf -- "$stage_dir"' EXIT
  FLATPAK_USER_DIR="$stage_dir" flatpak override --user "${policy[@]}" "$app_id"
  test -s "$stage_dir/overrides/$app_id"

  # GNU mv uses a same-filesystem rename here: either the old or new complete
  # override remains in place. Any earlier error leaves the old file intact.
  mv -fT -- "$stage_dir/overrides/$app_id" "$override_dir/$app_id"
  printf 'Applied strict user policy for %s. Restart the application.\n' "$app_id"
)

for app_id in "${apps[@]}"; do
  apply_policy "$app_id"
done
FLATPAK_POLICIES
```

Reopen the applications after the block completes. Rerunning it reapplies the same policy choices. Rerun it after app updates or changes to inherited overrides so newly introduced D-Bus grants are included.

## Everyday use

- **Firefox:** use the file chooser for uploads and explicit **Save As** for downloads, or enable asking where to save. The host Downloads folder is not permanently shared.
- **GIMP:** put images in `~/gimp`; save and export there. Flatpak creates the folder on launch if necessary. Host GIMP configuration is no longer shared, so settings may initially appear fresh. Optional OpenCL and GPU-dependent plug-ins are outside this profile.
- **Showtime:** open local videos through its file chooser. External subtitles may require separate selection. Direct network streaming is disabled.

## Remaining access and trade-offs

- **Audio includes microphone access.** Flatpak's PulseAudio permission has no playback-only variant.
- **Portals remain available.** Previously granted document access is not revoked; the separate accessibility bus also remains available.
- **Firefox retains broad network access**, including reachable local services and abstract Unix sockets. These profiles do not provide destination filtering.
- **Firefox crash reporting, some profiling and desktop media controls can be affected** by removing development and explicit D-Bus ownership permissions.
- **Multiple installations or branches need separate review.** The installer inspects the instance that `flatpak info APP_ID` resolves. New permission types introduced by future Flatpak releases also need review.

## Verify

Inspect effective permissions, the stored overrides and existing portal grants:

```bash
for app_id in org.mozilla.firefox org.gimp.GIMP org.gnome.Showtime; do
  printf '\n%s\n' "$app_id"
  flatpak info --show-permissions "$app_id"
  flatpak override --user --show "$app_id"
  flatpak permission-show "$app_id"
  flatpak documents "$app_id"
done
```

Check Firefox browsing, sound, upload and Save As; GIMP opening, saving and exporting from `~/gimp`; and Showtime video selection, sound and seeking.

**Validation:** the separate profiles and this combined installer were checked with a real Flatpak 1.18.4 binary and local test packages carrying the upstream permission declarations. The combined installer produces equivalent overrides. No live Fedora/Sway application session was tested.

## Remove these overrides

```bash
flatpak override --user --reset org.mozilla.firefox
flatpak override --user --reset org.gimp.GIMP
flatpak override --user --reset org.gnome.Showtime
```

This restores permissions inherited from the installed apps and applicable global/system overrides. It does not recover earlier custom per-app overrides or change portal decisions.

## References

[Flatpak permissions](https://docs.flatpak.org/en/latest/sandbox-permissions.html) · [Command reference](https://docs.flatpak.org/en/latest/flatpak-command-reference.html) · [Permission-merging source](https://github.com/flatpak/flatpak/blob/1.18.4/common/flatpak-context.c)
