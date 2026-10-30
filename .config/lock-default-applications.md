# Lock Default Applications

Prevent applications from modifying `~/.config/mimeapps.list` by setting the file's immutable attribute.

## Lock the file

```bash
run0 chattr +i "$HOME/.config/mimeapps.list"
```

## Verify

```bash
lsattr "$HOME/.config/mimeapps.list"
```

The output should contain `i`, for example:

```text
----i----------------- ~/.config/mimeapps.list
```

While immutable, the file cannot be modified, truncated, renamed, deleted, or replaced.

This is stronger than making the file read-only with `chmod 444`, because a read-only file in a user-owned directory can ordinarily still be deleted and recreated.

## Change the defaults later

Temporarily remove the immutable attribute:

```bash
run0 chattr -i "$HOME/.config/mimeapps.list"
```

Edit the file:

```bash
nano "$HOME/.config/mimeapps.list"
```

Then lock it again:

```bash
run0 chattr +i "$HOME/.config/mimeapps.list"
```
