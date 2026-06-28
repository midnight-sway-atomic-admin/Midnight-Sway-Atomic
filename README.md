UPDATE: A major refactor of userChrome.css has dramatically simplified the file to ~500 LoC (excluding comments and blank lines). 

(a) The refactor removes the back-forward arrows (if Alt+< and > is sufficient for Thunar, why shouldn't it be sufficient for Firefox?).

(b) The custom trust-icon has also been removed: the default Firefox icon is uglier, but removing the custom icon helps future-proof the code and decrease the fragility of messing with the browser's security-states indicators.  

(c) Density=Compact is now no longer recommended; it now distorts the appearance of the URL bar and tabs, and so Density=Normal should be set if you are currently using Compact mode. This is a win as it minimizes setup hassle and fragility. Make sure to update your user.js file with the new one.

(d) Both sides of the tab-bar now have a fade, preventing an unpleasant blunt cutoff on the left.

(e) Bookmarks appear more cleanly, without twisties.

(f) There is now the option (by default turned off) to make the URL-bar search box sweep across the page from end to end when clicked; to enable this, go to line 144 of userChrome.css and make the required changes specified in the comment.

(g) The refactor also now tags almost all the current code as XX, meaning that the file is currently nearly final in terms of maturity. There are many minor additions still to be made in terms of capturing and styling all surfaces, but the end--a state of pure maintainability--is in sight, and the final LoC should be able to stay below 750.

(h) The "Add Bookmark" and Trust-icon popups now have manual positioning controls in userChrome.css; for my display I want their top-left corners to overlap perfectly, so that the popups always display in the same top-left area. For your display, you will probably have to adjust the values to have the popups display neatly.

(i) The updated .bashrc script modifies the dunst timer-notificatons code, which now includes the ability to set exact times and notes for timers: for instance, if you need a timer to go off in 1 day, 23 hours and 59 minutes, you type "1d23h59m"; if you want to attach a note to that notiifcation, you type:

1d23h59m "This is my note!"

You now cannot set the timer for more than 59 minutes by minutes alone; nor can you set the timer for more than 23 hours by hours alone; nor can you set the timer for more than 9 days 23 hours and 59 minutes. The shortest possible timer is "1m" for 1 minute.

/* END OF UPDATE NOTIFICATION */


The files here quickly set up a visually austere and elegant base DE after a fresh install of Fedora Sway Atomic. Some of the files -- such as .bashrc -- are opinionated and thus contain stuff you might not need but that I want in a fresh install (for instance: a simple script that makes dunst timer-notifications via CLI commands like "1m" for "1 minute"). The files are a work in progress and will be changing continually.

For the rice to look correct and be functional, you should:

(a) configure the appropriate scaling settings for your display in ~/.config/sway/config (the rice is being built on a 2560x1600 display, and other display sizes have not been tested);

(b) note that the rofi files here assume you have flatpak Firefox and GIMP installed; if you use other apps, a simple change to the app names in the relevant rofi files is all you need to do; but you might have to manually adjust the rofi width to make the title of your apps cleanly fit fully within the rofi menu. But if you use something besides Firefox, as far as I know, you won't be able to apply Firefox's chrome files, and you won't be able to use the Firefox Temporary Extensions (Speed Dial and YouTube Speed Controller);

(c) install the Firefox Temporary Extensions (they are meant to be used with the rice; without the Speed Dial extension, a new tab on Firefox will default to Firefox's widgets); the number of Speed Dial cubes can be easily adjusted via the extension files themselves by editing newtab.js (change "const TOTAL_CELLS = 60" to your desired total number) and style.css (scroll down to "grid-template-columns" and "grid-template-rows" and change "12" and "5" to your desired numbers). By default, the number of speed-dial cubes is set to 60 (12x5);

(d) install Privacy Badger, Ublock Origin, and NoScript;

(e) install the user.js file; this removes the "This time search with" icon on the left-side of the URL bar; it is useless bloat. Go to "settings" > "search" and disable all default "Search Shortcuts"; then create your own with brief keywords. Ultimately, it is much faster and more natural to type "yt [your query]" and press Enter to invoke a YouTube search than it is to navigate your mouse to the shortcuts icon, click it, click on the YouTube icon, and then type your query and press Enter. The user.js file is also now used to aggressively suppress all Firefox tooltips except those for tabs; to enable CSS styling; etc.;

(f) store all your main bookmarks under the default "Bookmarks Toolbar". Via userChrome.css, the bookmarks sidebar has been modified to hide (but not remove) the text label "Bookmarks Toolbar", "Bookmarks Menu", and "Other Bookmarks", so your main bookmarks -- when stored correctly -- should appear cleanly when you press Ctrl+B to bring up the sidebar;

(g) use only Ctrl+B to bring up the left-side bookmarks sidebar (there is no sidebar button), while removing the horizontal bookmarks toolbar itself from appearing;

(h) use Ctrl+D to bookmark pages (there is no URL-bar bookmark button);

(i) in Thunar, press Ctrl+M, click "View," and check "Show File Highlight" (this is now recommended whereas before it was not; the gtk.css file now includes color controls for the highlight);

(j) get used to operating Firefox without right-click menus, most of which have been disabled (they are usually redundant clutter; for instance, if Ctrl+A copies highlighted text, why do you need an explicit "Copy" command in a right-click menu?);

(k) have at least a 400 (ideally 500) nit display; otherwise the theme will likely be too dark to use comfortably;

(l) ideally use Firefox's zoom feature to set YouTube to 90% zoom (text looks much better this way);

(m) don't use the new-tab feature (Ctrl+T) in Thunar; use a new Thunar window (Ctrl+N) if you need two separate Thunar file areas; and clear the new-tab Ctrl+T and Split View shortcuts to prevent accidental splitting.

Gradually, improvements will be made to the files until all the problems identified in problems-to-be-fixed.txt are fixed (or marked as unfixable).

Thanks go to Visax (https://unsplash.com/@visaxslr) for his elegant designs which I have repurposed as wallpapers.

Note: AI -- mainly ChatGPT 5.5 plus -- has been and will continue to be indespensible in creating and maintaining the userChrome.css and userContent.css files (I'm not going to spend a year or more of my life painstakingly manually writing fragile CSS for Firefox); if, for whatever reason, you have a principle against using AI, this is your warning.
