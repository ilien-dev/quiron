# My Twitch Stream Setup

Building a Twitch stream setup can feel overwhelming. There are endless microphones, cameras, lights, capture cards, keyboards, and software tools competing for attention. My goal was simpler: create a setup that looks clean, sounds good, and stays out of the way while I’m live.

Here’s the setup I use and the reasoning behind it.

## The Computer

My streaming PC is also my everyday development and gaming machine. It has a modern multi-core CPU, 32 GB of RAM, and a dedicated GPU with hardware video encoding.

Hardware encoding is important because it lets the GPU handle most of the streaming workload. That keeps CPU usage under control when I’m compiling code, running containers, or playing a game.

I use two monitors:

- The primary monitor displays the game, editor, or terminal.
- The secondary monitor holds chat, stream controls, documentation, and monitoring tools.

Two monitors aren’t essential, but they make managing a live stream much less stressful.

## Audio

Audio quality matters more than video quality. Viewers will usually tolerate an average camera, but noisy or distorted audio makes a stream difficult to watch.

I use a dynamic microphone mounted on a boom arm. Dynamic microphones are useful in untreated rooms because they tend to capture less keyboard noise and room echo than sensitive condenser microphones.

My audio chain includes:

1. A noise-suppression filter
2. A noise gate
3. A compressor
4. A limiter

The noise gate reduces background sound when I’m not speaking. Compression keeps quiet and loud speech closer together, while the limiter prevents sudden peaks from clipping.

I also monitor the final audio through headphones before every stream. A thirty-second recording has saved me from broadcasting muted, distorted, or incorrectly routed audio more than once.

## Camera and Lighting

My camera is a standard 1080p webcam. It isn’t especially expensive, but good lighting makes it look significantly better.

I use one soft light positioned slightly above eye level and off to one side. A smaller light behind me helps separate my outline from the background. Both lights are set to similar color temperatures so the image doesn’t look unnaturally blue or orange.

I keep the camera framing fairly tight. The stream is usually focused on code or gameplay, so my face doesn’t need to occupy much screen space.

## OBS Studio

OBS Studio is the center of the setup. I organize scenes around activities rather than individual applications:

- Starting Soon
- Coding
- Gaming
- Break
- Just Chatting
- Stream Ending

Each scene contains reusable sources for the camera, microphone, alerts, and overlays. Shared elements are placed in nested scenes, which means I can update the camera layout once instead of changing every scene separately.

For coding streams, I increase the editor font size and hide unnecessary panels. Text that feels enormous on my monitor often looks merely readable after Twitch compression and playback on a phone.

I also record locally using a separate audio track for the microphone. That makes editing highlights much easier because voice audio can be adjusted independently.

## Controls and Automation

A small programmable control pad handles scene switching, microphone muting, recording, and marker creation. Keyboard shortcuts can accomplish the same thing, but physical buttons are harder to press accidentally while typing.

Before going live, I follow a short checklist:

- Verify the stream title and category.
- Record a local audio and video test.
- Confirm that private windows and notifications are hidden.
- Open chat and moderation tools.
- Keep water nearby.

## What I’d Upgrade Next

The next improvement won’t be a new camera or microphone. It will be better acoustic treatment. Reducing reflections in the room would improve both the live audio and my recordings.

That reflects the main lesson from building this setup: upgrades should solve specific problems. Start with clear audio, reliable software, and a repeatable workflow. Everything else can evolve as the stream grows.