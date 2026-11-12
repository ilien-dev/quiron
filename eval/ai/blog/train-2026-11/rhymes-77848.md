# The dangers of the unibrow(ser)

Every web developer has one. Maybe you've met them in a code review, or maybe you've been one. They have a single browser, they love it, and they have never once opened the site in anything else. "Works on my machine" has a cousin: "Works in my browser."

I'm calling this condition the **unibrow(ser)**. It's harmless in small doses, and it can quietly wreck a product.

## Symptoms

- Your DevTools are open in the same browser every day, and its quirks feel like web standards.
- The phrase "just open it in Chrome" comes up whenever someone reports a bug.
- Your CSS includes a fix that does nothing except make things work in the one browser you use.
- You've never checked how a form behaves in Safari on an iPhone, and you're not sure you want to know.
- When a user says "it's broken," your first question is "which browser?" and your second is "why would you use that?"

## Why it's dangerous

**1. Blind spots become bugs in production.** A flexbox gap that renders fine in one engine may collapse in another. A date input that looks polished in Chromium may be a plain text box somewhere else. You won't notice until a customer does, and the customer will not be impressed.

**2. You ship features that only half exist.** If the only browser you test in supports a newer API, you may build your whole feature around it. Half your users then get a blank screen, and nobody on your team saw it coming.

**3. Monoculture hides accessibility failures.** Screen readers, zoom behavior, and keyboard navigation vary across browsers and assistive technologies. Testing in one setup gives you one set of results, and it's easy to mistake that for "accessible."

**4. You become the bottleneck.** When only one person understands how the app behaves across environments, every cross-browser issue ends up on their desk. That's a fragile system, and it's a bad week waiting to happen.

**5. Your users are not your browser.** Your users run older devices, locked-down corporate machines, budget Android phones, and whatever their employer's IT department approved in 2019. Your setup is a sample of one.

## The cure

Recovery is easier than you'd think:

- **Test in at least the big three engines**: Chromium, Gecko (Firefox), and WebKit (Safari). Playwright makes this a config change rather than a weekend project.
- **Check your analytics.** Look at which browsers your users actually use, and test those first, not the one you happen to like.
- **Use feature detection, not browser sniffing.** Check `@supports` and `'feature' in window` rather than guessing from the user agent.
- **Add cross-browser checks to CI.** If a regression can slip through, it eventually will. Let the pipeline catch it.
- **Try a real device now and then.** Emulators are useful, but an actual phone with a flaky connection teaches you things a desktop never will.
- **Pair with someone who uses something else.** A colleague who lives in Firefox will find your blind spots within minutes.

## One browser is a starting point

Nothing here means you should abandon your favorite browser. Use it daily. Love it. Just don't let it be the only lens you look through.

The unibrow(ser) is not a character flaw. It's a habit, and habits can be unlearned. Open the site in something you don't use. Click around. You may be surprised by what you find, and your users will be glad you did.
