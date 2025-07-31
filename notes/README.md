# Audio Normalization Feature Notes

This directory contains documentation for the audio normalization feature added to Roundware.

## Files

- **`AUDIO_NORMALIZATION.md`** - Complete feature documentation including configuration, usage, and troubleshooting
- **`AUDIO_NORMALIZATION_TESTS.md`** - Test documentation and instructions for running the unit tests

## Quick Reference

- **Feature**: Automatic audio volume normalization for speaker files
- **Target LUFS**: -23.0 (EBU R128 broadcast standard)
- **Tolerance**: ±2.0 LUFS
- **Test Files**: `files/test-audio/` (soft_audio.wav, loud_audio.wav, normal_audio.wav)
- **Tests**: `roundware/api2/tests/test_audio_normalization.py`

## Implementation

- **Main Code**: `roundware/lib/convertaudio.py` (normalize_audio_file function)
- **Settings**: `roundware/settings/common.py` (AUDIO_NORMALIZATION_* settings)
- **Integration**: Called from `convert_uploaded_file()` for speaker API uploads 