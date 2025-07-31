# Audio Normalization Test Files

These files are specifically created for testing the audio normalization feature in Roundware.

## Test Files

### `soft_audio.wav` (431KB)
- **Original LUFS**: -38.1 LUFS (very quiet)
- **Purpose**: Test normalization UP to target level
- **Expected Result**: Should be normalized to ~-23.0 LUFS (much louder)

### `loud_audio.wav` (431KB)  
- **Original LUFS**: -12.0 LUFS (very loud)
- **Purpose**: Test normalization DOWN to target level
- **Expected Result**: Should be normalized to ~-23.0 LUFS (quieter)

### `normal_audio.wav` (431KB)
- **Original LUFS**: -20.0 LUFS (normal volume)
- **Purpose**: Test that files within tolerance are not normalized
- **Expected Result**: Should remain ~-20.0 LUFS (within tolerance of -23.0 ± 2.0)

## Normalization Settings

- **Target LUFS**: -23.0 (EBU R128 broadcast standard)
- **Tolerance**: ±2.0 LUFS (acceptable range: -25.0 to -21.0 LUFS)
- **Enabled by default**: Yes

## Usage

Upload these files via the Roundware speakers API to test the audio normalization feature:

1. **POST** to `/api/2/speakers/` with the audio file
2. Check server logs for normalization messages
3. Download the processed file and verify volume changes
4. Measure final LUFS using: `ffmpeg -i file.wav -af ebur128=peak=true:dualmono=true -f null - 2>&1 | grep "I:" | tail -1`

## File Generation

These files were created using FFmpeg with sine wave generation and volume adjustment:

```bash
# Soft audio (quiet)
ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" -af "volume=0.1" soft_audio.wav

# Loud audio (loud)  
ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" -af "volume=2.0" loud_audio.wav

# Normal audio (medium)
ffmpeg -f lavfi -i "sine=frequency=1000:duration=5" -af "volume=0.8" normal_audio.wav
``` 