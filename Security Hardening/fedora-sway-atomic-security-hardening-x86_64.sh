#!/usr/bin/env bash
# Fedora Sway Atomic — host hardening for an x86-64 desktop
#
# Purpose:
#   1. Install persistent sysctl hardening under /etc/sysctl.d/.
#   2. Stage persistent rpm-ostree kernel arguments, including
#      lockdown=confidentiality.
#   3. Suppress systemd-coredump storage and processing of application dumps.
#      Force SMT off and disable 32-bit Linux execution after reboot.
#
# Strict, opt-in policy for x86-64 Fedora Sway Atomic systems using the latest
# stock Fedora kernel. Intel and AMD IOMMU options follow the running CPU vendor.
# Firmware must expose a working IOMMU; kernel arguments cannot create one.
# This is not a compatibility guarantee for every x86-64 machine or application.
# It does NOT disable unprivileged user namespaces because Flatpak/bubblewrap
# relies on them for sandbox construction.
#
# Run:
#   bash fedora-sway-atomic-security-hardening-x86_64.sh --help
#   sudo bash fedora-sway-atomic-security-hardening-x86_64.sh
#
# Reboot after it completes. Some runtime sysctls set here are deliberately
# one-way until reboot (notably ptrace_scope=3, unprivileged_bpf_disabled,
# and kexec_load_disabled).

set -euo pipefail

SYSCTL_FILE="/etc/sysctl.d/99-zz-security-hardening.conf"
SYSTEMD_SYSCTL="/usr/lib/systemd/systemd-sysctl"
COREDUMP_FILE="/etc/systemd/coredump.conf.d/99-zz-security-hardening.conf"

die() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

show_policy() {
    cat <<'POLICY'
Fedora Sway Atomic: strict x86-64 host hardening

Usage:
  sudo bash fedora-sway-atomic-security-hardening-x86_64.sh
  bash fedora-sway-atomic-security-hardening-x86_64.sh --help

Requires Fedora Atomic, an x86-64 kernel >= 6.12, rpm-ostree, lockdown support,
the required sysctls, and systemd-sysctl with --strict. Requires a reboot.
Intended for the latest stock Fedora kernel; checks use the running kernel.

Compatibility consequences of this opt-in policy:
  - Disables SMT on CPUs that support it; CPU throughput may decrease.
  - Disables 32-bit Linux execution, including affected games and Wine/Proton
    components. Containers and Flatpak do not bypass this host restriction.
  - Blocks new io_uring instances for all users, including root.
  - Disables ptrace debugging and restricts crash diagnostics and profiling.
  - Requires trusted signatures on kernel modules, including third-party GPU,
    virtualisation and filesystem modules. Unsigned modules will not load.
  - Enables confidentiality lockdown and disables debugfs; hardware utilities
    and hibernation may stop working. Lockdown does not require Secure Boot,
    and does not provide Secure Boot's protection of the boot chain.
  - Requests strict IOMMU translation; firmware/driver limitations can prevent
    protection or cause compatibility problems. Verify after reboot.
  - Enforces CPU mitigations and memory clearing, with performance costs.
  - Suppresses systemd core-dump storage/processing; existing dumps and
    application-specific crash reports are not removed.
  - Retains user namespaces for Flatpak.

Some sysctls take effect immediately and cannot be undone during that boot.
If applying the script fails partway through, changes may already be present.
Review the policy and keep a bootable previous deployment available.
POLICY
}

