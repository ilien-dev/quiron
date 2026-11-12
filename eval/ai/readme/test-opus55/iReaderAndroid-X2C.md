# X2C

**Increase layout loading speed 200%**

X2C is a compile-time tool for Android that turns your XML layouts into plain Java code. You keep writing layouts in XML with full IDE preview support. At runtime, X2C skips XML parsing and reflection and builds your views directly with `new`. The result is much faster inflation, especially for complex screens and list items.

---

## Why X2C?

Android's `LayoutInflater` is flexible, but every `inflate()` call has to do a lot of work:

1. **I/O.** The binary XML resource is read from the APK.
2. **Parsing.** An `XmlPullParser` walks the document tag by tag.
3. **Reflection.** Each tag name is resolved to a class and instantiated with `Constructor.newInstance()`.
4. **Attribute resolution.** Every attribute goes through `TypedArray` lookups.

Each step is small, but together they add up on deep hierarchies, in `RecyclerView` adapters that inflate many items, and on low-end devices. Slow inflation shows up as longer cold starts, dropped frames during scrolling, and a sluggish first draw.

X2C moves that work to build time. An annotation processor reads your layout XML during compilation and generates equivalent Java code that constructs the view tree directly. No parsing, no reflection, no attribute lookups at runtime.

---

## Features

- **Up to 200% faster inflation.** Layouts load in roughly a third of the original time, depending on layout complexity and device.
- **Keep your XML.** Layouts remain the source of truth, so Android Studio preview, the Layout Editor, and lint all keep working.
- **Automatic fallback.** If a layout can't be converted, X2C falls back to `LayoutInflater`, so your app never breaks.
- **Drop-in API.** Replace `setContentView` and `LayoutInflater.inflate` with one-line X2C equivalents.
- **No runtime reflection.** Generated code is easier to optimize and works cleanly with R8 and ProGuard.
- **Standard views and attributes.** Common widgets, layout params, margins, padding, backgrounds, text styling, and more are supported out of the box.

---

## Installation

Add the dependencies to your module's `build.gradle`:

```groovy
dependencies {
    implementation 'com.example.x2c:x2c-lib:<version>'
    annotationProcessor 'com.example.x2c:x2c-apt:<version>'
}
```

For Kotlin projects, use `kapt` in place of `annotationProcessor`:

```groovy
apply plugin: 'kotlin-kapt'

dependencies {
    implementation 'com.example.x2c:x2c-lib:<version>'
    kapt 'com.example.x2c:x2c-apt:<version>'
}
```

Replace `<version>` with the latest release from the Releases page.

---

## Quick Start

### 1. Annotate the layouts you want converted

Add `@Xml` to any class, such as your Activity, Fragment, or Adapter, and list the layouts to compile:

```java
@Xml(layouts = {"activity_main", "item_feed"})
public class MainActivity extends AppCompatActivity {
    // ...
}
```

Only the layouts you list are converted. This keeps the generated code small and lets you adopt X2C one screen at a time.

### 2. Replace your inflation calls

**Activities:**

```java
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    X2C.setContentView(this, R.layout.activity_main);
}
```

**Fragments and adapters:**

```java
View view = X2C.inflate(context, R.layout.item_feed, parent, false);
```

### 3. Build

Run a normal build. The annotation processor generates one class per layout under `build/generated/`. When X2C has generated code for a layout, the API calls it. Otherwise, the API falls back to `LayoutInflater`.

---

## How It Works

At compile time, the X2C annotation processor:

1. Finds every `@Xml` annotation and collects the requested layout names.
2. Locates and parses the matching XML files in your `res/layout` directories.
3. Maps each tag and attribute to the matching Java constructor and setter calls.
4. Writes a generated class that builds the full view tree.
5. Registers the class in a lookup table keyed by layout resource ID.

For example, this layout:

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textSize="18sp" />
</LinearLayout>
```

becomes code along these lines:

```java
LinearLayout root = new LinearLayout(ctx);
root.setOrientation(LinearLayout.VERTICAL);
int pad = (int) TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_DIP, 16, res.getDisplayMetrics());
root.setPadding(pad, pad, pad, pad);

TextView title = new TextView(ctx);
title.setId(R.id.title);
title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18);
root.addView(title, new LinearLayout.LayoutParams(
        ViewGroup.LayoutParams.WRAP_CONTENT,
        ViewGroup.LayoutParams.WRAP_CONTENT));
```

At runtime, `X2C.inflate()` looks up the generated class by resource ID and calls it directly.

---

## Performance

Gains depend on layout depth, view count, and device class. The biggest improvements tend to appear in these cases:

| Scenario | Typical improvement |
|---|---|
| Simple layout (fewer than 10 views) | Modest |
| Medium layout (10–40 views) | Significant |
| Complex layout or nested hierarchy | Up to ~3× faster |
| `RecyclerView` items inflated repeatedly | Large cumulative savings |

To measure the effect on your app, wrap inflation calls with `SystemClock.elapsedRealtimeNanos()` or use Android Studio's CPU Profiler with and without X2C. A benchmark module is included in `sample/` so you can compare results on your own devices.

---

## Limitations

X2C covers the most common layout features, but some XML constructs can't be fully expressed as static code. When X2C finds an unsupported construct, it skips that layout and falls back to `LayoutInflater`.

- **`<merge>` and `<include>`.** Supported for basic cases. Complex attribute overrides on `<include>` may fall back.
- **Data Binding.** Layouts wrapped in `<layout>` tags are not converted.
- **Theme and style attributes.** `?attr/` references are resolved at runtime through the context theme, which is slightly slower than literal values.
- **Custom views.** Supported if they expose a `(Context)` constructor and public setters for their attributes. Custom attributes declared in `attrs.xml` may need a mapping.
- **Resource qualifiers.** Generated code is created per layout variant, so `layout-land`, `layout-sw600dp`, and similar folders each produce their own class. This increases method count slightly.
- **Compose.** X2C is designed for the View system and has no effect on Jetpack Compose UI.

---

## ProGuard / R8

The library ships with consumer rules, so no extra configuration is usually needed. If you've customized shrinking aggressively, keep the generated classes:

```proguard
-keep class com.example.x2c.generated.** { *; }
```

---

## FAQ

**Will this break my layout preview?**
No. Your XML is unchanged, so the preview works as it always has.

**What happens if I edit a layout?**
The next build regenerates the code automatically.

**Does it increase APK size?**
Slightly, because each converted layout adds a small class. Convert only performance-critical layouts to keep the overhead minimal.

**Can I use it with view binding?**
Yes. Generated views keep their IDs, so `findViewById` and view binding's `bind(view)` both work as expected.

---

## Contributing

Bug reports, feature requests, and pull requests are welcome. Please include a minimal layout that reproduces the issue, and add tests for new attribute mappings.

---

## License

X2C is released under the Apache License 2.0. See [LICENSE](LICENSE) for details.
