/* Install this file in the same place that you have installed the "chrome" folder */

/* X Suppresses non-tab Firefox tooltips */
user_pref("browser.chrome.toolbar_tips", false);

/* X Keeps tab hover tooltip/card */
user_pref("browser.tabs.hoverPreview.enabled", true);
user_pref("browser.tabs.hoverPreview.showThumbnails", false);

/* X Suppresses "This time search with..." URL-button */
user_pref("browser.urlbar.scotchBonnet.enableOverride", false);

/* X Ensures the "Add Bookmark" popup is always shown after pressing Ctrl+D; the "Add Bookmark" popup no longer contains the text or check box for enabling the editor for every new bookmark */
user_pref("browser.bookmarks.editDialog.showForNewBookmarks", true);

/* X Enables CSS customization via userChrome.css and userContent.css */
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

/* X Prevents the full-screening of videos by tapping the touchpad or otherwise; on YouTube use Mod+F to enlarge the videoplayer */
user_pref("full-screen-api.enabled", false);

/* Warns before closing Firefox */
user_pref("browser.tabs.warnOnClose", true);
