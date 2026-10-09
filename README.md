# Midnight Sway Atomic

A visually austere, minimal base desktop environment for a fresh install of Fedora Sway Atomic.

> **Work in progress:** These files change continually as the setup is refined. Some are deliberately opinionated and include personal conveniences that you may not want. For example, `.bashrc` includes a small script for creating Dunst timer notifications from the command line.

<!-- GIF COLLAGE: add showcase GIF here -->

## Setup Notes

For the rice to look correct and function as intended, review the following before using it.

### Display scaling

The rice is being built on a **2560×1600** display. Other display sizes have not been tested.

Configure the appropriate scaling settings for your display in:

```text
~/.config/sway/config
```

### Rofi application entries

The Rofi files assume that the Flatpak versions of **Firefox** and **GIMP** are installed.

If you use different applications, change the application names in the relevant Rofi files. You may also need to adjust the Rofi width manually so that application titles fit cleanly within the menu.

If you replace Firefox, you also won't be able to use the included Firefox chrome files or the Firefox temporary extensions described below.

## Firefox Setup

### Temporary extensions

Install the included Firefox temporary extensions:

- **Speed Dial**
- **YouTube Speed Controller**

They are intended to be used with the rice. Without the Speed Dial extension, a new Firefox tab will fall back to Firefox's own new-tab content.

The number of Speed Dial cells can be changed in the extension files:

In `newtab.js`, change:

```js
const TOTAL_CELLS = 60;
```

In `style.css`, scroll to:

```css
grid-template-columns
grid-template-rows
```

and change the default values of `12` and `5` to the dimensions you want.

The default layout is **60 cells (12×5)**.

### Recommended extensions

Install:

- Privacy Badger
- uBlock Origin
- NoScript

### `user.js`

Install the included `user.js`.

Among other things, it:

- removes the **"This time search with"** control from the left side of the URL bar;
- aggressively suppresses Firefox tooltips except those for tabs;
- enables CSS styling used by the rice;
- applies other Firefox preferences needed by the configuration.

In **Settings → Search**, disable all default **Search Shortcuts**, then create your own with short keywords.

For example, using `yt` as the keyword for YouTube lets you type:

```text
yt [your query]
```

and press Enter, rather than opening the search-shortcuts interface and selecting YouTube manually.

### Bookmarks sidebar

Store your main bookmarks under Firefox's default **Bookmarks Toolbar** folder.

The included `userChrome.css` hides—but does not remove—the sidebar labels:

- Bookmarks Toolbar
- Bookmarks Menu
- Other Bookmarks

When your bookmarks are stored under **Bookmarks Toolbar**, they therefore appear cleanly when you press `Ctrl+B`.

Use `Ctrl+B` to open the left-side bookmarks sidebar. The rice does not provide a sidebar button, and the horizontal bookmarks toolbar itself is hidden.

Use `Ctrl+D` to bookmark the current page. The URL-bar bookmark button is removed.

### Density

Do **not** use `Density=Compact`.

Compact density now distorts the appearance of the URL bar and tabs. Use **Density=Normal** instead.

If you previously used Compact mode, update your `user.js` with the current version.

### Popup positioning

The **Add Bookmark** and **Trust** popups have manual positioning controls in `userChrome.css`.

On the display used to build this rice, their top-left corners are positioned to overlap exactly so that both popups open in the same area.

You will probably need to adjust those values for a different display size or scaling configuration.

### Right-click menus

Most Firefox right-click menus have been disabled because the rice assumes keyboard-driven operation where practical.

For example, after selecting text, `Ctrl+C` copies it directly; an additional **Copy** entry in a context menu is usually unnecessary.

This is an opinionated choice and may require some adjustment if you normally rely on context menus.

## Thunar Setup

### File highlight

In Thunar:

1. Press `Ctrl+M`.
2. Open **View**.
3. Enable **Show File Highlight**.

This is now recommended. The included `gtk.css` contains color controls for the highlight.

### Avoid tabs and split view

Do not use Thunar's new-tab feature (`Ctrl+T`) with this setup.

If you need two separate file-manager areas, open a second Thunar window with `Ctrl+N`.

It is also recommended that you clear the shortcuts for:

- **New Tab** (`Ctrl+T`)
- **Split View**

This prevents accidental tab creation or pane splitting.

## Display Brightness

A display capable of at least **400 nits**, and preferably around **500 nits**, is recommended.

The theme is intentionally dark and may be uncomfortable or difficult to use on substantially dimmer displays.

## Dunst Timer Commands

The included `.bashrc` contains a small Dunst timer-notification script.

Timers can be entered as compact durations. For example:

```text
1d23h59m
```

sets a timer for **1 day, 23 hours, and 59 minutes**.

A note can be attached:

```text
1d23h59m "This is my note!"
```

Quotation marks are required only when the note contains spaces.

Current limits:

- minutes alone: `1m` through `59m`;
- hours alone: `1h` through `23h`;
- maximum duration: `9d23h59m`;
- minimum duration: `1m`.

## Development Status

The files are being refined gradually.

The aim is to fix, or deliberately abandon after investigation, the issues listed in:

```text
problems-to-be-fixed.txt
```

## Credits

Thanks to [Visax](https://unsplash.com/@visaxslr) for the abstract designs repurposed here as wallpapers, and to [Andrew Hughes](https://unsplash.com/@hughesy) for the moon photograph used as another wallpaper.

## AI Use

AI has been, and will continue to be, used extensively in creating and maintaining this rice.

If you prefer not to use configurations or software developed with AI assistance, this repository may not be suitable for you.
