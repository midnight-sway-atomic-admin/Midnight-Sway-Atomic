/* Firefox user.js
   Place this file in the Firefox profile root, alongside prefs.js and the
   chrome/ directory */

/* ============================== GENERAL =============================== */

/* Enables CSS customization through userChrome.css and userContent.css */
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

/* Sets the onscreen CSS-pixel scale to 1.8; a positive value overrides
   automatic platform scaling and affects both Firefox chrome and web
   content */
user_pref("layout.css.devPixelsPerPx", "1.8");

/* Overrides Firefox's system Highlight and HighlightText colors, which
   provide default selection colors. Sites and styles can use different
   colors */
user_pref("ui.highlight", "#8a97bf");
user_pref("ui.highlighttext", "#000000");

/* Disables ordinary Firefox chrome tooltips; tab hover previews are
   controlled separately below */
user_pref("browser.chrome.toolbar_tips", false);

/* Keeps tab hover previews enabled but suppresses their page thumbnails */
user_pref("browser.tabs.hoverPreview.enabled", true);
user_pref("browser.tabs.hoverPreview.showThumbnails", false);

/* Stops the Scotch Bonnet override from enabling its grouped search
   features. Individual feature settings can still enable them, and some UI
   may remain */
user_pref("browser.urlbar.scotchBonnet.enableOverride", false);

/* Disables Firefox Suggest-branded Quick Suggest results in the URL bar,
   including sponsored suggestions */
user_pref("browser.urlbar.suggest.quicksuggest.all", false);

/* Shows the bookmark-edit panel when creating a new bookmark;
   userChrome.css hides the panel's corresponding "show editor" checkbox */
user_pref("browser.bookmarks.editDialog.showForNewBookmarks", true);

/* Enables Firefox's closing-multiple-tabs confirmation, subject to its
   normal window-closing and quit conditions. Pinned-tab handling varies by
   situation */
user_pref("browser.tabs.warnOnClose", true);

/* Disables loading of site favicons for Firefox chrome, including tab
   favicons */
user_pref("browser.chrome.site_icons", false);

/* Disables the Web Fullscreen API for webpages, including video players;
   this does not control window-manager/compositor fullscreen */
user_pref("full-screen-api.enabled", false);

/* Enables "Alt + Enter" to open the save-file dialogue for a selected file
   link on a website. Helps with keyboard-driven workflow since the
   right-click menu with Save is suppressed */
user_pref("browser.altClickSave", true);

/* Disables picture-in-picture mode */
user_pref("media.videocontrols.picture-in-picture.enabled", false);

/* Disables RTCPeerConnection and WebRTC data channels; calls may stop
   working. Camera and microphone capture are controlled separately */
user_pref("media.peerconnection.enabled", false);

/* Neutralizes Nova redesign; when these stop working, neutralization will
   move on to the actual CSS */
user_pref("browser.nova.enabled", false);
user_pref("sidebar.revamp", false);

/* ============================== PRIVACY =============================== */

/* Privacy settings updated for Firefox 160.0 on 11 November 2026 */

/* Opt out of technical/interaction data and the independently controlled
   daily usage ping */
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("datareporting.usage.uploadEnabled", false);

/* Disable the legacy data-submission policy and legacy Telemetry recording.
   toolkit.telemetry.enabled alone isn't a working desktop master switch;
   disabling unified Telemetry as well makes this pair stop legacy recording
   on the Release channel. Glean is controlled separately above */
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.enabled", false);

/* Remove the legacy Telemetry destination and disable local ping archiving */
user_pref("toolkit.telemetry.server", "");
user_pref("toolkit.telemetry.archive.enabled", false);

/* Disable the remaining legacy new-profile, shutdown, hang and health pings */
user_pref("toolkit.telemetry.newProfilePing.enabled", false);
user_pref("toolkit.telemetry.firstShutdownPing.enabled", false);
user_pref("toolkit.telemetry.shutdownPingSender.enabled", false);
user_pref("toolkit.telemetry.shutdownPingSender.enabledFirstSession", false);
user_pref("toolkit.telemetry.bhrPing.enabled", false);
user_pref("toolkit.telemetry.healthping.enabled", false);

/* Opt out of the user-characteristics ping and clear its manual send
   trigger */
user_pref("toolkit.telemetry.user_characteristics_ping.opt-out", true);
user_pref("toolkit.telemetry.user_characteristics_ping.send-once", false);

/* Disable New Tab telemetry, its telemetry feed, and its Glean content
   pings; the Activity Stream telemetry preference also covers welcome-page
   telemetry */
user_pref("browser.newtabpage.activity-stream.telemetry", false);
user_pref("browser.newtabpage.activity-stream.feeds.telemetry", false);
user_pref("browser.newtabpage.ping.enabled", false);
user_pref("browser.newtabpage.activity-stream.telemetry.privatePing.enabled", false);
user_pref("browser.newtabpage.activity-stream.telemetry.privatePing.inferredInterests.enabled", false);

/* Disable automatic crash-report submission and omit tab URLs if a tab
   crash report is later sent manually. Reports can still be submitted
   explicitly */
user_pref("browser.crashReports.unsubmittedCheck.autoSubmit2", false);
user_pref("browser.tabs.crashReporting.sendReport", false);
user_pref("browser.tabs.crashReporting.includeURL", false);

/* Disable reminders about unsent reports and requests for selected old
   crashes */
user_pref("browser.crashReports.unsubmittedCheck.enabled", false);
user_pref("browser.crashReports.onDemand", false);
user_pref("browser.crashReports.requestedNeverShowAgain", true);

