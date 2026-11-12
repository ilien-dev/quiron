# ProgressWheel

A progress wheel for Android, intended for use instead of the standard progress bar.

## Overview

ProgressWheel is a lightweight, customizable circular progress indicator. It replaces the horizontal progress bar with a wheel that fits naturally into modern interfaces. You can declare it in an XML layout or create it in code. It has no dependencies beyond the Android SDK.

## Features

- **Indeterminate mode:** a continuously spinning wheel for tasks of unknown length
- **Determinate mode:** show exact progress from 0 to 100 percent
- **Smooth animation:** progress changes are interpolated rather than jumping
- **Customizable appearance:** colors, bar width, radius, and rim
- **Optional text:** display a label or percentage in the center
- **State restoration:** progress survives configuration changes such as rotation
- **Small footprint:** a single custom view and a few attributes

## Installation

Copy the library module into your project and add it as a dependency.

```groovy
// settings.gradle
include ':progresswheel'

// app/build.gradle
dependencies {
    implementation project(':progresswheel')
}
```

## Usage

### XML

```xml
<com.example.progresswheel.ProgressWheel
    android:id="@+id/progress_wheel"
    android:layout_width="80dp"
    android:layout_height="80dp"
    app:pwBarColor="#2196F3"
    app:pwBarWidth="6dp"
    app:pwRimColor="#E0E0E0"
    app:pwRimWidth="2dp" />
```

### Java

```java
ProgressWheel wheel = findViewById(R.id.progress_wheel);

// Unknown duration
wheel.spin();

// Known progress, from 0.0 to 1.0
wheel.setProgress(0.75f);

// Stop spinning and hide the wheel when finished
wheel.stopSpinning();
```

### Kotlin

```kotlin
val wheel = findViewById<ProgressWheel>(R.id.progress_wheel)
wheel.setProgress(0.5f)
```

## Attributes

| Attribute | Description | Default |
|-----------|-------------|---------|
| `pwBarColor` | Color of the moving bar | `#2196F3` |
| `pwBarWidth` | Thickness of the bar | `4dp` |
| `pwRimColor` | Color of the background rim | `#33000000` |
| `pwRimWidth` | Thickness of the rim | `2dp` |
| `pwRadius` | Radius of the wheel | fits view |
| `pwSpinSpeed` | Rotation speed while spinning | `230` |
| `pwText` | Text displayed in the center | none |
| `pwTextColor` | Color of the center text | `#000000` |

## Tips

- Use the indeterminate mode while waiting for a network response, and switch to determinate mode once you can report real progress.
- Keep the view square. A wheel inside a non-square layout will be sized to the smaller dimension.
- Call `stopSpinning()` in `onPause()` so the animation does not run while the screen is hidden.

## Requirements

- Android API level 14 or higher
- Android Studio with Gradle

## Contributing

Contributions are welcome. To get started:

1. Fork the repository.
2. Create a branch for your change.
3. Make your changes and test them on a device or emulator.
4. Open a pull request describing what you changed and why.

Please keep changes focused and follow the existing code style. Bug reports and feature requests can be filed as issues.

## License

Released under the Apache License 2.0. See the `LICENSE` file for details.
