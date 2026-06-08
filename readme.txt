The files here quickly set up a visually austere and elegant base DE after a fresh install of Fedora Sway Atomic. Some of the files -- such as .bashrc -- are opinionated and thus contain stuff you might not need but that I want in a fresh install (for instance: a simple script that makes dunst timer-notifications via CLI commands like "1m" for "1 minute"). The files are a work in progress and will be changing continually.

For the rice to look correct and be functional, you should:

(a) configure the appropriate scaling settings for your display in ~/.config/sway/config;

(b) note that the rofi files here assume you have flatpak Firefox and GIMP installed; if you use other apps, a simple change to the app names in the relevant rofi files is all you need to do; but you might have to manually adjust the rofi width to make the title of your apps cleanly fit fully within the rofi menu. But if you use something besides Firefox, as far as I know, you won't be able to apply Firefox's chrome files, and you won't be able to use the Firefox Temporary Extensions (Speed Dial and YouTube Speed Controller);

(c) install the Firefox Temporary Extensions (they are meant to be used with the rice; without the Speed Dial extension, a new tab on Firefox will be blank black); the number of Speed Dial cubes can be easily adjusted via the extension files themselves by editing newtab.js (change "const TOTAL_CELLS = 60" to your desired total number) and style.css (scroll down to "grid-template-columns" and "grid-template-rows" and change "12" and "5" to your desired numbers). By default, the number of speed-dial cubes is set to 60 (12x5);

(d) install Privacy Badger, Ublock Origin, and NoScript;

(e) enable custom CSS in Firefox by setting "toolkit.legacyUserProfileCustomizations.stylesheets" to "true" in about:config;

(f) keep "browser.bookmarks.editDialog.showForNewBookmarks" set to "true" in about:config; the checkbox for this setting and the associated text have been removed from the actual "Add Bookmark" popup;

(g) in Firefox's about:config, set "full-screen-api.enabled" to "false" (this prevents tapping to fullscreen on a YouTube video while preserving Mod+F for an enlarged player);

(h) set "browser.urlbar.scotchBonnet.enableOverride" to "false" in about:config; this removes the "This time search with" icon on the left-side of the URL bar; it is useless bloat. Go to "settings" > "search" and disable all default "Search Shortcuts"; then create your own with brief keywords, making sure that even for these the blue left-side check mark is not set. (Unchecking the blue check mark prevents the ugly addition of icons and "This time search with" text to the bottom of your URL-bar dropdown.) Ultimately, it is much faster and more natural to type "yt [your query]" and press enter to invoke a YouTube search than it is to navigate your mouse to the shortcuts icon, click it, click on the YouTube icon, and then type your query and press enter;

(i) store all your main bookmarks under the default "Bookmarks Toolbar". Via userChrome.css, the bookmarks sidebar has been modified to hide (but not remove) the text label "Bookmarks Toolbar", "Bookmarks Menu", and "Other Bookmarks", so your main bookmarks -- when stored correctly -- should appear cleanly when you press Ctrl+B to bring up the sidebar;

(j) use only Ctrl+B to bring up the left-side bookmarks sidebar (there is no sidebar button), while removing the horizontal bookmarks toolbar itself from appearing;

(k) use Ctrl+D to bookmark pages (there is no URL-bar bookmark button);

(l) in Thunar, press Ctrl+M, click "View," and check "Show File Highlight" (this is now recommended whereas before it was not; the gtk.css file now includes color controls for the highlight);

(m) get used to operating Firefox without right-click menus, most of which have been disabled (they are usually redundant clutter; for instance, if Ctrl+A copies highlighted text, why do you need an explicit "Copy" command in a right-click menu?);

(n) set Firefox to dark mode;

(o) via Firefox's Customize Toolbar, set Density to Compact if (1) you want the tabs and URL-box and back-forward arrows to align perfectly and (2) you want to remove an unpleasant tab-drag zoom effect;

(p) have at least a 400 (ideally 500) nit display; otherwise the theme will likely be too dark to use comfortably.

Gradually, improvements will be made to the files until all the problems identified in problems-to-be-fixed.txt are fixed (or marked as unfixable).

Note: AI -- mainly ChatGPT 5.5 plus -- has been and will continue to be indespensible in creating and maintaining the userChrome.css and userContent.css files (I'm not going to spend a year or more of my life painstakingly manually writing fragile CSS for Firefox); if, for whatever reason, you have a principle against using AI, this is your warning.
