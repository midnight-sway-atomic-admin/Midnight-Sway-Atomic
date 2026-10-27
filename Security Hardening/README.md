# Fedora Sway Atomic security hardening

A Bash script that makes several kinds of attack harder by restricting access to the Linux kernel, protecting memory, tightening network behaviour and reducing sensitive crash data.

The **kernel** is the central part of Linux that manages hardware, memory and running programs. **Root** is the system administrator account.

This is a strict configuration for an x86-64 Fedora Sway Atomic desktop using the stock Fedora kernel. Some settings may already match Fedora's defaults; the script explicitly sets them so the intended policy is clear.

## Before running

- **32-bit Linux programs won't run.** This can break games and Wine/Proton components, including those inside Flatpak or containers.
- **SMT is disabled.** On supported processors, this stops multiple hardware threads sharing one CPU core. Some workloads will run more slowly.
- **Debugging and crash diagnosis are restricted.** Tools such as `gdb` and `strace`, and some application crash handlers, may stop working.
- **Unsigned kernel modules won't load.** Third-party drivers need a signature the kernel trusts.
- **Some applications and hardware tools may fail.** Restrictions on `io_uring`, kernel debugging and memory access can affect them. Hibernation may also be unavailable.
- **Performance may decrease.** CPU protections, memory clearing and stricter hardware isolation have costs that depend on the machine and workload.

The script requires an OSTree-booted Fedora system, Linux 6.12 or newer, `rpm-ostree`, kernel lockdown support and the required kernel settings. It also checks that `systemd-sysctl` supports `--strict`.

Keep a working previous deployment available in the boot menu. A deployment is a bootable version of the operating system. If the script fails after starting its changes, some changes may already have taken effect.

## Run

Save the script as `fedora-sway-atomic-security-hardening-x86_64.sh`. From its folder, read its help:

```bash
bash fedora-sway-atomic-security-hardening-x86_64.sh --help
```

Apply the configuration:

```bash
sudo bash fedora-sway-atomic-security-hardening-x86_64.sh
```

Then reboot:

```bash
systemctl reboot
```

Some settings apply immediately. Rebooting activates the full configuration, including the kernel boot settings.

## What each setting does

### Kernel access and debugging

These are `sysctl` settings: controls for the running kernel that the script also saves for future boots.

| Setting | Simple explanation |
| --- | --- |
| `kernel.kptr_restrict = 2` | Hides kernel memory addresses in interfaces that use the restricted-pointer format, even from root. These addresses can help attackers. |
| `kernel.dmesg_restrict = 1` | Limits access to the kernel message buffer, which can reveal useful information to attackers. |
| `kernel.randomize_va_space = 2` | Randomises where programs store code and data, including the heap, making memory attacks harder to aim. |
| `kernel.yama.ptrace_scope = 3` | Blocks `ptrace` debugging, including for root, reducing one way programs can inspect or alter other programs. |
| `kernel.perf_event_paranoid = 2` | Stops unprivileged programs from profiling the kernel. It doesn't ban all profiling of their own code. |
| `kernel.unprivileged_bpf_disabled = 1` | Stops unprivileged programs from loading BPF programs: small programs that run inside the kernel. |
| `net.core.bpf_jit_harden = 2` | Adds protection to compiled BPF code for all users, making certain code-injection attacks harder. |
| `kernel.kexec_load_disabled = 1` | Blocks loading another kernel through `kexec`, which normally allows switching kernels without a normal reboot. |
| `kernel.io_uring_disabled = 2` | Blocks new `io_uring` instances for everyone, including root. This closes access to a complex input/output interface; existing instances remain usable. |
| `dev.tty.ldisc_autoload = 0` | Stops unprivileged programs from automatically loading extra terminal-processing modules into the kernel. |
| `dev.tty.legacy_tiocsti = 0` | Stops unprivileged programs from using the old `TIOCSTI` interface to inject keystrokes into a terminal. |

The two `dev.tty` entries are optional: the script tolerates failures when applying them. `ptrace_scope=3`, `unprivileged_bpf_disabled=1` and `kexec_load_disabled=1` can't be relaxed again during the same boot.

### Program memory

| Setting | Simple explanation |
| --- | --- |
| `vm.unprivileged_userfaultfd = 0` | Restricts the `userfaultfd` system call's handling of kernel-side memory faults, making some kernel bugs harder to exploit. It doesn't disable the feature entirely. |
| `vm.mmap_min_addr = 65536` | Keeps ordinary programs out of the lowest 64 KiB of memory, helping limit damage from certain kernel bugs. |
| `vm.mmap_rnd_bits = 32` | Increases the unpredictability of memory mapping locations for 64-bit programs. |