/* Disable opt-out studies, the Normandy recipe client and Nimbus targeting
   context telemetry. These don't disable security blocklists or updates */
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("app.normandy.enabled", false);
user_pref("app.normandy.api_url", "");
user_pref("nimbus.telemetry.targetingContextEnabled", false);

/* Disable the separately controlled Firefox Account association/info pings */
user_pref("identity.fxaccounts.telemetry.clientAssociationPing.enabled", false);
user_pref("identity.fxaccounts.telemetry.clientInfoPing.enabled", false);

/* Stop local classification of search-results pages for search telemetry */
user_pref("browser.search.serpEventTelemetryCategorization.enabled", false);

/* Disable traffic-category, Akamai response, email-tracker and
   unexpected-system-load telemetry instrumentation. Email-tracker blocking
   remains available */
user_pref("network.traffic_analyzer.enabled", false);
user_pref("network.http.akamai_waf_telemetry.enabled", false);
user_pref("privacy.trackingprotection.emailtracking.data_collection.enabled", false);
user_pref("dom.security.unexpected_system_load_telemetry_enabled", false);

/* Disable personalized extension discovery and contextual recommendations */
user_pref("browser.discovery.enabled", false);
user_pref("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.addons", false);
user_pref("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.features", false);

/* Disable Firefox Suggest itself and its online requests, in addition to
   the result-visibility preference in the original settings above */
user_pref("browser.urlbar.quicksuggest.enabled", false);
user_pref("browser.urlbar.quicksuggest.online.enabled", false);

/* Disable sponsored New Tab content and the corresponding advertising feeds */
user_pref("browser.newtabpage.activity-stream.showSponsored", false);
user_pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);
user_pref("browser.topsites.contile.enabled", false);
user_pref("browser.newtabpage.activity-stream.unifiedAds.tiles.enabled", false);
user_pref("browser.newtabpage.activity-stream.unifiedAds.spocs.enabled", false);
user_pref("browser.newtabpage.activity-stream.unifiedAds.adsFeed.enabled", false);

/* ============================== SECURITY ============================== */

/* Require HTTPS in all windows; HTTP-only sites need an explicit exception */
user_pref("dom.security.https_only_mode", true);

/* Avoid the plaintext background probe that HTTPS-Only mode can send when
   an HTTPS connection is slow. Diagnosing an HTTP-only site may take longer */
user_pref("dom.security.https_only_mode_send_http_background_request", false);

/* Block HTTP scripts and HTTP images/audio/video embedded in HTTPS pages;
   older sites with insecure media may display incompletely */
user_pref("security.mixed_content.block_active_content", true);
user_pref("security.mixed_content.block_display_content", true);

/* Start with TLS 1.2 as the minimum and deprecated TLS disabled. These
   settings are not locked: an override can re-enable deprecated TLS during
   a session. Disable TLS 1.3 early data (0-RTT) to avoid its replay risk.
   Resumed connections may need one extra round trip; ordinary TLS 1.3
   remains enabled */
user_pref("security.tls.version.min", 3);
user_pref("security.tls.version.enable-deprecated", false);
user_pref("security.tls.enable_0rtt_data", false);

/* Show internationalized domain names as ASCII Punycode to expose
   lookalikes; legitimate non-ASCII domains will also display in their xn--
   form */
user_pref("network.IDN_show_punycode", true);

/* Prevent cross-origin embedded resources from opening HTTP-authentication
   prompts. Some authenticated embedded resources may no longer work */
user_pref("network.auth.subresource-http-auth-allow", 1);

/* Retain Local Network Access checks, including WebSockets; additionally
   block tracker-originated requests and requests from untrustworthy HTTP
   origins, and check private-network pages that contact localhost. Local
   device/app integrations may need permission or a secure connection */
user_pref("network.lna.enabled", true);
user_pref("network.lna.blocking", true);
user_pref("network.lna.websocket.enabled", true);
user_pref("network.lna.block_trackers", true);
user_pref("network.lna.block_insecure_contexts", true);
user_pref("network.lna.local-network-to-localhost.skip-checks", false);

/* Disable JavaScript embedded in PDFs. Scripted PDF calculations,
   validation and form actions may stop working; ordinary PDF viewing
   remains available */
user_pref("pdfjs.enableScripting", false);

/* Explicitly retain site isolation and extension signature/blocklist
   checks; keep platform-specific sandbox levels under Firefox's own
   defaults */
user_pref("fission.autostart", true);
user_pref("xpinstall.signatures.required", true);
user_pref("extensions.blocklist.enabled", true);
user_pref("extensions.update.enabled", true);

/* Retain phishing, malware and download protection. These security checks
   can contact Mozilla/Google; disabling browser telemetry doesn't disable
   them */
user_pref("browser.safebrowsing.phishing.enabled", true);
user_pref("browser.safebrowsing.malware.enabled", true);
user_pref("browser.safebrowsing.downloads.enabled", true);
user_pref("browser.safebrowsing.downloads.remote.enabled", true);
user_pref("browser.safebrowsing.downloads.remote.block_dangerous", true);
user_pref("browser.safebrowsing.downloads.remote.block_dangerous_host", true);
user_pref("browser.safebrowsing.downloads.remote.block_potentially_unwanted", true);
user_pref("browser.safebrowsing.downloads.remote.block_uncommon", true);

/* Retain certificate-revocation protection: enforce CRLite and allow OCSP
   fetching where applicable. Remote Settings stays enabled for revocation
   data, intermediate certificates and other security updates */
user_pref("security.pki.crlite_mode", 2);
user_pref("security.OCSP.enabled", 1);
user_pref("security.ssl.enable_ocsp_stapling", true);
