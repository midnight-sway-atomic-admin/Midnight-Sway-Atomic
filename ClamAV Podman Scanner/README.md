# ClamAV Podman Scanner

A small rootless Podman container for scanning untrusted files with ClamAV.

The ClamAV signatures are downloaded when the image is built. The scanning container itself runs without network access, Linux capabilities, or write access to the scanned files.

## Files

```text
~/.local/share/clamav-container/
└── Containerfile

~/.local/bin/
└── clam-scan
```

Add this alias to your shell configuration (`~/.bashrc`):

```bash
alias a-fresh-clam='cd "$HOME/.local/share/clamav-container" && podman build --pull=always --no-cache -t localhost/clamav-monthly:45 . && podman image prune -f'
```

## Containerfile

Save as:

```text
~/.local/share/clamav-container/Containerfile
```

```Dockerfile
FROM registry.fedoraproject.org/fedora:45

# Update Fedora and install the scanner and signature updater.
RUN dnf -y upgrade \
 && dnf -y --setopt=install_weak_deps=False install clamav clamav-freshclam \
 && dnf clean all

# Download current virus signatures into the image.
RUN freshclam

WORKDIR /scan

# Harmless default when run without an explicit command.
CMD ["clamscan", "--version"]
```

`clamav-freshclam` is installed explicitly because `freshclam` is provided by that package and is not installed by the above `clamav` command when weak dependencies are disabled.

## Build

Build the image:

```bash
cd "$HOME/.local/share/clamav-container"
podman build --pull=always --no-cache -t localhost/clamav-monthly:45 .
```

This:

1. fetches the current Fedora 45 base image;
2. updates its packages;
3. installs `clamav` and `clamav-freshclam`;
4. downloads current ClamAV signatures;
5. creates `localhost/clamav-monthly:45`.

Verify the image exists:

```bash
podman image exists localhost/clamav-monthly:45
printf 'exit status: %s\n' "$?"
```

A successful build should report:

```text
exit status: 0
```

## Scanner

Save as:

```text
~/.local/bin/clam-scan
```

```bash
#!/usr/bin/env bash
set -euo pipefail

exec podman run --rm \
  --pull=never \
  --network=none \
  --no-hosts \
  --no-hostname \
  --userns=keep-id \
  --cap-drop=all \
  --security-opt=no-new-privileges \
  --read-only \
  --read-only-tmpfs=false \
  --tmpfs /tmp:rw,nosuid,nodev,noexec,size=2g \
  -v "$HOME/suspicious-files:/scan:ro,Z" \
  -w /scan \
  localhost/clamav-monthly:45 \
  clamscan --recursive --infected --cross-fs=no "$@"
```

Make it executable:

```bash
chmod +x "$HOME/.local/bin/clam-scan"
```

The container:

- has no network access;
- runs with the invoking user's UID;
- has no Linux capabilities;
- cannot gain additional privileges;
- has a read-only root filesystem;
- sees `$HOME/suspicious-files` read-only at `/scan`;
- has only `/tmp` as writable temporary storage.

## Usage

Create the scan directory if needed:

```bash
mkdir -p "$HOME/suspicious-files"
```

Place files to inspect there, then run:

```bash
clam-scan
```

Additional `clamscan` options can be appended:

```bash
clam-scan --verbose
```

Inside the container, `$HOME/suspicious-files` appears as `/scan`.

## Refreshing ClamAV

After adding the alias to `~/.bashrc`, reload the shell configuration:

```bash
source "$HOME/.bashrc"
```

Then rebuild the image with current Fedora packages and current ClamAV signatures:

```bash
a-fresh-clam
```

The alias runs:

```bash
alias a-fresh-clam='cd "$HOME/.local/share/clamav-container" && podman build --pull=always --no-cache -t localhost/clamav-monthly:45 . && podman image prune -f'
```

`podman image prune -f` removes all dangling images in the user's Podman storage, not only old ClamAV images.