### Files and shared folders

| Setting | Simple explanation |
| --- | --- |
| `fs.protected_hardlinks = 1` | Restricts creating extra filenames, called hard links, for other users' files. This helps prevent misuse of privileged programs. |
| `fs.protected_symlinks = 1` | Restricts following unsafe symbolic links in shared folders such as `/tmp`, helping stop malicious redirection to another file. |
| `fs.protected_fifos = 2` | Helps stop programs being tricked into writing to someone else's named pipe when they expected to create a file. |
| `fs.protected_regular = 2` | Helps stop programs being tricked into writing to someone else's existing file when they expected to create their own. |
| `fs.suid_dumpable = 0` | Disables ordinary core dumps for programs that gain extra privileges, reducing the risk of exposing their memory. |

The FIFO and regular-file protections cover relevant shared folders writable by everyone or by a group. They don't prevent all writes to other users' files.

### IPv4 networking

For rows containing `<scope>`, the script sets `all`, `default` and `*`: the global control, defaults for new interfaces and rules for individual interfaces. An interface is a network connection such as Wi-Fi or Ethernet.

| Setting | Simple explanation |
| --- | --- |
| `net.ipv4.conf.<scope>.accept_source_route = 0` | Rejects packets that try to specify their own route through the network. |
| `net.ipv4.conf.<scope>.accept_redirects = 0` | Ignores messages telling the computer to change its network route, reducing opportunities for malicious redirection. |
| `net.ipv4.conf.<scope>.secure_redirects = 0` | Also disables the limited form of route redirects called “secure redirects”. These aren't encrypted or guaranteed trustworthy. |
| `net.ipv4.conf.<scope>.send_redirects = 0` | Stops the computer from sending route-change instructions to other devices. |
| `net.ipv4.icmp_echo_ignore_broadcasts = 1` | Ignores pings sent to a whole network at once, reducing participation in certain flooding attacks. Ordinary pings remain allowed. |
| `net.ipv4.icmp_ignore_bogus_error_responses = 1` | Suppresses warnings about certain malformed network error messages. This mainly reduces log noise. |
| `net.ipv4.tcp_syncookies = 1` | Enables a fallback that helps preserve incoming TCP connections when excessive connection requests fill the waiting queue. |
| `net.ipv4.tcp_rfc1337 = 1` | Stops reset packets from prematurely removing TCP's waiting state after a connection closes, helping avoid interference from old packets. |

### IPv6 networking

The same `<scope>` notation applies here. IPv6 and its normal automatic address configuration remain enabled.

| Setting | Simple explanation |
| --- | --- |
| `net.ipv6.conf.<scope>.accept_redirects = 0` | Ignores IPv6 messages that tell the computer to change its network route. |
| `net.ipv6.conf.<scope>.accept_source_route = -1` | Rejects IPv6 routing extension headers. The negative value also rejects the type still allowed by `0`. |

### Kernel boot settings

These take effect after reboot. The script uses `rpm-ostree` to prepare a deployment with these arguments. It replaces conflicting values for managed settings and removes several known options that disable CPU protections.

| Setting | Simple explanation |
| --- | --- |
| `lockdown=confidentiality` | Restricts interfaces that can modify the kernel or expose its memory, including access normally available to root. |
| `module.sig_enforce=1` | Requires kernel modules, including extra drivers, to have a signature the kernel trusts. |
| `spectre_v2=on` | Forces Spectre v2 protections, including protection between applications, where supported. |
| `spec_store_bypass_disable=on` | Disables a CPU optimisation that can leak information through the Speculative Store Bypass vulnerability. |
| `nosmt=force` | Disables SMT wherever supported and prevents it being switched back on during that boot. |
| `ia32_emulation=0` | Disables 32-bit Linux programs and their system calls, removing older kernel entry points. |
| `randomize_kstack_offset=on` | Randomises an offset in the kernel's working memory for system calls, making its layout harder to predict. |
| `init_on_alloc=1` | Clears newly allocated kernel memory to reduce exposure of leftover data. |
| `init_on_free=1` | Clears kernel memory when it's released, reducing how long old data remains available. |
| `page_alloc.shuffle=1` | Shuffles available memory pages, making the physical memory allocation pattern less predictable. |
| `slab_nomerge` | Keeps different kernel object caches separate, making some memory-corruption attacks harder to arrange. |
| `debugfs=off` | Disables a kernel debugging interface that can expose powerful controls and sensitive information. |
| `iommu.strict=1` | Immediately revokes hardware memory mappings when they're released, reducing the time devices retain access. |
| `iommu.passthrough=0` | Requests controlled device memory access through the IOMMU instead of bypassing it by default. |
| `pti=on` | Separates kernel and program address mappings to help protect against Meltdown-style attacks. |
| `vsyscall=none` | Disables an old system-call mechanism with predictable addresses. Very old programs may stop working. |
| `proc_mem.force_override=never` | Stops `/proc/PID/mem` access from overriding a program's normal memory-page permissions. |
| `amd_iommu=force_isolation` — AMD only | Requests device isolation without allowing the AMD IOMMU driver to relax it for individual devices. |
| `intel_iommu=on` — Intel only | Enables Intel's IOMMU driver when the hardware and firmware support it. |

