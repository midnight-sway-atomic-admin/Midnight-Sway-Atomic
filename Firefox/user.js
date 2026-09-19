/* Firefox user.js Place this file in the Firefox profile root, alongside prefs.js and the chrome/ directory. */

/* Enables CSS customization through userChrome.css and userContent.css */
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

/* Sets the onscreen CSS-pixel scale to 1.8; a positive value overrides automatic platform scaling and affects both Firefox chrome and web content */
user_pref("layout.css.devPixelsPerPx", "1.8");

/* Overrides Firefox's system Highlight and HighlightText colors globally, including selected-text background and foreground colors */
user_pref("ui.highlight", "#8a97bf");
user_pref("ui.highlighttext", "#000000");

/* Disables ordinary Firefox chrome tooltips; tab hover previews are controlled separately below */
user_pref("browser.chrome.toolbar_tips", false);

/* Keeps tab hover previews enabled but suppresses their page thumbnails */
user_pref("browser.tabs.hoverPreview.enabled", true);
user_pref("browser.tabs.hoverPreview.showThumbnails", false);

/* Disables Firefox's Scotch Bonnet unified-search feature set, including its unified search-button and secondary-action UI */
user_pref("browser.urlbar.scotchBonnet.enableOverride", false);

/* Disables Firefox Suggest-branded Quick Suggest results in the URL bar, including sponsored suggestions */
user_pref("browser.urlbar.suggest.quicksuggest.all", false);

/* Shows the bookmark-edit panel when creating a new bookmark; userChrome.css hides the panel's corresponding "show editor" checkbox */
user_pref("browser.bookmarks.editDialog.showForNewBookmarks", true);

/* Enables Firefox's closing-multiple-tabs confirmation when at least two non-pinned tabs are open, subject to the normal quit-prompt conditions */
user_pref("browser.tabs.warnOnClose", true);

/* Disables loading of site favicons for Firefox chrome, including tab favicons */
user_pref("browser.chrome.site_icons", false);

/* Disables the Web Fullscreen API for webpages, including video players; this does not control window-manager/compositor fullscreen */
user_pref("full-screen-api.enabled", false);
