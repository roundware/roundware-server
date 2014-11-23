---
page_title: "Audiotrack"
sidebar_current: "setup-audiotrack"
---


# Audiotrack

<div class="alert alert-block alert-info">
	<p>
		<strong>DEFINITION:</strong> A linear assemblage of audio assets and silence (‘dead air’) which dynamically forms part of each stream by incorporating audio assets into the stream. There can be multiple audiotracks for each project and they determine how many audio assets can play simultaneously.
	</p>
</div>

Audiotracks provide the ability to aesthetically tune the audio experience by allowing administrators to control how many assets are allowed to play simultaneously, how frequently assets play as well as panning and volume considerations.

<br>

## Fields

<!-- table table-hover table-bordered mr-types -->
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
            <td>which project is Audiotrack associated with</td>
            <td>the number of Audiotracks created determines the highest number of assets ever played simultaneously</td>
        </tr>
        <tr>
            <td>Maxvolume</td>
            <td>float</td>
            <td>upper value for range of randomized volume attenuation to be applied to each asset when played back in stream</td>
            <td>1.0 means no attenuation from original volume of source material.  A range of 0.0-1.0 would mean each asset would be attenuated somewhere between silence and full source volume</td>
        </tr>
        <tr>
            <td>Minvolume</td>
            <td>float</td>
            <td>Upper value for range of randomized volume attenuation to be applied to each asset when played back in stream</td>
            <td></td>
        </tr>
        <tr>
            <td>Minduration</td>
            <td>integer/nanoseconds</td>
            <td>minimum length of time each asset in Audiotrack will play</td>
            <td>assets with shorter lengths than this value will be played in the entirety every time</td>
        </tr>
        <tr>
            <td>Maxduration</td>
            <td>integer/nanoseconds</td>
            <td>maximum length of time each asset in Audiotrack will play</td>
            <td>assets longer than this value will never be played in entirety</td>
        </tr>
        <tr>
            <td>Mindeadair</td>
            <td>integer/nanoseconds</td>
            <td>minimum length of pause between consecutive assets in Audiotrack</td>
            <td>if set to 0, assets can play with no pause between them</td>
        </tr>
        <tr>
            <td>Maxdeadair</td>
            <td>integer/nanoseconds</td>
            <td>maximum length of pause between consecutive assets in Audiotrack</td>
            <td>RW randomly chooses a value between Min and Max deadair each time a new assets is selected to play in the stream</td>
        </tr>
        <tr>
            <td>Minfadeintime</td>
            <td>integer/nanoseconds</td>
            <td>minimum length of time over which an asset fades in at the beginning of playback from 0 volume to its max volume (determined by Max/Minvolume values)</td>
            <td></td>
        </tr>
        <tr>
            <td>Maxfadeintime</td>
            <td>integer/nanoseconds</td>
            <td>maximum length of time over which an asset fades in from 0 volume to its max volume (determined by Max/Minvolume values)</td>
            <td></td>
        </tr>
        <tr>
            <td>Minfadeouttime</td>
            <td>integer/nanoseconds</td>
            <td>minimum length of time over which an asset fades out at the end of its playback from its max volume (determined by Max/Minvolume values) to 0 volume</td>
            <td></td>
        </tr>
        <tr>
            <td>Maxfadeouttime</td>
            <td>integer/nanoseconds</td>
            <td>maximum length of time over which an asset fades out from its max volume (determined by Max/Minvolume values) to 0 volume</td>
            <td></td>
        </tr>
        <tr>
            <td>Min Pan Position</td>
            <td>float</td>
            <td>furthest left position in stereo field to which asset can be panned automatically</td>
            <td>-1.0 is hard pan left; 1.0 is hard pan right</td>
        </tr>
        <tr>
            <td>Max Pan Position</td>
            <td>float</td>
            <td>furthest right position in stereo field to which asset can be panned automatically</td>
            <td>to turn off panning, set both min/max pan positions to the same value. this will enforce every asset to remain at that value for its entire playback</td>
        </tr>
        <tr>
            <td>Min Pan Duration</td>
            <td>integer/nanoseconds</td>
            <td>minimum length of time asset will be automatically panned between two randomly selected pan positions within the pan range defined by min/max pan position</td>
            <td>assets are continually panned during playback.  as soon as one pan ramp completes, a new one is calculated and begun.</td>
        </tr>
        <tr>
            <td>Max Pan Duration</td>
            <td>integer/nanoseconds</td>
            <td>maximum length of time asset will be automatically panned between two randomly selected pan positions within the pan range defined by min/max pan position</td>
            <td></td>
        </tr>
        <tr>
            <td>Repeat Recordings</td>
            <td>boolean</td>
            <td>determines whether or not recordings can be played more than once sans server receiving a modify_stream request</td>
            <td></td>
        </tr>
    </tbody>
</table>


