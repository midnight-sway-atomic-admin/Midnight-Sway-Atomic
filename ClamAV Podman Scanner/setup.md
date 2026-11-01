# ClamAV Podman Scanner

A small rootless Podman container for scanning untrusted files with ClamAV.

The ClamAV database is downloaded when the image is built. The scanning container itself runs without network access, Linux capabilities, or write access to the scanned files.

## Files

```text
~/.local/share/clamav-container/
└── Containerfile

~/.local/bin/
└── clam-scan
```

Add this alias to your shell configuration (`~/.bashrc`):

```bash
alias a-fresh-clam='cd "$HOME/.local/share/clamav-container" && podman build --pull=always --no-cache -t localhost/clamav-monthly:44 . && podman image prune -f'
```

## Containerfile

`~/.local/share/clamav-container/Containerfile`

```Dockerfile
FROM registry.fedoraproject.org/fedora:44

# Update Fedora, install ClamAV without weak dependencies,
# clean package metadata, and bake current signatures into the image.
RUN dnf -y upgrade \
 && dnf -y --setopt=install_weak_deps=False install clamav \
 && dnf clean all \
 && freshclam

WORKDIR /scan

# Harmless default when run without an explicit command.
CMD ["clamscan", "--version"]
```

## Build

Build the container image:

```bash
cd "$HOME/.local/share/clamav-container"
podman build --pull=always --no-cache -t localhost/clamav-monthly:44 .
```

This fetches the current Fedora 44 base image, rebuilds every layer, installs the current Fedora ClamAV packages, and downloads current ClamAV signatures.

## Scanner

`~/.local/bin/clam-scan`

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
  -v "/home/suspicious-files:/scan:ro,Z" \
  -w /scan \
  localhost/clamav-monthly:44 \
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
- sees `/home/suspicious-files` read-only;
- has only `/tmp` as writable temporary storage.

Assuming `~/.local/bin` is in `PATH`, run:

```bash
clam-scan
```

Additional `clamscan` options can be appended:

```bash
clam-scan --verbose
```

## Refreshing ClamAV

Run:

```bash
a-fresh-clam
```

The alias fetches the current Fedora 44 base image, rebuilds without cached layers, updates Fedora packages, downloads current ClamAV signatures, replaces `localhost/clamav-monthly:44`, and removes dangling Podman images.

`podman image prune -f` removes all dangling images in the user's Podman storage, not only old ClamAV images.

## Usage

Place files to inspect under:

```text
/home/suspicious-files/
```

Then run:

```bash
clam-scan
```

The files are exposed to ClamAV read-only, and the scanning container has no network access.
