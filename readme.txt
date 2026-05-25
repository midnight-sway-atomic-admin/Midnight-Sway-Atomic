The files here quickly set up a visually austere and elegant base OS after a fresh install of Fedora Sway Atomic. Some of the files -- such as .bashrc -- are opinionated and thus contain stuff you might not need but that I want in a fresh install (for instance: a simple script that makes dunst timer-notifications via CLI commands like "1m" for "1 minute"). 

For the rice to look correct and be functional, you should:

(a) manually set the first YouTube video you load to theater-mode via the theater-mode toggle (the toggle is below the video progress bar, on the right); all subsequently loaded videos will then be in theater-mode (but when you close and reopen Firefox, you must do this again). Currently, there is no way, as far as I know, to set theater-mode permanently via .css or otherwise;

(b) set the auto-play toggle to off; as with theater-mode, this will also persist across videos;

(c) use only Ctrl+B to bring up the left-side bookmarks sidebar, while removing the horizontal bookmarks toolbar itself from appearing;

(d) via Customize Toolbar, set Density to "Compact"; this prevents a weird, unpleasant zoom effect when dragging tabs;

(e) disable splitview and tab groups via about:config;

(f) use Ctrl+D to bookmark pages; there is no URL-bar bookmark icon;

(g) get used to operating without right-click menus, most of which have been disabled (they are usually redundant clutter; for instance, if Ctrl+A copies highlighted text, why do you need an explicit "Copy" command in a right-click menu?);

(h) in Thunar, press Ctrl+M, click View, and uncheck Show File Highlight;

(i) get used to used opening external drives in Thunar via the CLI (this is not the same as managing external drives fully through the CLI and requires enabling volume management in Thunar preferences); currently, external drives are not visible upon plug due to the sidebar text being hidden; this is one of the listed problems in problems-to-be-fixed.txt;

(j) note that the rofi files here assume you have flatpak Firefox and GIMP installed; if you use other apps, a simple change to the app names in the relevant rofi files is all you need to do; but you might have to manually adjust the rofi width to make the title of your apps cleanly fit fully within the rofi menu. But if you use something besides Firefox, as far as I know, you won't be able to apply Firefox's chrome files, and you won't be able to use the Firefox Temporary Extensions (Speed Dial and YouTube Speed Controller);

(k) be already subscribed to the YouTube channels you want to be subscribed to; the current YouTube userContent.css file hides the subscribe button on YouTube profiles, and this is listed in problems-to-be-fixed.txt. It will be fixed soon, but it is not an urgent priority for me;

(l) remember that the extensions button is invisible but set to the left of the backwards-arrow icon;

(m) install Privacy Badger, Ublock Origin, and NoScript;

(n) configure the appropriate scaling settings for your display in ~/.config/sway/config.

Gradually, improvements will be made to the files until all the problems identified in problems-to-be-fixed.txt are fixed (or marked as unfixable).

Note: AI -- mainly ChatGPT 5.5 plus -- has been and will continue to be indespensible in creating and maintaining the userChrome.css and userContent.css files (I'm not going to spend a year or more of my life painstakingly manually writing fragile .css for Firefox); if, for whatever reason, you have a principle against using AI, this is your warning.
