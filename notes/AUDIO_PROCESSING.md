# Audio Processing for Speaker Files

This feature provides comprehensive audio processing for speaker uploads, including aggressive compression and loudness normalization to ensure consistent, professional-quality audio across all speaker files.

## Overview

The audio processing system applies two stages of processing to uploaded speaker audio files:

1. **Audio Compression** - Aggressively flattens dynamics using configurable compressor settings
2. **Loudness Normalization** - Standardizes volume levels using LUFS (Loudness Units relative to Full Scale)

This dual-stage approach ensures that all speaker audio files have consistent perceived loudness and flattened dynamics, creating a professional, uniform listening experience.

## Configuration

Both compression and normalization can be configured through Django settings in `roundware/settings/common.py`:

### Audio Compression Settings

```python
# Audio compression settings
# Enable audio compression for speaker files (default: True)
AUDIO_COMPRESSION_ENABLED = True
# Compression ratio (higher = more aggressive compression, default: 8.0 for very aggressive)
AUDIO_COMPRESSION_RATIO = 8.0
# Compression threshold in dB (default: -30.0 dB for aggressive compression)
AUDIO_COMPRESSION_THRESHOLD = -30.0
# Attack time in milliseconds (default: 1ms for extremely fast response)
AUDIO_COMPRESSION_ATTACK = 1
# Release time in milliseconds (default: 100ms for sustained compression)
AUDIO_COMPRESSION_RELEASE = 100
# Makeup gain in dB to compensate for volume reduction (default: 6.0 dB)
AUDIO_COMPRESSION_MAKEUP_GAIN = 6.0
```

### Audio Normalization Settings

```python
# Audio normalization settings
# Target LUFS level for speaker audio normalization (default: -23 LUFS for broadcast standard)
AUDIO_NORMALIZATION_TARGET_LUFS = -23.0
# Enable audio normalization for speaker files (default: True)
AUDIO_NORMALIZATION_ENABLED = True
# Tolerance range for LUFS (files within this range won't be normalized)
AUDIO_NORMALIZATION_TOLERANCE = 2.0
```

## How It Works

### Processing Pipeline

When a file is uploaded via **any** speaker upload method (API endpoints or Django admin), the system applies the following processing pipeline:

1. **File Upload** → File is saved to media directory
2. **Audio Compression** (if enabled) → Applies aggressive compression to flatten dynamics
3. **Loudness Normalization** (if enabled) → Standardizes volume levels using LUFS
4. **Format Conversion** → Converts to MP3 and M4A formats for web compatibility

### Stage 1: Audio Compression

The compression stage uses FFmpeg's `acompressor` filter with aggressive settings:

- **Threshold**: -30.0 dB (compression starts early, catching quieter peaks)
- **Ratio**: 8:1 (very aggressive - for every 8dB above threshold, only 1dB comes through)
- **Attack**: 1ms (extremely fast response to volume spikes)
- **Release**: 100ms (sustained compression for consistent flattening)
- **Makeup Gain**: 6.0 dB (compensates for volume reduction from compression)

This creates a "punchy" sound with dramatically reduced dynamic range, similar to commercial radio processing.

### Stage 2: Loudness Normalization

The normalization stage uses FFmpeg's `ebur128` and `loudnorm` filters:

- **Target LUFS**: -23.0 LUFS (EBU R128 broadcast standard)
- **Tolerance**: 2.0 LUFS (files within range are skipped)
- **Measurement**: Uses integrated loudness for accurate perceived volume

This ensures all files have consistent perceived loudness regardless of their original recording levels.

## LUFS Standards

Common LUFS targets:
- **-23.0 LUFS**: EBU R128 broadcast standard (default)
- **-16.0 LUFS**: YouTube standard
- **-14.0 LUFS**: Spotify standard
- **-18.0 LUFS**: Netflix standard

## Supported Formats

The processing works with all audio formats supported by FFmpeg, including:
- WAV
- MP3
- M4A/AAC
- FLAC
- OGG
- And many others

## Error Handling

The system includes robust error handling:
- If compression fails, the original file is preserved and processing continues
- If LUFS measurement fails, it falls back to a conservative volume adjustment
- If normalization fails, the original file is preserved and processing continues
- All errors are logged for debugging purposes

## Logging

