The files here quickly set up a visually austere and elegant base DE after a fresh install of Fedora Sway Atomic. Some of the files -- such as .bashrc -- are opinionated and thus contain stuff you might not need but that I want in a fresh install (for instance: a simple script that makes dunst timer-notifications via CLI commands like "1m" for "1 minute").

For the rice to look correct and be functional, you should:

(a) configure the appropriate scaling settings for your display in ~/.config/sway/config;

(b) note that the rofi files here assume you have flatpak Firefox and GIMP installed; if you use other apps, a simple change to the app names in the relevant rofi files is all you need to do; but you might have to manually adjust the rofi width to make the title of your apps cleanly fit fully within the rofi menu. But if you use something besides Firefox, as far as I know, you won't be able to apply Firefox's chrome files, and you won't be able to use the Firefox Temporary Extensions (Speed Dial and YouTube Speed Controller);

(c) install the Firefox Temporary Extensions (they are meant to be used with the rice; without the Speed Dial extension, a new tab on Firefox will be blank black); the number of Speed Dial cubes can be easily adjusted via the extension files themselves;

(d) install Privacy Badger, Ublock Origin, and NoScript;

(e) enable custom .css in Firefox by setting "toolkit.legacyUserProfileCustomizations.stylesheets" to "true" in about:config;

(f) keep "browser.bookmarks.editDialog.showForNewBookmarks" set to "true" in about:config; the checkbox for this setting and the associated text has been removed from the actual "Add Bookmark" popup.

(g) in Firefox's about:config, set "full-screen-api.enabled" to "false" (this prevents tapping to fullscreen on a YouTube video while preserving Mod+F for an enlarged player);

(h) disable split view and tab groups via about:config;

(i) set "browser.urlbar.scotchBonnet.enableOverride" to "false" in about:config; this removes the "This time search with" icon on the left-side of the URL bar; it is useless bloat. Go to "settings" > "search" and disable all default "Search Shortcuts"; then create your own with brief keywords, making sure that even for these the blue left-side check mark is not set. (Unchecking the blue check mark prevents the ugly addition of icons and "This time search with" text to the bottom of your URL-bar dropdown.) Ultimately, it is much faster and more natural to type "yt [your query]" and press enter to invoke a YouTube search than it is to navigate your mouse to the shortcuts icon, click it, click on the YouTube icon, and then type your query and press enter;

(j) via Customize Toolbar, set Density to "Compact"; this prevents a weird, unpleasant zoom effect when dragging tabs;

(k) store your main bookmarks under the default "Bookmarks Toolbar". Via userChrome.css, the bookmarks sidebar has been modified to hide (but not remove) the text label "Bookmarks Toolbar", "Bookmarks Menu", and "Other Bookmarks", so your main bookmarks should appear cleanly when you press Ctrl+B to bring up the sidebar;

(l) use only Ctrl+B to bring up the left-side bookmarks sidebar, while removing the horizontal bookmarks toolbar itself from appearing;

(m) use Ctrl+D to bookmark pages; there is no URL-bar bookmark icon;

(n) manually set the first YouTube video you load to theater-mode via the theater-mode toggle (the toggle is below the video progress bar, on the right); all subsequently loaded videos will then be in theater-mode (but when you close and reopen Firefox, you must do this again). Currently, there is no way, as far as I know, to set theater-mode permanently via .css or otherwise;

(o) set the auto-play toggle to off; as with theater-mode, this will also persist across videos;

(p) be already subscribed to the YouTube channels you want to be subscribed to; the current YouTube userContent.css file hides the subscribe button on YouTube profiles, and this is listed in problems-to-be-fixed.txt. It will be fixed soon, but it is not an urgent priority for me;

(q) in Thunar, press Ctrl+M, click "View," and uncheck "Show File Highlight";

(r) get used to used opening external drives in Thunar via the CLI (this is not the same as managing external drives fully through the CLI and requires enabling volume management in Thunar preferences); currently, external drives are not visible upon plug due to the sidebar text being hidden; this is one of the listed problems in problems-to-be-fixed.txt;

(s) get used to operating without right-click menus, most of which have been disabled (they are usually redundant clutter; for instance, if Ctrl+A copies highlighted text, why do you need an explicit "Copy" command in a right-click menu?);

(t) use Firefox in dark mode.

Gradually, improvements will be made to the files until all the problems identified in problems-to-be-fixed.txt are fixed (or marked as unfixable).

Note: AI -- mainly ChatGPT 5.5 plus -- has been and will continue to be indespensible in creating and maintaining the userChrome.css and userContent.css files (I'm not going to spend a year or more of my life painstakingly manually writing fragile .css for Firefox); if, for whatever reason, you have a principle against using AI, this is your warning.
