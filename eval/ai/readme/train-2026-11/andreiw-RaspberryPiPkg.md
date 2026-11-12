I wrote the README to `README.md`. It runs about 1,200 words.

**Assumption to check:** the description ends with "Go here instead ->" but doesn't say where. I pointed it to the upstream TianoCore `edk2-platforms` `Platform/RaspberryPi` tree, with the Pi Firmware Task Force (`pftf/RPi3`, `pftf/RPi4`) releases as the prebuilt option. That's where the original RaspberryPiPkg UEFI work for the Pi 3 ended up. If your replacement is somewhere else, update the links in the top banner, the "Where to go instead" section and the closing footer.

**What's in it:**
- A deprecation banner at the top, plus a short summary
- What the project was: AArch64 UEFI firmware for the Raspberry Pi 3
- Why it was deprecated: the work moved upstream, it only supports old hardware, and its EDK2 base is out of date
- Where to go instead, split into using it, building it, and contributing
- Step-by-step migration from an existing setup
- FAQ and a status table
- Acknowledgements and license notes