case "${1:-}" in
    --help|-h) show_policy; exit 0 ;;
    "") (( $# == 0 )) || die "unexpected arguments; use --help." ;;
    *) die "unexpected argument: $1; use --help." ;;
esac

[[ ${EUID} -eq 0 ]] || die "run this script as root (for example with sudo)."
[[ "$(uname -m)" == "x86_64" ]] || die "this script requires x86-64 Fedora Atomic."

# /etc/os-release is the operating system's own trusted identification file.
[[ -r /etc/os-release ]] || die "/etc/os-release is unavailable."
os_id="$(. /etc/os-release; printf '%s' "${ID:-}")"
[[ "${os_id}" == fedora ]] || die "this script requires Fedora."
[[ -e /run/ostree-booted ]] || die "this host was not booted as an OSTree deployment."

command -v rpm-ostree >/dev/null 2>&1 || die "rpm-ostree was not found; this script is intended for Fedora Atomic."
command -v sysctl >/dev/null 2>&1 || die "sysctl was not found."
[[ -x "${SYSTEMD_SYSCTL}" ]] || die "${SYSTEMD_SYSCTL} was not found or is not executable."
SYSTEMD_SYSCTL_HELP="$("${SYSTEMD_SYSCTL}" --help 2>&1)"
grep -q -- '--strict' <<<"${SYSTEMD_SYSCTL_HELP}" || \
    die "systemd-sysctl on this host lacks --strict; refusing to apply without reliable error reporting."

# Do not overwrite an unrelated administrator policy that happens to use the
# same filename. Re-running this script over its own prior revision is allowed.
if [[ -L "${SYSCTL_FILE}" ]] || { [[ -e "${SYSCTL_FILE}" ]] && \
   ! grep -qx '# Fedora Atomic host security hardening' "${SYSCTL_FILE}"; }; then
    die "${SYSCTL_FILE} already exists and was not created by this hardening script."
fi

# Protect unrelated administrator configuration, including dangling symlinks.
if [[ -L "${COREDUMP_FILE}" ]] || { [[ -e "${COREDUMP_FILE}" ]] && \
   ! grep -qx '# Fedora Atomic host security hardening' "${COREDUMP_FILE}"; }; then
    die "${COREDUMP_FILE} already exists and is not an owned regular configuration file."
fi

# Linux 6.12 provides both ia32_emulation and proc_mem.force_override.
# Reject older kernels rather than relying on an unverified backport.
kernel_release="$(uname -r)"
if [[ "${kernel_release}" =~ ^([0-9]+)\.([0-9]+) ]]; then
    kernel_major="${BASH_REMATCH[1]}"
    kernel_minor="${BASH_REMATCH[2]}"
    (( kernel_major > 6 || (kernel_major == 6 && kernel_minor >= 12) )) || \
        die "Linux 6.12 or newer is required for the complete boot-argument policy."
else
    die "cannot parse running kernel release: ${kernel_release}"
fi

# Fedora kernels expose this file when the lockdown LSM is available. Refuse to
# stage a lockdown policy if the running kernel cannot demonstrate support for
# the requested confidentiality mode.
if [[ ! -r /sys/kernel/security/lockdown ]]; then
    die "/sys/kernel/security/lockdown is unavailable; cannot verify kernel-lockdown support."
fi
if ! grep -qw 'confidentiality' /sys/kernel/security/lockdown; then
    die "the running kernel does not advertise lockdown=confidentiality support."
fi

umask 022
TMP_WORKDIR="$(mktemp -d)"
trap 'rm -rf -- "${TMP_WORKDIR}"' EXIT
TMP_SYSCTL="${TMP_WORKDIR}/sysctl.conf"
TMP_COREDUMP="${TMP_WORKDIR}/coredump.conf"

cat >"${TMP_SYSCTL}" <<'SYSCTL'
# Fedora Atomic host security hardening
# =====================================
# Intended for an x86-64 Fedora desktop. Applied at boot by systemd-sysctl.

# --- Kernel information exposure / process inspection ---

# Hide %pK kernel pointers even from otherwise privileged readers.
kernel.kptr_restrict = 2

# Require CAP_SYSLOG to read the kernel log buffer.
kernel.dmesg_restrict = 1

# Full userspace ASLR, including heap randomization.
kernel.randomize_va_space = 2

# Disable ptrace completely. Yama mode 3 blocks both PTRACE_ATTACH and
# PTRACE_TRACEME for all processes, including privileged ones. Once set to 3,
# this value cannot be lowered again until reboot.
kernel.yama.ptrace_scope = 3

# Strongest restriction whose semantics are documented by upstream Linux:
# unprivileged users may not profile the kernel. Upstream does not assign
# stronger semantics to values above 2.
kernel.perf_event_paranoid = 2

# Permanently disable unprivileged BPF for the current boot once this is set.
kernel.unprivileged_bpf_disabled = 1

# Harden the BPF JIT for all users.
net.core.bpf_jit_harden = 2

# Disable kexec loading for the remainder of the current boot.
kernel.kexec_load_disabled = 1

# Deny creation of new io_uring instances to all processes, including root.
# Value 2 has no CAP_SYS_ADMIN or group exemption. Existing rings remain usable.
kernel.io_uring_disabled = 2

# Prevent unprivileged requests from autoloading TTY line-discipline modules.
# A leading '-' tells systemd-sysctl to ignore the assignment if a future
# kernel removes the knob.
-dev.tty.ldisc_autoload = 0

# Require CAP_SYS_ADMIN for legacy TIOCSTI terminal-input injection when this
# runtime knob exists.
-dev.tty.legacy_tiocsti = 0

# --- Memory exploitation resistance ---

# Unprivileged userfaultfd callers may not handle kernel-mode page faults.
vm.unprivileged_userfaultfd = 0

# Prevent mappings of the first 64 KiB.
vm.mmap_min_addr = 65536

# x86-64 Fedora supports 32 bits of randomization for native mappings.
vm.mmap_rnd_bits = 32

# --- Filesystem / IPC protections ---

fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.protected_fifos = 2
fs.protected_regular = 2

# Do not produce useful core dumps for setuid/setgid or otherwise privileged
# programs.
fs.suid_dumpable = 0

# --- IPv4 network-stack hardening ---
# Explicit all/default assignments are paired with systemd-sysctl globs so
# existing interfaces as well as interfaces appearing later receive the same
# policy.

# Reject source-routed IPv4 packets.
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.conf.*.accept_source_route = 0

# Reject ICMP redirects.
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.*.accept_redirects = 0

# Do not accept even so-called secure redirects.
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.conf.*.secure_redirects = 0

# Do not generate redirects.
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.*.send_redirects = 0

# Ignore broadcast ICMP echo and malformed ICMP error responses.
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Keep SYN cookies available as overflow protection.
net.ipv4.tcp_syncookies = 1

# RFC 1337 mode retains TIME_WAIT state rather than killing it on an in-window
# RST; current Linux source implements this when the knob is enabled.
net.ipv4.tcp_rfc1337 = 1

# --- IPv6 network-stack hardening ---
# Keep IPv6 functional; do not disable Router Advertisements or SLAAC.

# Reject ICMPv6 redirects.
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0
net.ipv6.conf.*.accept_redirects = 0

# For IPv6, zero still permits Routing Header Type 2. A negative value is the
# documented setting that rejects routing extension headers entirely.
net.ipv6.conf.all.accept_source_route = -1
net.ipv6.conf.default.accept_source_route = -1
net.ipv6.conf.*.accept_source_route = -1
SYSCTL

# Verify that every non-glob, non-optional sysctl key exists on the running
# kernel before making any persistent or one-way runtime change.
missing=0
while IFS= read -r key; do
    if ! sysctl -N "${key}" >/dev/null 2>&1; then
        printf 'Unsupported required sysctl on this kernel: %s\n' "${key}" >&2
        missing=1
    fi
done < <(
    awk -F= '
        /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
        /^[[:space:]]*-/ { next }
        /\*/ { next }
        {
            key=$1
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", key)
            print key
        }
    ' "${TMP_SYSCTL}"
)
(( missing == 0 )) || die "one or more required sysctl keys are unavailable; no changes were made."

# --- Kernel command-line hardening ---
# rpm-ostree creates a new deployment; it does not rewrite the currently booted
# deployment. Existing values for the same key are replaced below.
kargs=(
    "lockdown=confidentiality"
    "module.sig_enforce=1"
    # Explicit application-wide mitigations, rather than per-thread opt-in.
    "spectre_v2=on"
    "spec_store_bypass_disable=on"
    # Disable SMT unconditionally and prevent runtime re-enabling.
    "nosmt=force"
    # Disable 32-bit programs and their syscall entry points.
    "ia32_emulation=0"
    "randomize_kstack_offset=on"
    "init_on_alloc=1"
    "init_on_free=1"
    "page_alloc.shuffle=1"
    "slab_nomerge"
    "debugfs=off"
    "iommu.strict=1"
    "iommu.passthrough=0"
    "pti=on"
    "vsyscall=none"
    "proc_mem.force_override=never"
)

# Select only the vendor-specific driver options applicable to this CPU.
# Intel needs explicit driver enablement where it is not the default. AMD's
# driver normally enables itself when supported by hardware and firmware.
# Unknown vendors retain the generic IOMMU requests, without an assurance of
# vendor-specific driver support. The same limitation applies inside VMs.
cpu_vendor="$(awk -F: '/^vendor_id[[:space:]]*:/ {
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2; exit
}' /proc/cpuinfo)"
case "${cpu_vendor}" in
    AuthenticAMD) kargs+=("amd_iommu=force_isolation") ;;
    GenuineIntel) kargs+=("intel_iommu=on") ;;
    *) printf 'Warning: CPU vendor %s has no vendor-specific IOMMU policy here.\n' \
           "${cpu_vendor:-unknown}" >&2 ;;
