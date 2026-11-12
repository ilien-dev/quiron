# HermesEventBus

A library for using EventBus between processes, useful in IPC or plugin development.

HermesEventBus extends the familiar publish/subscribe model of [GreenRobot EventBus](https://github.com/greenrobot/EventBus) across process boundaries. Post an event in one process and subscribers in other processes receive it, with no AIDL files, Binder boilerplate, or manual serialization plumbing.

## Table of Contents

- [Why HermesEventBus?](#why-hermeseventbus)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Notes](#usage-notes)
- [Plugin Development](#plugin-development)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Why HermesEventBus?

Android apps often run components in several processes: a push service, a media player, a WebView sandbox, or plugins loaded in their own process. A standard in-process event bus cannot reach across those boundaries, and hand-written IPC is verbose and error-prone.

HermesEventBus keeps the API you already know and routes events through a lightweight inter-process layer, so the code stays small and readable.

## Features

- **Cross-process delivery:** events posted in any process reach subscribers in all connected processes.
- **Familiar API:** the same `register`, `unregister`, `post`, and `@Subscribe` workflow as EventBus.
- **No AIDL:** event classes are passed between processes without interface definitions.
- **Sticky events:** supports sticky posts so late subscribers still receive the latest event.
- **Plugin friendly:** designed for host/plugin architectures where components are loaded dynamically.
- **Thread modes:** works with EventBus thread modes such as `MAIN` and `BACKGROUND`.

## Installation

Add the dependency to your module's `build.gradle`:

```groovy
dependencies {
    implementation 'xiaofei.library:hermes-eventbus:<latest-version>'
}
```

Replace `<latest-version>` with the most recent release listed on the project's releases page.

## Quick Start

### 1. Initialize in your Application class

Initialization must run in every process that takes part in event delivery. Placing it in `Application.onCreate()` covers this automatically.

```java
public class App extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        HermesEventBus.getDefault().init(this);
    }
}
```

### 2. Define an event

Events are plain Java objects. Make sure they can be transferred between processes (keep fields simple and provide a public no-argument constructor where needed).

```java
public class MessageEvent {
    public String text;

    public MessageEvent() {}

    public MessageEvent(String text) {
        this.text = text;
    }
}
```

### 3. Subscribe

```java
public class MainActivity extends AppCompatActivity {

    @Override
    protected void onStart() {
        super.onStart();
        HermesEventBus.getDefault().register(this);
    }

    @Override
    protected void onStop() {
        HermesEventBus.getDefault().unregister(this);
        super.onStop();
    }

    @Subscribe(threadMode = ThreadMode.MAIN)
    public void onMessage(MessageEvent event) {
        Toast.makeText(this, event.text, Toast.LENGTH_SHORT).show();
    }
}
```

### 4. Post from any process

```java
HermesEventBus.getDefault().post(new MessageEvent("Hello from another process"));
```

Every registered subscriber for `MessageEvent`, in any initialized process, receives the event.

### 5. Clean up

When the application no longer needs the bus, release its resources:

```java
HermesEventBus.getDefault().destroy();
```

## Usage Notes

- **Initialize early.** Call `init` before registering or posting. A process that has not been initialized will not send or receive cross-process events.
- **Unregister symmetrically.** Pair every `register` with an `unregister` in the matching lifecycle callback to avoid leaks and duplicate deliveries.
- **Keep events small.** Events are serialized to cross the process boundary. Prefer compact, simple data over large payloads or complex object graphs.
- **Use the same class on both sides.** The event class must exist, with the same fully qualified name, in every process that handles it.
- **Obfuscation.** If you use ProGuard or R8, keep your event classes and subscriber methods:

```proguard
-keep class com.example.app.events.** { *; }
-keepclassmembers class * {
    @org.greenrobot.eventbus.Subscribe <methods>;
}
```

## Plugin Development

Plugin systems usually separate a host app from independently built plugins, sometimes running in their own processes. HermesEventBus fits this layout well:

1. The host and each plugin initialize `HermesEventBus` in their process.
2. A shared module contains the event classes, so the host and plugins agree on the contract.
3. Either side posts and subscribes without knowing where the other lives.

This lets you add, remove, or update plugins without changing how the host communicates with them. The shared event module becomes your only coupling point, and it can be versioned like any other API.

A typical structure:

```
host-app/        # initializes the bus, subscribes to plugin events
plugin-a/        # initializes the bus, posts status events
shared-events/   # event classes used by host and plugins
```

## Limitations

- Delivery is intended for processes belonging to the same application or cooperating applications that initialize the library. It is not a general-purpose network messaging system.
- Event delivery across processes is asynchronous. Do not rely on a post returning only after remote subscribers have finished.
- Events that cannot be serialized cleanly (for example, those holding `Context`, `View`, or open streams) should not be posted.
- Cross-process calls add overhead compared with an in-process bus. Avoid very high-frequency posting of large events.

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-change`.
3. Commit your changes with a clear message.
4. Push the branch and open a pull request describing what changed and why.

Please include tests for new behavior where possible and keep the public API consistent with EventBus conventions. Bug reports are most useful when they include the Android version, the number of processes involved, and a minimal reproduction.

## License

Distributed under the Apache License 2.0. See the `LICENSE` file for details.
