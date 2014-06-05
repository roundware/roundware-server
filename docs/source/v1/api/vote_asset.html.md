---
page_title: "vote_asset"
sidebar_current: "api-vote-asset"
---

# vote_asset

Used to collect user-generated data associated with specific assets.  Most common uses
are to allow users to "like" an asset or "flag" an asset for review.

**Example Call:**

```
http://rw.roundware.org/roundware/?operation=vote_asset&asset_id=234&session_id=1&vote_type=like
```

## Parameters (some optional*):

* `vote_type`
* `asset_id`
* `session_id`
* `value`*

### vote_type

This is an unrestricted field allowing different projects to create flexible voting scenarios.  Typically,
vote_types are 'like' or 'flag'.

### asset_id

Indicates which asset is being voted upon.

### session_id

Allows for proper recording of a related event for full session tracking

### value

*OPTIONAL:* Allows for the collection of an additional piece of information related to the vote.  For example,
if there was a vote_type of 'rating', one could use the value field to contain a numeric value for the rating
i.e. 1-5.


## Response

JSON response is success boolean, indicating that the vote was properly received by the server.

### Example Response

```
{"success": true}
```
