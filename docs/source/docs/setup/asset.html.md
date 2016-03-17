---
page_title: "Assets"
sidebar_current: "setup-asset"
---


# Asset

<div class="alert alert-block alert-info">
    <p>
        <strong>DEFINITION:</strong> An individual piece of media contributed by a user or administrator.  Roundware currently handles audio, photo and text assets and will soon handle video assets as well.  Assets are assigned many pieces of metadata, including a project, tags, location, and others.
    </p>
</div>

<br>

## Fields

<table class="table table-striped table-bordered mr-types">
    <thead>
        <tr>
            <th>Parameter</th>
            <th>Format/Units</th>
            <th>Definition</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Mediatype</td>
            <td>picklist</td>
            <td>what type of media?</td>
            <td>options are: audio, video, photo, text, though video is still under development</td>
        </tr>
        <tr>
            <td>Media Display</td>
            <td>audio player</td>
            <td>allows for playback of audio</td>
            <td>only present for assets of mediatype=audio</td>
        </tr>
        <tr>
            <td>File</td>
            <td>binary file</td>
            <td>actual media file of asset</td>
            <td>currently this field should not be edited via the admin as it does not function properly</td>
        </tr>
        <tr>
            <td>Volume</td>
            <td>float</td>
            <td>asset-specific volume attenuation; 1.0 = no attenuation</td>
            <td>this can be used to compensate if the recording level of an asset is particulary high or low</td>
        </tr>
        <tr>
            <td>Audio File Length</td>
            <td>nanoseconds</td>
            <td>length of the audio recording</td>
            <td>Gstreamer uses nanoseconds as units, to Roundware does as well</td>
        </tr>
        <tr>
            <td>Description</td>
            <td>text</td>
            <td>descriptive info for an asset; can be private or displayed in the client if desired</td>
            <td></td>
        </tr>
        <tr>
            <td>Loc Description</td>
            <td>multi-select</td>
            <td>localized descriptive info</td>
            <td></td>
        </tr>
        <tr>
            <td>Project</td>
            <td>picklist</td>
            <td>every asset is assigned to a Project</td>
            <td></td>
        </tr>
        <tr>
            <td>Language</td>
            <td>picklist</td>
            <td>uses the standard Roundware localization functions</td>
            <td>audio asset playback in streams is determined by the language setting of the client device with a default of English</td>
        </tr>
        <tr>
            <td>Session</td>
            <td>integer</td>
            <td>session during which the asset was recorded and uploaded</td>
            <td>if asset uploaded via the Admin, the session id defaults to -10 (or whatever value is specified in settings.py</td>
        </tr>
        <tr>
            <td>Created</td>
            <td>datetime</td>
            <td>time stamp when the asset record was created</td>
            <td></td>
        </tr>
        <tr>
            <td>Weight</td>
            <td>picklist</td>
            <td>prioritization value to determine order of playback within stream when using 'by_weight' ordering</td>
            <td>this value is ignored in the standard 'random' ordering scenario</td>
        </tr>
        <tr>
            <td>Submitted</td>
            <td>boolean</td>
            <td>whether or not the asset is active in the system</td>
            <td>this is a useful way of keeping assets in the system while not having them used in playback</td>
        </tr>
        <tr>
            <td>Tags</td>
            <td>multi-select</td>
            <td>tag metadata assignments for asset</td>
            <td></td>
        </tr>
        <tr>
            <td>Latitude/Longitude</td>
            <td>float</td>
            <td>location of asset in the real world</td>
            <td></td>
        </tr>
        <tr>
            <td>Related Envelope</td>
            <td>picklist</td>
            <td>assets are associated with an envelope, allowing for them to be grouped together</td>
            <td></td>
        </tr>
        <tr>
            <td>Votes</td>
            <td>inline</td>
            <td>votes collected from users pertaining to asset</td>
            <td>typical vote types are 'like', 'flag', or 'rating'</td>
        </tr>
    </tbody>
</table>