An **IOMMU** limits which parts of memory hardware devices can access directly. These requests need working hardware, firmware and driver support; listing the arguments doesn't prove protection is active.

Kernel lockdown doesn't enable Secure Boot or replace its protection of the boot process.

### Application crash dumps

A core dump is a copy of a crashed program's memory. It can contain passwords, document text or other private data.

| Setting | Simple explanation |
| --- | --- |
| `Storage=none` | Tells `systemd-coredump` not to keep core dumps. |
| `ProcessSizeMax=0` | Stops it processing core dumps, avoiding temporary dump files created during that processing. |

Together, these leave only a crash log entry. They don't delete existing dumps or stop applications from making their own crash reports.

## Files installed

| Location | Purpose |
| --- | --- |
| `/etc/sysctl.d/99-zz-security-hardening.conf` | Saves the kernel controls applied immediately and again at boot. |
| `/etc/systemd/coredump.conf.d/99-zz-security-hardening.conf` | Saves the crash-dump restrictions. |

Kernel arguments are managed separately by `rpm-ostree`. The script refuses to overwrite an unrelated file at either configuration path.

User namespaces remain enabled because Flatpak uses them to build application sandboxes.

## Check after reboot

```bash
cat /sys/kernel/security/lockdown
cat /proc/cmdline
sysctl kernel.yama.ptrace_scope kernel.io_uring_disabled
systemd-analyze cat-config systemd/coredump.conf
```

Look for `[confidentiality]`, `ptrace_scope = 3`, `io_uring_disabled = 2`, and the two crash-dump settings above. `/proc/cmdline` shows the arguments used for the current boot.

On CPUs with SMT controls:

```bash
cat /sys/devices/system/cpu/smt/control
```

Expect `forceoff` where forced SMT disabling is supported. Hardware without SMT may report `notsupported`.

Check IOMMU messages:

```bash
sudo dmesg | grep -Ei 'DMAR|IOMMU|AMD-Vi'
```

Look for successful initialisation and any errors. A matching message alone isn't proof of complete device isolation. These checks are a quick inspection, not a full security audit.

## Undo changes

If the new deployment won't boot, select the previous deployment from the boot menu. Each deployment has its own `/etc`; inspect whichever deployment you intend to keep using.

To remove this script's persistent kernel controls and crash-dump configuration from the current deployment:

```bash
sudo rm -f /etc/sysctl.d/99-zz-security-hardening.conf
sudo rm -f /etc/systemd/coredump.conf.d/99-zz-security-hardening.conf
```

To remove its boot restrictions, edit the default deployment's kernel arguments:

```bash
sudo rpm-ostree kargs --editor
```

Remove the arguments listed under **Kernel boot settings** that you want to undo, preserving unrelated boot arguments. Restore any previous custom values you need: the script doesn't save them.

Reboot after making these changes. Deleting the files doesn't immediately reset running settings, and rebooting without removing the configuration simply reapplies it. Removing an argument lets the kernel use its default or other configured policy; some protections may remain enabled by Fedora or Secure Boot.

## References

- [Linux kernel controls](https://docs.kernel.org/admin-guide/sysctl/kernel.html)
- [Yama process-inspection restrictions](https://docs.kernel.org/admin-guide/LSM/Yama.html)
- [Memory controls](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [File protections](https://docs.kernel.org/admin-guide/sysctl/fs.html)
- [BPF compiler protection](https://docs.kernel.org/admin-guide/sysctl/net.html#bpf-jit-harden)
- [IPv4 and IPv6 controls](https://docs.kernel.org/networking/ip-sysctl.html)
- [TCP waiting-state implementation](https://github.com/torvalds/linux/blob/master/net/ipv4/tcp_minisocks.c)
- [Kernel boot arguments](https://docs.kernel.org/admin-guide/kernel-parameters.html)
- [systemd crash-dump settings](https://www.freedesktop.org/software/systemd/man/latest/coredump.conf.html)