The audio processing system logs detailed information about its operation:

### Log Levels
- **INFO**: Processing status, successful operations, and skipped files
- **WARNING**: Issues with file probing or measurement
- **ERROR**: Failed processing attempts or system errors
- **DEBUG**: Detailed FFmpeg output and technical details

### Example Log Messages
```
INFO: Audio compression enabled - processing speaker-audio.mp3
INFO: Applying audio compression - File: speaker-audio.mp3, Ratio: 8.0, Threshold: -30.0dB, Attack: 1ms, Release: 100ms, Makeup: 6.0dB
INFO: Successfully compressed speaker-audio.mp3 with aggressive settings
INFO: Audio normalization enabled - processing speaker-audio.mp3
INFO: Audio normalization check - File: speaker-audio.mp3, Current LUFS: -70.0, Target: -23.0, Tolerance: 2.0
INFO: Successfully normalized speaker-audio.mp3 from -70.0 LUFS to target -23.0 LUFS
```

## Testing

### Running Tests

The audio processing system includes comprehensive unit tests:

```bash
# Run all tests (includes audio processing tests)
cd /code
python run_tests.py --reuse-db

# Run specific audio processing tests
python run_tests.py roundware/api2/tests/test_audio_normalization.py -v
```

### Test Coverage

The tests cover:
- **Compression functionality** with various settings
- **Normalization functionality** with different LUFS targets
- **Integration** with both API and admin upload paths
- **Error handling** for various failure scenarios
- **Settings validation** for different configurations

### Test Files

Pre-made test files are available in `files/test-audio/`:
- `soft_audio.wav` (-38.1 LUFS) - Tests normalization UP
- `loud_audio.wav` (-12.0 LUFS) - Tests normalization DOWN  
- `normal_audio.wav` (-20.0 LUFS) - Tests tolerance (should not normalize)

## Performance Considerations

- Processing adds time to file uploads (typically 1-3 seconds per file)
- The system uses temporary files during processing
- **File sizes are preserved** - processing does not significantly increase file size
- Large audio files may take longer to process
- Both features can be disabled entirely if performance is a concern

## File Size Preservation

The processing is designed to preserve reasonable file sizes:
- **Sample rate is maintained** at the original value (typically 44.1kHz)
- **Audio format is preserved** (WAV, MP3, M4A, etc.)
- **Minimal quality degradation** from processing
- **Efficient processing** with optimized FFmpeg settings

## Troubleshooting

If audio processing is not working:

1. Check that FFmpeg is installed and accessible
2. Verify the settings in `roundware/settings/common.py`
3. Check the logs for error messages
4. Ensure the audio file is not corrupted
5. Try with a different audio file to isolate the issue

## Disabling Processing

To disable processing entirely:

```python
# Disable compression
AUDIO_COMPRESSION_ENABLED = False

# Disable normalization
AUDIO_NORMALIZATION_ENABLED = False
```

This will skip the respective processing step while still performing the normal audio conversion to MP3 and M4A formats.

## Advanced Configuration

### For Even More Aggressive Compression

For extremely flat dynamics (similar to commercial radio):

```python
AUDIO_COMPRESSION_RATIO = 12.0
AUDIO_COMPRESSION_THRESHOLD = -40.0
AUDIO_COMPRESSION_ATTACK = 0.5
AUDIO_COMPRESSION_RELEASE = 200
AUDIO_COMPRESSION_MAKEUP_GAIN = 8.0
```

### For Gentler Processing

For more natural-sounding results:

```python
AUDIO_COMPRESSION_RATIO = 3.0
AUDIO_COMPRESSION_THRESHOLD = -18.0
AUDIO_COMPRESSION_ATTACK = 5
AUDIO_COMPRESSION_RELEASE = 50
AUDIO_COMPRESSION_MAKEUP_GAIN = 2.0
```

## Integration Points

The audio processing is integrated into:

1. **API Uploads** - `roundware/lib/api.py` → `save_speaker_from_request()`
2. **Admin Uploads** - `roundware/rw/file_utils.py` → `handle_speaker_audio_upload()`
3. **Admin Form Uploads** - `roundware/rw/admin_upload.py` → `SpeakerUploadForm`

All upload paths now include the complete compression → normalization → conversion pipeline.
