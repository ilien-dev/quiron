# reark

**RxJava architecture library for Android**

reark helps you structure Android applications around reactive data flows. It brings application state, asynchronous work, and presentation logic into a consistent architecture built on RxJava.

Android applications coordinate many things at once: user input, network requests, local storage, navigation, and lifecycle changes. As these responsibilities grow, it becomes harder to understand where data comes from, which component owns it, and why a screen changed. reark provides a foundation for organizing that complexity into components with clear responsibilities.

The goal is straightforward: make application behavior easier to follow, test, and maintain as features evolve.

## Why reark?

RxJava provides tools for composing asynchronous operations. Architecture determines where those operations belong and how the rest of an application interacts with them.

Without consistent boundaries, reactive code can become scattered across activities, fragments, adapters, and services. A screen might start a request, transform its result, update a cache, handle errors, and render views inside one subscription. That approach can work initially, but it becomes difficult to reuse or verify.

reark encourages a structure in which:

- Data sources handle access to external systems.
- Application logic coordinates operations and applies rules.
- State describes what the application currently knows.
- Presentation components translate state into something the user can see.
- User actions enter the system through explicit boundaries.

These responsibilities work together through reactive streams, giving asynchronous behavior a consistent place in the application.

## Architectural approach

A useful starting point is to think in terms of a repeating cycle:

```text
User action
    |
    v
Application logic
    |
    v
Data operation
    |
    v
Updated state
    |
    v
UI rendering
```

The user performs an action, application logic decides what should happen, and a data operation produces an outcome. That outcome updates the state observed by the presentation layer.

Not every action requires a network request or database operation. Selecting a filter, expanding an item, or dismissing a message may update local state directly. The important property is that behavior follows an understandable path.

This structure also separates the lifetime of a view from the lifetime of the data it displays. Recreating a screen should not require rebuilding every application decision inside its view callbacks.

## Core concepts

### Reactive data sources

A data source represents access to information outside a consuming component. It might read from a database, call a remote service, or observe a device capability.

Expose meaningful operations through these boundaries. Callers should understand what an operation does without needing to know the details of an HTTP client, database cursor, or storage format.

Keep transformations close to the responsibility they serve. Parsing a response belongs near the data boundary; deciding whether a user can perform an action belongs in application logic.

### Application logic

Application logic connects user intent with the operations needed to fulfill it. It coordinates dependencies, applies rules, and determines how results affect state.

For example, refreshing a list may involve checking whether a refresh is already running, requesting new data, preserving existing content during loading, and translating a failure into a recoverable state.

Keeping this coordination outside Android views makes it easier to exercise without launching an activity or fragment.

### State

State gives consumers a coherent description of the application at a particular moment.

A list screen might need to represent its items, loading status, selected filter, and any relevant error. Treat these values as related parts of the same experience rather than independent callbacks that happen to update the same view.

Prefer state that makes valid combinations clear. If existing content can remain visible while refreshing, represent that explicitly. If an empty result differs from an initial load, preserve that distinction.

### Presentation

Presentation components observe state and render it. They also translate interactions into actions that application logic can handle.

Keep rendering predictable: given the same state, a screen should produce the same visible result. Avoid hiding business decisions inside rendering code, where they become dependent on callback order or view lifecycle behavior.

## Getting started

Begin with a single feature that has an understandable data flow, such as loading a list or displaying an item’s details.

1. Identify the information the feature needs.
2. Define the states the user can encounter.
3. Describe the actions the user can perform.
4. Place data access behind a focused boundary.
5. Compose the required operations with RxJava.
6. Connect state observation to the presentation lifecycle.
7. Test the transitions that matter.

Start with the smallest useful structure. Introduce shared abstractions when multiple features demonstrate the same need.

Dependency coordinates, supported versions, and concrete APIs should be taken from the release documentation for the version you use.

## Threading and scheduling

Make scheduling decisions deliberately. Blocking work should run away from the Android main thread, while view updates must reach the appropriate UI thread.

Choose scheduling boundaries where ownership is clear. A component performing blocking storage access should have an explicit threading contract. A presentation component should know where its observed values will be delivered.

For testable code, consider providing schedulers through dependencies. This lets tests control execution without relying on real thread timing or arbitrary delays.

Avoid scattering scheduler changes throughout a chain unless each change serves a clear purpose.

## Lifecycle and subscriptions

Every subscription needs an owner and a defined end.

UI observation usually belongs to the lifecycle of the view consuming it. Work intended to survive a particular screen needs an owner with a suitable lifetime.

Dispose of subscriptions when their owner no longer needs them. Otherwise, an obsolete view may continue receiving updates or retain references longer than intended.

Also decide what should happen when observation resumes. Some consumers need the latest state immediately; others need only future events. Make that choice explicit when designing streams and state ownership.

## Error handling

Errors are part of application behavior. Handle them at the boundary that has enough context to make a useful decision.

A data layer may classify a failure. Application logic may decide whether retrying is appropriate. Presentation code may explain the outcome and offer a recovery action.

Distinguish a failed operation from the permanent failure of a long-lived stream. A refresh error should not accidentally prevent every future refresh.

Use retries carefully. Consider cancellation, repeated user actions, and whether an operation is safe to repeat.

## Testing

Test observable behavior and meaningful state transitions.

Useful scenarios include an initial load, a successful refresh, an empty result, a failure with existing content, and overlapping actions. Verify cancellation where it affects correctness.

Use controlled dependencies so tests can produce results and failures predictably. RxJava’s testing facilities and controllable schedulers can help verify emissions and timing.

Keep most application logic tests independent of Android components. Add integration and UI tests where platform behavior or rendering needs verification.

## Project organization

Organize code so a reader can locate a feature’s behavior without tracing unrelated layers.

Feature-based packages can keep state, coordination, and presentation close together. Shared infrastructure can hold reusable data access and platform integrations.

Whatever structure you choose, keep dependency direction clear and apply the conventions consistently.

## Contributing

Contributions should explain the problem being solved and the resulting behavior. Include a focused example when proposing an architectural change.

Keep changes small enough to review, document public behavior, and add tests for meaningful logic changes. Follow the repository’s contribution instructions and license terms when available.
