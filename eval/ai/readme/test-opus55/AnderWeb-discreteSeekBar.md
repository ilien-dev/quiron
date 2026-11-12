# discreteSeekBar

A lightweight Android seek bar that snaps to discrete values and shows a floating indicator with the current value while the user drags the thumb.

The stock `SeekBar` works well for continuous input like volume or brightness. Many settings, though, only accept a fixed set of values: a rating from 1 to 5, a font size in steps of 2, or a timer in 15-minute increments. discreteSeekBar is built for those cases. It keeps the familiar slider interaction, enforces valid steps, and gives clear visual feedback so users always know which value they are about to select.

## Features

- **Discrete steps.** Define a minimum, a maximum, and a step size. The thumb snaps to the nearest valid value on release.
- **Floating value indicator.** A bubble rises above the thumb during a drag and shows the current value. It hides when the user lets go.
- **Custom value formatting.** Display `3` as `3 stars`, `30` as `0:30`, or anything else through a simple formatter interface.
- **Tick marks.** You can draw a mark at each step so the available positions are visible before the user touches the control.
- **Theming.** Colors for the track, progress, thumb, ticks and indicator can be set in XML or code, and they default to your app's theme accent color.
- **Accessibility.** The control reports its range and current value to TalkBack and responds to accessibility increment and decrement actions.
- **Keyboard and D-pad support.** Arrow keys move one step at a time, which helps on TV and Chromebook devices.
- **RTL aware.** The control mirrors its layout correctly in right-to-left locales.
- **No extra dependencies** beyond AndroidX core.

## Installation

Add the repository and dependency to your module's `build.gradle`:

```groovy
dependencies {
    implementation "<group-id>:discreteseekbar:<version>"
}
```

Replace `<group-id>` and `<version>` with the coordinates from the latest release. The minimum supported SDK is listed in the library's `build.gradle`.

## Quick start

Declare the view in your layout:

```xml
<com.example.discreteseekbar.DiscreteSeekBar
    android:id="@+id/rating"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:dsb_min="1"
    app:dsb_max="5"
    app:dsb_step="1"
    app:dsb_value="3"
    app:dsb_showTicks="true" />
```

Then listen for changes in your activity or fragment:

```kotlin
val rating = findViewById<DiscreteSeekBar>(R.id.rating)

rating.setOnValueChangeListener { seekBar, value, fromUser ->
    if (fromUser) {
        viewModel.updateRating(value)
    }
}
```

## Formatting the indicator

By default the indicator shows the raw integer value. To change that, supply a formatter:

```kotlin
rating.valueFormatter = DiscreteSeekBar.ValueFormatter { value ->
    if (value == 1) "1 star" else "$value stars"
}
```

Keep formatted strings short. The indicator resizes to fit its text, but long labels can crowd the screen on narrow devices.

## XML attributes

| Attribute | Type | Default | Description |
|---|---|---|---|
| `dsb_min` | integer | `0` | Lowest selectable value |
| `dsb_max` | integer | `100` | Highest selectable value |
| `dsb_step` | integer | `1` | Distance between valid values |
| `dsb_value` | integer | `dsb_min` | Initial value |
| `dsb_showTicks` | boolean | `false` | Draw a mark at each step |
| `dsb_indicatorEnabled` | boolean | `true` | Show the floating bubble while dragging |
| `dsb_trackColor` | color | theme | Color of the inactive track |
| `dsb_progressColor` | color | accent | Color of the active track |
| `dsb_thumbColor` | color | accent | Color of the thumb |
| `dsb_indicatorColor` | color | accent | Background of the value bubble |
| `dsb_indicatorTextAppearance` | style | built-in | Text style inside the bubble |

Every attribute has a matching property in code, so you can change the range or colors at runtime.

## Listening to drag events

If you need to know when a drag starts and ends, for example to pause a preview, implement the full listener:

```kotlin
rating.setOnSeekBarChangeListener(object : DiscreteSeekBar.OnSeekBarChangeListener {
    override fun onValueChanged(seekBar: DiscreteSeekBar, value: Int, fromUser: Boolean) { }
    override fun onStartTrackingTouch(seekBar: DiscreteSeekBar) { }
    override fun onStopTrackingTouch(seekBar: DiscreteSeekBar) { }
})
```

## Saving state

The view saves and restores its current value across configuration changes automatically, as long as it has an `android:id`. If you hold the value in a ViewModel, set it back on the view after it is recreated and treat the ViewModel as the source of truth.

## Sample app

The `sample` module shows common setups: a star rating, a stepped font-size picker, a time selector with custom formatting, and a fully themed variant. Run it from Android Studio to try each configuration on a device or emulator.

## Contributing

Bug reports and pull requests are welcome. Before opening a pull request:

1. Open an issue to discuss larger changes first.
2. Follow the existing code style. The project uses the default Kotlin conventions.
3. Add or update tests for any behavior change.
4. Run `./gradlew check` and make sure it passes.

When reporting a bug, include the library version, device model, Android version, and a minimal layout or code snippet that reproduces it.

## License

discreteSeekBar is released under the Apache License 2.0. See [LICENSE](LICENSE) for the full text.
