# Audio Normalization for Speaker Files

This feature automatically normalizes the volume levels of audio files uploaded to the speakers API endpoints to ensure consistent loudness across all speaker audio files.

## Overview

The audio normalization system uses the LUFS (Loudness Units relative to Full Scale) standard to measure and adjust audio levels. This ensures that all speaker audio files have consistent perceived loudness, preventing some files from being significantly louder or softer than others.

## Configuration

The normalization can be configured through Django settings in `roundware/settings/common.py`:

```python
# Audio normalization settings
# Target LUFS level for speaker audio normalization (default: -23 LUFS for broadcast standard)
AUDIO_NORMALIZATION_TARGET_LUFS = -23.0
# Enable audio normalization for speaker files (default: True)
AUDIO_NORMALIZATION_ENABLED = True
# Tolerance range for LUFS (files within this range won't be normalized)
AUDIO_NORMALIZATION_TOLERANCE = 2.0
```

### Settings Explanation

- **AUDIO_NORMALIZATION_TARGET_LUFS**: The target LUFS level for all audio files. Default is -23.0 LUFS, which is the EBU R128 broadcast standard.
- **AUDIO_NORMALIZATION_ENABLED**: Enable or disable the normalization feature entirely.
- **AUDIO_NORMALIZATION_TOLERANCE**: Files within this range of the target LUFS won't be normalized to avoid unnecessary processing.

## How It Works

1. When a file is uploaded via the POST `/api/2/speakers/` or PATCH `/api/2/speakers/:id/` endpoints, the system checks if normalization is enabled.

2. If enabled, the system:
   - Measures the current LUFS level of the uploaded audio file using FFmpeg's `ebur128` filter
   - Compares it to the target LUFS level
   - If the difference is greater than the tolerance, applies normalization using FFmpeg's `loudnorm` filter
   - Replaces the original file with the normalized version
   - Continues with the normal conversion process (to MP3 and M4A formats)

3. The normalization preserves the original filename and location, only adjusting the audio levels.

## LUFS Standards

Common LUFS targets:
- **-23.0 LUFS**: EBU R128 broadcast standard (default)
- **-16.0 LUFS**: YouTube standard
- **-14.0 LUFS**: Spotify standard
- **-18.0 LUFS**: Netflix standard

## Supported Formats

The normalization works with all audio formats supported by FFmpeg, including:
- WAV
- MP3
- M4A/AAC
- FLAC
- OGG
- And many others

## Error Handling

The system includes robust error handling:
- If LUFS measurement fails, it falls back to a conservative volume adjustment
- If normalization fails, the original file is preserved and processing continues
- All errors are logged for debugging purposes

## Logging

The audio normalization process logs detailed information about its operation:

### Log Levels
- **INFO**: Normalization checks, successful operations, and skipped files
- **WARNING**: Issues with file probing or LUFS measurement
- **ERROR**: Failed normalization attempts or system errors
- **DEBUG**: Detailed FFmpeg output and technical details

### Example Log Messages
```
INFO: Audio normalization enabled - processing soft_audio.wav
INFO: Audio normalization check - File: soft_audio.wav, Current LUFS: -38.1, Target: -23.0, Tolerance: 2.0
INFO: Successfully normalized soft_audio.wav from -38.1 LUFS to target -23.0 LUFS
INFO: Audio file normal_audio.wav is within tolerance range, skipping normalization
```

## Testing

To test the normalization feature:

1. Upload audio files with different volume levels via the speakers API
2. Check the server logs for normalization messages (see Logging section above)
3. Download the processed files and compare volume levels
4. Use FFmpeg to measure LUFS values: `ffmpeg -i file.wav -af ebur128=peak=true:dualmono=true -f null - 2>&1 | grep "I:" | tail -1`

### Test Files

Pre-made test files are available in `files/test-audio/`:
- `soft_audio.wav` (-38.1 LUFS) - Tests normalization UP
- `loud_audio.wav` (-12.0 LUFS) - Tests normalization DOWN  
- `normal_audio.wav` (-20.0 LUFS) - Tests tolerance (should not normalize)

See `files/test-audio/NORMALIZATION_TEST_FILES.md` for detailed usage instructions.

## Performance Considerations

- Normalization adds processing time to file uploads
- The system uses temporary files during processing
- **File sizes are preserved** - normalization does not increase file size
- Large audio files may take longer to process
- The feature can be disabled entirely if performance is a concern

## File Size Preservation

The normalization process is designed to preserve the original file size:
- **Sample rate is maintained** at the original value (typically 44.1kHz)
- **Audio format is preserved** (WAV, MP3, M4A, etc.)
- **No quality degradation** from unnecessary re-encoding
- **Efficient processing** with minimal storage impact

## Troubleshooting

If normalization is not working:

1. Check that FFmpeg is installed and accessible
2. Verify the settings in `roundware/settings/common.py`
3. Check the logs for error messages
4. Ensure the audio file is not corrupted
5. Try with a different audio file to isolate the issue

## Disabling Normalization

To disable normalization entirely, set:

```python
AUDIO_NORMALIZATION_ENABLED = False
```

This will skip the normalization step while still performing the normal audio conversion to MP3 and M4A formats. 