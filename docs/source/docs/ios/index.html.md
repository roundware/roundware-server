---
page_title: "iOS Client"
sidebar_current: "ios"
---

# iOS Client

The Roundware iOS framework can be found in a separate git repository.  It includes
the base framework as well as a generic example app which shows how the framework is
implemented in the context of an iOS app.

In an attempt to create code that is re-usable across clients, the tag-related screens
for both the Listen and Speak flows are webviews.  These screens are built dynamically
based on the contents of the JSON response to the get_tags API call and are therefore
very flexible with server changes, not app changes.

Additionally, the webview files themselves
are downloaded upon app startup (only if a new version is available), so they are likewise
updateable without any changes to the app.  The goal is to keep things as flexible as possible
without having to resubmit the app to Apple for approval more than absolutely necessary.
