# Configure firewalld

Enable and start `firewalld`:

```bash
sudo systemctl enable --now firewalld
```

Set the default firewall zone to `drop`. This changes both the runtime and permanent configuration:

```bash
sudo firewall-cmd --set-default-zone=drop
```

Disable intra-zone forwarding in the `drop` zone:

```bash
sudo firewall-cmd --permanent --zone=drop --remove-forward
```

Reload `firewalld` to apply the permanent configuration:

```bash
sudo firewall-cmd --reload
```

## Verify

Confirm that `firewalld` is enabled:

```bash
systemctl is-enabled firewalld
```

Expected output:

```text
enabled
```

Confirm that `firewalld` is running:

```bash
systemctl is-active firewalld
```

Expected output:

```text
active
```

Confirm that the default zone is `drop`:

```bash
sudo firewall-cmd --get-default-zone
```

Expected output:

```text
drop
```

Check which zones are actually active:

```bash
sudo firewall-cmd --get-active-zones
```

The default `drop` zone applies to traffic that isn't explicitly assigned to another zone through a connection profile, interface or source binding. Explicit assignments take precedence over the default zone.

Inspect the final `drop` zone configuration:

```bash
sudo firewall-cmd --zone=drop --list-all
```

Confirm that intra-zone forwarding is disabled:

```bash
sudo firewall-cmd --zone=drop --query-forward
```

Expected output:

```text
no
```

This query also returns exit status `1` when forwarding is disabled. That's the expected negative query result, not a command error.
