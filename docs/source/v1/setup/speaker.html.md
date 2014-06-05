---
page_title: "Speakers"
sidebar_current: "setup-speaker"
---


# Speaker

<div class="alert alert-block alert-info">
    <p>
        <strong>DEFINITION:</strong> A geo-located object that continuously broadcasts audio within a specified area.
    </p>
</div>

Every project - even if geo\_listen is not enabled - must have at least one active speaker in order to generate audio streams.  If geo\_listen=N, the latitude, longitude and radius of the speaker are ignored, but if geo\_listen=Y, then the latitude, longitude and radius determine where in the physical world the audio associated with the speaker can be heard.

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
            <td>Project</td>
            <td>picklist</td>
            <td>which project is Speaker associated with</td>
            <td></td>
        </tr>
        <tr>
            <td>Activeyn</td>
            <td>boolean</td>
            <td>active/inactive</td>
            <td></td>
        </tr>
        <tr>
            <td>Code</td>
            <td>string</td>
            <td>short code to remember which speaker is which</td>
            <td>particularly useful in projects with lots of speakers</td>
        </tr>
        <tr>
            <td>Latitude/Longitude</td>
            <td>float</td>
            <td>central point of speaker range</td>
            <td></td>
        </tr>
        <tr>
            <td>Maxdistance</td>
            <td>integer/meters</td>
            <td>distance from speaker center point at which volume is attenuated to Minvolume</td>
            <td>generally speaking, volume attenuates as listeners get further and further from the center point of the speaker, though there is no reason this needs to always hold true</td>
        </tr>
        <tr>
            <td>Mindistance</td>
            <td>integer/meters</td>
            <td>distance from speaker center point at which volume begins to attenuate from Maxvolume towards Minvolume</td>
            <td>all points closer to the center of the speaker range than Mindistance will have volume Maxvolume</td>
        </tr>
        <tr>
            <td>Maxvolume</td>
            <td>float</td>
            <td>highest volume level, typically at the center of a speaker’s range</td>
            <td>1.0 means no attenuation from original volume of source material</td>
        </tr>
        <tr>
            <td>Minvolume</td>
            <td>float</td>
            <td>lowest volume level; in effect at all distances greater than Maxdistance</td>
            <td></td>
        </tr>
        <tr>
            <td>Uri</td>
            <td>string/url format</td>
            <td>mountpoint of audio to be played in association with speaker</td>
            <td></td>
        </tr>
        <tr>
            <td>Backupuri</td>
            <td>string/url format</td>
            <td>mountpoint of audio to be played in association with speaker if primary Uri is not accessible for any reason</td>
            <td>useful when primary uri is a live generated stream which has a higher failure rate</td>
        </tr>
    </tbody>
</table>