# MyDiary

> In the movie *"Your Name."* (君の名は。, 你的名字), "My Diary" is the Android version.

MyDiary is an Android diary app inspired by the notebook that Mitsuha and Taki use to talk to each other across time and distance in *Your Name.* Instead of two strangers swapping bodies, you get a quiet place to write down your day, and entries that stay readable years later.

## Inspiration

In the film, Mitsuha and Taki wake up in each other's lives and can't explain the gaps in their memory. They begin leaving notes on paper, in their phones, and sometimes on their own skin. The notes become a conversation and then a bond.

MyDiary borrows that idea. A diary is a message to someone who will read it later, usually your future self. The app aims to make that exchange feel personal and calm.

## Features

- **Daily entries**: Write freely, with a date, title, and body. Entries are saved automatically as you type.
- **Mood tracking**: Tag each day with a mood and review how you felt over a week or a month.
- **Calendar view**: Jump to any day and see at a glance which days have entries.
- **Photos**: Attach pictures to an entry, such as a sunset, a train platform, or a meal.
- **Search**: Find entries by keyword, date, or mood.
- **"Message to future me"**: Lock an entry until a date you choose and read it when the time comes.
- **Themes**: Light and dark themes, plus a twilight palette inspired by the film's comet-lit skies.
- **Local-first storage**: Entries live on your device. Nothing is uploaded unless you turn on backup.
- **Export and backup**: Export entries as plain text or JSON, or back them up to a file you control.
- **App lock**: Protect your diary with a PIN or biometric authentication.

## Screenshots

Screenshots will be added to the `docs/screenshots` folder.

| Home | Editor | Calendar |
|------|--------|----------|
| _coming soon_ | _coming soon_ | _coming soon_ |

## Requirements

- Android Studio (latest stable release recommended)
- JDK 17 or newer
- Android SDK with API level 34 installed
- A device or emulator running Android 8.0 (API 26) or higher

## Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/MyDiary.git
   cd MyDiary
   ```

2. **Open the project** in Android Studio using *File → Open* and select the project folder.

3. **Sync Gradle** and wait for dependencies to download.

4. **Run the app** on an emulator or a connected device with the *Run* button, or from the command line:

   ```bash
   ./gradlew installDebug
   ```

On Windows, use `gradlew.bat installDebug` instead.

## Project Structure

```
MyDiary/
├── app/
│   ├── src/main/
│   │   ├── java/        # Application source code
│   │   ├── res/         # Layouts, drawables, strings, themes
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── docs/                # Documentation and screenshots
├── build.gradle
├── settings.gradle
└── README.md
```

## Architecture

MyDiary follows a simple layered approach:

- **UI layer**: Screens and view models that react to state changes.
- **Domain layer**: Plain classes describing entries, moods, and reminders.
- **Data layer**: A local database that stores entries, with repositories hiding storage details from the rest of the app.

This separation keeps the code easy to test and makes it simple to swap storage or add sync later.

## Privacy

A diary is private by nature, so MyDiary is designed accordingly:

- Entries stay on your device by default.
- The app does not require an account.
- No analytics or advertising trackers are included.
- Backups and exports happen only when you ask for them.

If you enable backup, keep the resulting file somewhere safe, since it contains your writing in readable form unless you encrypt it.

## Roadmap

- [ ] Optional encrypted backups
- [ ] Home screen widget for quick entries
- [ ] Daily writing reminders
- [ ] Rich text formatting
- [ ] Multiple languages, including Japanese and Chinese
- [ ] Tablet and foldable layouts

## Contributing

Contributions are welcome, whether a bug report, a translation, or a new feature.

1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-feature`.
3. Make your changes and add tests where it makes sense.
4. Commit with a clear message describing what changed and why.
5. Open a pull request and describe your changes.

Please keep the code style consistent with the existing project and run the test suite before submitting:

```bash
./gradlew test
```

## Reporting Issues

If you find a bug, open an issue and include:

- Your Android version and device model
- Steps to reproduce the problem
- What you expected to happen and what happened instead
- Screenshots or logs, if available

## Acknowledgments

- *Your Name.* (君の名は。), directed by Makoto Shinkai, for the inspiration.
- The open-source Android community and the libraries this project builds on.

## Disclaimer

MyDiary is an independent fan-inspired project. It is not affiliated with, endorsed by, or connected to the creators, studio, or distributors of *Your Name.* All rights to the film and its characters belong to their respective owners.

## License

Released under the MIT License. See the `LICENSE` file for details.

---

*Write down today, so that someone, even if it's only you, can remember it tomorrow.*

---

This is about 830 words. I haven't saved it to a file. I can write it to `README.md` in the working directory if you'd like. The clone URL, license, and feature list are placeholders, so adjust them to match what the app actually does.
