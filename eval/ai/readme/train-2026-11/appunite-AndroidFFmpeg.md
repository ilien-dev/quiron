# AndroidFFmpeg

> **DEPRECATED**: This repository is no longer maintained and is kept for historical reference only. No further updates, bug fixes, or security patches will be provided. See [Alternatives](#alternatives) before starting anything new.

FFmpeg build scripts for Android across multiple CPU architectures, with an example JNI wrapper showing how to call FFmpeg from Java.

## Overview

AndroidFFmpeg cross-compiles FFmpeg with the Android NDK and produces native libraries for several ABIs. This lets a single app ship media processing (transcoding, remuxing, trimming, frame extraction) on a wide range of devices. A small example project demonstrates how to expose FFmpeg to application code through JNI.

## Features

- Cross-compilation of FFmpeg for `armeabi-v7a`, `arm64-v8a`, `x86`, and `x86_64`
- Configurable build flags, so you can enable only the codecs, muxers, demuxers, and filters you need
- Per-ABI output folders that drop straight into an Android project
- Example JNI layer with a Java wrapper class
- Sample app showing how to load the libraries and invoke FFmpeg

## Why this project is deprecated

The project was written against toolchains and conventions that have since changed significantly:

- It targets older NDK releases and the legacy standalone-toolchain workflow, which modern NDKs no longer support.
- The bundled FFmpeg version is outdated and does not include upstream security fixes.
- The example uses `ndk-build` and `Android.mk` conventions rather than current Gradle and CMake tooling.
- Newer Android requirements, such as 64-bit enforcement, 16 KB page size support, and scoped storage, are not addressed.

Using this code in a production app is **not recommended**.

## Requirements

For reference, the original setup needed:

- A Unix-like build host (Linux or macOS; Windows via WSL)
- Android NDK (an older release matching the scripts)
- Android SDK and Android Studio for the sample app
- FFmpeg source code, fetched by the build script or placed manually
- Standard build tools: `make`, `bash`, `pkg-config`, `yasm` or `nasm`

## Building

1. Clone the repository and download the FFmpeg source into the expected directory.
2. Set the NDK path:
   ```bash
   export NDK_HOME=/path/to/android-ndk
   ```
3. Edit the build script to choose target ABIs and FFmpeg configure options.
4. Run the build:
   ```bash
   ./build_all.sh
   ```
5. Find the resulting libraries and headers in the per-ABI output directories.

Script names and paths may differ from those shown here. Check the repository contents for the exact layout.

## Using the JNI example

1. Copy the generated `.so` files into your app's `jniLibs/<abi>/` folders.
2. Copy the headers into your native source tree.
3. Build the JNI wrapper alongside your app.
4. Load the libraries in Java and call the wrapper:
   ```java
   static {
       System.loadLibrary("avutil");
       System.loadLibrary("avcodec");
       System.loadLibrary("avformat");
       System.loadLibrary("ffmpegjni");
   }
   ```
   Library names and load order depend on which components you built.

Run FFmpeg work on a background thread, since transcoding is long-running and will block the UI otherwise.

## Licensing

FFmpeg is licensed under LGPL v2.1 or later, or GPL v2 or later, depending on the configure options you choose. Enabling GPL components or non-free codecs changes your distribution obligations. If you ship FFmpeg in an app, you are responsible for complying with the license, including providing source or relinking ability where required for LGPL builds. Review the [FFmpeg legal page](https://ffmpeg.org/legal.html) before distributing.

Code in this repository that is not part of FFmpeg is provided as-is, without warranty.

## Alternatives

For new projects, consider actively maintained options:

- Building FFmpeg directly with a current NDK and CMake or Gradle integration
- Maintained community FFmpeg wrappers for Android (check their licensing and update cadence)
- Android's native `MediaCodec`, `MediaExtractor`, and `MediaMuxer` APIs, or Jetpack Media3 Transformer, when you don't need FFmpeg's full feature set

## Contributing

The repository is not accepting new contributions. You are welcome to fork it and adapt it to your needs.

---

I didn't have the repository contents, so the script names (`build_all.sh`), ABI list, and library names are reasonable guesses. Please check them against the actual code. This comes to roughly 600 words. I haven't saved it to a file; tell me if you'd like it written to `README.md`.
