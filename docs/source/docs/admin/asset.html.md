---
page_title: "Admin - Assets"
sidebar_current: "admin-asset"
---

# Asset Admin

<div class="alert alert-block alert-info">
    <p>
        <strong>DEFINITION:</strong> An individual piece of media contributed by a user or administrator.  Roundware currently handles audio, photo and text assets and will soon handle video assets as well.  Assets are assigned many pieces of metadata, including a project, tags, location, and others.
    </p>
</div>

Assets are listed in the Project List view with their key data.  You can playback audio assets directly from the list view.

![Asset List](../docimg/admin/asset-list.png)

Certain parameters are conveniently editable en-masse from the list view itself:  `Submitted`, `Weight`, `Volume`.
Just update for as many assets as you want and hit Save for the changes to take effect.

`Media link url` opens a new browser window with the asset itself contained, whether it be audio, image or text.  Roundware stores
all assets in a publicly accessible directory `http://yourserver/rwmedia`.

Click the Asset id of the Asset you want to view and edit to open the Asset Detail view.  All Project fields are
detailed on the [Asset setup](../setup/asset.html) page.

![Asset Detail](../docimg/admin/asset-detail.png)

It is not currently possible to change the asset file associated with an asset record via the admin, but we hope this functionality will be
available shortly.

NEXT: [`tags`](tag.html)