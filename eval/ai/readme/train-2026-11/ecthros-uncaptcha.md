# uncaptcha

> Defeating Google's audio reCaptcha with 85% accuracy.

uncaptcha is a research project exploring the security of audio-based CAPTCHA challenges. It examines whether an automated system can interpret an audio challenge accurately enough to undermine its intended purpose: distinguishing human visitors from software.

The project focuses on a fundamental tension in CAPTCHA design. An accessibility feature must make a challenge understandable to people who cannot use its visual equivalent, but that same clarity can make the challenge understandable to automated speech recognition systems. uncaptcha investigates this tension and demonstrates why accessibility and abuse prevention must be designed together.

The headline figure—85% accuracy—is a reported result under particular experimental conditions. It should not be interpreted as a guarantee against current versions of reCAPTCHA, across all websites, or under every network and deployment configuration.

## Overview

Audio CAPTCHAs offer an alternative to visual puzzles. Instead of selecting images or reading distorted text, a user listens to a recording and enters the requested information. The challenge assumes that a human listener can recover the relevant speech while an automated system will struggle.

uncaptcha questions that assumption. Its central research question is straightforward:

**How much protection does an audio CAPTCHA provide when automated speech recognition can interpret the same recording?**

At a conceptual level, the approach involves obtaining an authorized challenge, preparing its audio for recognition, interpreting the speech, and evaluating the resulting answer. The important finding is broader than any particular implementation: advances in speech recognition can weaken challenges built around the expectation that understanding speech remains difficult for machines.

## Why This Matters

CAPTCHAs are often treated as a convenient boundary between legitimate users and automated activity. In practice, they provide a probabilistic signal, and their effectiveness depends on the capabilities of the systems attempting to solve them.

Audio challenges make this especially visible. Adding distortion or background noise may make automated recognition harder, but it can also make the challenge harder for legitimate users. People using assistive technology may bear a disproportionate share of that cost.

uncaptcha highlights the need to evaluate accessibility paths as part of the complete security system. An alternative challenge is not a separate concern: if it provides access to the same protected action, its weaknesses affect the overall protection.

## Understanding the 85% Result

A success rate is meaningful only when its measurement is clear. Evaluating the reported 85% accuracy requires context, including:

- The number and variety of challenges tested.
- The version of the challenge system used.
- Whether accuracy measures transcription or accepted solutions.
- Whether multiple attempts were allowed.
- Which recognition services or models were available.
- How failed requests, unavailable challenges, and ambiguous recordings were counted.

Transcribing a recording correctly is not necessarily equivalent to completing a protected interaction. A deployment may use additional signals, request checks, or other controls beyond the audio answer.

For reproducible results, experiments should document these distinctions and report both successful and unsuccessful attempts. Historical measurements should also remain clearly separated from results obtained against newer systems.

## Repository Scope

This README describes the project's purpose and the interpretation of its headline result. It does not assume a particular programming language, dependency manager, recognition provider, or execution environment.

Installation and usage instructions should match the implementation present in the repository. Before running an experiment, review its source code and accompanying documentation to understand what it accesses, which external services it contacts, and what information it stores.

If an implementation depends on an external recognition service, consider its credentials, usage limits, costs, and handling of submitted audio. Avoid committing credentials or captured challenge data to version control.

## Responsible Use

Use uncaptcha for research, education, and testing on systems you own or have explicit permission to assess. Define the target, request volume, testing period, and data-handling expectations before beginning an assessment.

A useful experiment should answer a specific question without creating unnecessary traffic or interfering with other users. Controlled environments and recorded test material can help separate recognition performance from unrelated deployment behavior.

When a finding affects a live service, document the conditions carefully and use an appropriate disclosure process. Reports are most useful when they explain the observed behavior, its practical limits, and enough experimental context for the affected party to reproduce it.

## Limitations

Audio challenge formats and speech recognition capabilities change over time. Results can vary with language, recording quality, preprocessing, recognition models, and challenge selection.

The project therefore should be understood as an investigation of a security assumption, rather than a universal measure of CAPTCHA effectiveness. A strong evaluation also considers usability: making a challenge harder to automate is not a successful improvement if legitimate users can no longer complete it reliably.

## Contributing

Contributions should improve clarity, reproducibility, or understanding. Useful work includes documenting experimental conditions, correcting unsupported claims, improving evaluation methods, and examining accessibility tradeoffs.

When reporting results, distinguish observations from assumptions and include limitations alongside headline numbers. Keep examples free of credentials and personal information.

## License

Consult the repository's `LICENSE` file for applicable terms. If no license is provided, do not assume permission to redistribute or modify the code.
