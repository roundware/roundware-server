# Audio Normalization Unit Tests

This document describes the unit tests created for the audio normalization feature.

## Test Files

### `roundware/api2/tests/test_audio_normalization.py`

This is the main test file containing comprehensive unit tests for the audio normalization functionality. The tests are properly integrated into the existing API2 test structure and will be included when the `run_tests.py` script is executed.

## Test Coverage

The tests cover the following scenarios:

### Core Functionality Tests

1. **`test_normalization_disabled`** - Verifies that normalization is skipped when `AUDIO_NORMALIZATION_ENABLED=False`
2. **`test_normalization_enabled`** - Verifies that normalization is called when `AUDIO_NORMALIZATION_ENABLED=True`
3. **`test_convert_uploaded_file_file_not_found`** - Tests error handling for non-existent files
4. **`test_convert_audio_file_basic`** - Tests basic audio conversion functionality

### Settings Tests

5. **`test_normalize_audio_file_settings`** - Tests that normalization uses correct default settings
6. **`test_normalize_audio_file_custom_settings`** - Tests normalization with custom LUFS and tolerance settings
7. **`test_normalize_audio_file_file_not_found`** - Tests graceful handling of non-existent files

### Integration Tests

8. **`test_speakers_api_integration`** - Tests that the speakers API calls normalization when enabled
9. **`test_speakers_api_integration_disabled`** - Tests that the speakers API skips normalization when disabled

## Running the Tests

### Using the run_tests.py script (Recommended)

```bash
cd /code
python run_tests.py roundware/api2/tests/test_audio_normalization.py -v
```

### Running all API2 tests (includes audio normalization tests)

```bash
cd /code
python run_tests.py -v
```

## Test Configuration

The tests use Django's `@override_settings` decorator to test different configurations:

- **Default settings**: `AUDIO_NORMALIZATION_TARGET_LUFS=-23.0`, `AUDIO_NORMALIZATION_TOLERANCE=2.0`
- **Custom settings**: `AUDIO_NORMALIZATION_TARGET_LUFS=-16.0`, `AUDIO_NORMALIZATION_TOLERANCE=5.0`
- **Disabled**: `AUDIO_NORMALIZATION_ENABLED=False`

## Mocking Strategy

The tests use strategic mocking to isolate the functionality being tested:

- **FFmpeg calls**: Mocked to avoid requiring actual FFmpeg installation
- **File operations**: Mocked to avoid actual file system operations
- **API requests**: Mocked to test integration points

## Test Isolation

Each test:
- Creates its own temporary directory
- Cleans up after itself
- Uses isolated settings overrides
- Doesn't depend on external services

## Continuous Integration

These tests can be integrated into CI/CD pipelines to ensure:

1. **Feature integrity**: Audio normalization continues to work as expected
2. **Regression prevention**: Changes don't break existing functionality
3. **Configuration validation**: Settings work correctly in different environments

## Adding New Tests

To add new tests:

1. Add test methods to the appropriate test class
2. Use `@override_settings` for configuration-specific tests
3. Use `@patch` for mocking external dependencies
4. Follow the existing naming convention: `test_<functionality>_<scenario>`

## Example Test Structure

```python
@override_settings(AUDIO_NORMALIZATION_ENABLED=True)
def test_new_feature(self):
    """Test description"""
    # Setup
    filename = "test_audio.wav"
    self.create_test_audio_file(filename)
    
    # Mock dependencies
    with patch('module.function') as mock_function:
        mock_function.return_value = "expected_result"
        
        # Execute
        result = function_under_test()
        
        # Assert
        mock_function.assert_called_once()
        self.assertEqual(result, "expected_result")
```

## Benefits

These tests provide:

- **Confidence**: Developers can make changes knowing they won't break audio normalization
- **Documentation**: Tests serve as living documentation of expected behavior
- **Debugging**: Failed tests help identify issues quickly
- **Refactoring**: Safe refactoring with confidence that functionality is preserved 