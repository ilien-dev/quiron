## Video Call Support

This PR adds optional video call support to Bucket Brigade, so participants can see each other while singing together, not just hear the mixed audio.

### What changed

- Added a video call option to the client UI, off by default so existing audio-only sessions behave as before.
- Video is handled separately from the audio pipeline, so it can't add latency or glitches to the synchronized audio mix.
- Added a control to join or leave the video call without leaving the audio session.
- Updated the server and client to exchange the information needed to connect participants to the same call.

### Why

Singing together is more fun when you can see the other people. Video also helps with coordination, such as cues and noticing when someone needs help.

### Testing

- Verified that audio-only sessions are unchanged.
- Tried joining and leaving the call mid-session.
- Checked that disabling video leaves no leftover state.

I haven't looked at the actual diff, so the bullets and testing notes are generic. Adjust them to match what the code really does before posting.
