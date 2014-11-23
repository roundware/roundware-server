---
page_title: "Android Client"
sidebar_current: "android"
---

# Android Client

The Roundware Android framework can be found in a separate git repository.  In a different
repository, there is a generic example app which shows how the framework is
implemented in the context of an Android app.

In an attempt to create code that is re-usable across clients, the tag-related screens
for both the Listen and Speak flows are webviews.  These screens are built dynamically
based on the contents of the JSON response to the `get_tags` API call and are therefore
very flexible with server changes, not app changes.

Additionally, the webview files themselves
are downloaded upon app startup (only if a new version is available), so they are likewise
updateable without any changes to the app.  The goal is to keep things as flexible as possible
without having to resubmit the app to the Play Store any more than necessary.