esac

current_kargs="$(rpm-ostree kargs)"
read -r -a current_tokens <<<"${current_kargs}"

# The kernel treats '-' and '_' alike in parameter names, but not values.
# Keep the original spelling for rpm-ostree deletions.
normalized_tokens=()
for token in "${current_tokens[@]}"; do
    token_key="${token%%=*}"
    token_key="${token_key//-/_}"
    if [[ "${token}" == *=* ]]; then
        normalized_tokens+=("${token_key}=${token#*=}")
    else
        normalized_tokens+=("${token_key}")
    fi
done

rpm_args=()
declare -A rpm_arg_seen=()

add_rpm_arg() {
    local arg="$1"
    if [[ -z "${rpm_arg_seen[${arg}]+x}" ]]; then
        rpm_args+=("${arg}")
        rpm_arg_seen["${arg}"]=1
    fi
}

# Remove conflicting aliases and explicit CPU-mitigation opt-outs. Individual
# vulnerability controls can override the global mitigations policy.
# IOMMU options may share one comma-separated argument: remove only the
# conflicting components, retaining any other options from that argument.
for i in "${!current_tokens[@]}"; do
    token="${current_tokens[i]}"
    case "${normalized_tokens[i]}" in
        iommu=*)
            IFS=, read -r -a iommu_options <<<"${token#*=}"
            kept_iommu_options=()
            iommu_conflict=0
            for option in "${iommu_options[@]}"; do
                case "${option}" in
                    pt|off|soft) iommu_conflict=1 ;;
                    *) kept_iommu_options+=("${option}") ;;
                esac
            done
            if (( iommu_conflict )); then
                add_rpm_arg "--delete-if-present=${token}"
                if (( ${#kept_iommu_options[@]} > 0 )); then
                    kept_iommu_value="$(IFS=,; printf '%s' "${kept_iommu_options[*]}")"
                    add_rpm_arg "--append-if-missing=iommu=${kept_iommu_value}"
                fi
            fi
            ;;
        nopti|slab_merge|slub_merge|\
        nospectre_v1|nospectre_v2|nospec_store_bypass_disable|\
        l1tf=off|mds=off|tsx_async_abort=off|mmio_stale_data=off|\
        retbleed=off|spec_rstack_overflow=off|srbds=off|\
        gather_data_sampling=off|reg_file_data_sampling=off|\
        spectre_bhi=off|spectre_v2_user=off|indirect_target_selection=off|\
        tsa=off|vmscape=off|kvm.nx_huge_pages=off)
            add_rpm_arg "--delete-if-present=${token}"
            ;;
    esac
done

# Normalize each managed key without touching an already-correct value. Only
# conflicting values for the same key are deleted, and a hardened value is
# appended only when it is absent. Unrelated kernel arguments are untouched.
for wanted in "${kargs[@]}"; do
    wanted_present=0
    if [[ "${wanted}" == *=* ]]; then
        key="${wanted%%=*}"
        for i in "${!current_tokens[@]}"; do
            token="${current_tokens[i]}"
            normalized_token="${normalized_tokens[i]}"
            if [[ "${normalized_token}" == "${wanted}" ]]; then
                wanted_present=1
            elif [[ "${normalized_token}" == "${key}="* || "${normalized_token}" == "${key}" ]]; then
                add_rpm_arg "--delete-if-present=${token}"
            fi
        done
    else
        for normalized_token in "${normalized_tokens[@]}"; do
            if [[ "${normalized_token}" == "${wanted}" ]]; then
                wanted_present=1
                break
            fi
        done
    fi

    if (( wanted_present == 0 )); then
        add_rpm_arg "--append-if-missing=${wanted}"
    fi
done

# Stage kernel arguments first. If rpm-ostree rejects the transaction, no
# persistent sysctl file and no one-way runtime sysctl have yet been changed.
show_policy
printf '\nDetected CPU vendor: %s\n\n' "${cpu_vendor:-unknown}"
if (( ${#rpm_args[@]} > 0 )); then
    echo "Staging hardened kernel arguments with rpm-ostree..."
    rpm-ostree kargs "${rpm_args[@]}"
else
    echo "Kernel arguments already match the requested hardening policy."
fi

# Install the sysctl policy only after the rpm-ostree transaction succeeds.
install -o root -g root -m 0644 "${TMP_SYSCTL}" "${SYSCTL_FILE}"

# Disable systemd-coredump storage AND processing. Storage=none by itself can
# still permit temporary disk writes during processing. This does not remove
# existing dumps or prevent applications from writing their own crash reports.
install -d -o root -g root -m 0755 "$(dirname "${COREDUMP_FILE}")"
cat >"${TMP_COREDUMP}" <<'COREDUMP'
# Fedora Atomic host security hardening
[Coredump]
Storage=none
ProcessSizeMax=0
COREDUMP
install -o root -g root -m 0644 "${TMP_COREDUMP}" "${COREDUMP_FILE}"

# Apply exactly this sysctl.d file with systemd-sysctl. This preserves its glob
# semantics and avoids `sysctl --system`, whose separate /etc/sysctl.conf pass
# can override sysctl.d values. --strict makes any failure on a required entry
# fatal; the two deliberately optional TTY entries are prefixed with '-'.
echo "Applying sysctl hardening..."
"${SYSTEMD_SYSCTL}" --strict "${SYSCTL_FILE}"

cat <<MESSAGE

Hardening configuration installed.

Persistent sysctl file:
  ${SYSCTL_FILE}
Persistent systemd-coredump configuration:
  ${COREDUMP_FILE}

A reboot is required before the staged kernel arguments take effect.

After reboot, verify:
  cat /sys/kernel/security/lockdown
  cat /proc/cmdline
  rpm-ostree kargs
  # If this CPU exposes SMT controls:
  cat /sys/devices/system/cpu/smt/control
  lscpu
  sudo dmesg | grep -Ei 'DMAR|IOMMU|AMD-Vi'
  # Nonempty groups are useful evidence, not proof of complete DMA protection:
  find /sys/kernel/iommu_groups/ -mindepth 1 -maxdepth 1 -type d
  systemd-analyze cat-config systemd/coredump.conf
  sysctl kernel.yama.ptrace_scope kernel.unprivileged_bpf_disabled \\
         kernel.io_uring_disabled kernel.kexec_load_disabled \\
         vm.unprivileged_userfaultfd net.ipv6.conf.all.accept_source_route

Expected lockdown state:
  [confidentiality]

Important compatibility consequences:
  - lockdown=confidentiality restricts kernel-memory and debug interfaces.
  - module.sig_enforce=1 rejects kernel modules without a trusted signature.
  - debugfs=off disables debugfs entirely.
  - nosmt=force disables SMT unconditionally where supported.
    The effect on logical CPU count depends on the processor topology.
    Throughput can fall; there is no fixed percentage performance penalty.
  - spectre_v2=on and spec_store_bypass_disable=on enforce CPU mitigations
    across applications, with a possible performance cost.
  - ia32_emulation=0 prevents running 32-bit Linux software, including
    affected games and compatibility components, even inside containers.
  - systemd-coredump no longer stores or processes application core dumps.
    Application-specific reports and existing dumps are not removed.
  - kernel.io_uring_disabled=2 disables creation of new io_uring rings for all processes.
  - kernel.yama.ptrace_scope=3 disables ptrace entirely until reboot.
  - proc_mem.force_override=never prevents /proc/PID/mem from overriding
    normal memory-page permissions.
  - vsyscall=none can break very old Linux binaries.
  - init_on_alloc=1 and init_on_free=1 have a measurable performance cost.
  - amd_iommu=force_isolation is added only on AMD x86-64 CPUs.
  - intel_iommu=on is added only on Intel x86-64 CPUs.
  - IOMMU requests require hardware, firmware and driver support. Their
    presence in /proc/cmdline alone does not establish active protection.

If the pending deployment fails to boot, select the previous OSTree deployment
from the boot menu. Each OSTree deployment has its own /etc; configuration changes are merged
into new deployments, so the previous deployment may have a different policy.
If you abandon this sysctl policy, remove ${SYSCTL_FILE} wherever it is
present in the deployment you intend to use, then reboot. Rebooting alone
will not undo settings that are reapplied from that file at startup.
To restore systemd-coredump defaults, also remove ${COREDUMP_FILE}.
Kernel restrictions require removing the corresponding staged kernel
arguments and rebooting, or booting a deployment without those arguments.
MESSAGE
