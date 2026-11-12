# OneFileLinux

Live linux distro combined in one ~20MB file. Runs on any UEFI computer.

OneFileLinux is a complete Linux system (kernel, initramfs and userspace) packed into a single EFI executable. Copy it to the EFI System Partition, point the firmware at it, and you have a root shell in seconds. It needs no USB stick, extra partition or bootloader, and it leaves the installed operating system untouched.

## Why

Most rescue and live systems assume you can boot from external media. That is not always possible: the USB ports may be disabled, the machine may be remote, or you may not have a flash drive to hand.

Every UEFI machine already has an EFI System Partition (ESP), a small FAT32 volume the firmware reads directly. OneFileLinux lives there as an ordinary file, which gives it several advantages:

- **Nothing to install.** One copy command puts it in place, and deleting the file removes it completely.
- **No partitioning.** It uses the existing ESP, and 20 MB fits beside any bootloader already there.
- **Boot order stays intact.** It can be launched as a one-time boot target, so the next restart returns to your normal OS.
- **Runs from RAM.** The whole system is unpacked into memory, leaving every disk unmounted and free to be repaired, imaged or repartitioned.
- **Works alongside disk encryption.** The ESP is never encrypted, so FileVault, BitLocker or LUKS on the main volume do not get in the way.

## What's inside

- A Linux kernel built with the EFI stub, so the firmware can execute it directly
- An embedded initramfs based on the Alpine Linux minimal root filesystem
- BusyBox userland plus recovery and diagnostic tools: disk and filesystem utilities, networking, wireless support and SSH
- Drivers for common storage controllers, USB devices, keyboards and network adapters

## Requirements

- An x86_64 computer with UEFI firmware
- Write access to the EFI System Partition
- Secure Boot disabled, or the image signed with a key your firmware trusts

## Installation

The steps are the same on every platform: mount the ESP, copy the file, then register a boot entry.

### macOS

```sh
diskutil list                      # find the EFI partition, e.g. disk0s1
diskutil mount disk0s1
cp OneFileLinux.efi /Volumes/EFI/
bless --mount /Volumes/EFI --setBoot \
      --file /Volumes/EFI/OneFileLinux.efi --nextonly
```

`--nextonly` applies the entry to the next boot only. With System Integrity Protection enabled, run `bless` from Recovery mode.

### Linux

```sh
mount /dev/sda1 /mnt               # your ESP may be a different device
cp OneFileLinux.efi /mnt/
efibootmgr --create-only --disk /dev/sda --part 1 \
           --label "OneFileLinux" --loader '\OneFileLinux.efi'
efibootmgr --bootnext XXXX         # number printed by the previous command
```

`--create-only` adds the entry without changing the boot order, and `--bootnext` selects it for a single boot.

### Windows

From an elevated command prompt:

```bat
mountvol S: /S
copy OneFileLinux.efi S:\
```

Then reboot into the firmware boot menu and choose the file, or launch it from an EFI shell.

### EFI shell

If your firmware provides a shell, no boot entry is needed:

```
fs0:
OneFileLinux.efi
```

## Usage

Reboot the machine. If you set a one-time entry, OneFileLinux starts automatically; otherwise, select it from the firmware boot menu. The system boots straight to a root shell.

From there you can:

- Mount, check, image or repartition any internal disk
- Bring up a network interface with `udhcpc -i eth0`
- Start the SSH server and continue the work remotely
- Inspect hardware, firmware variables and boot entries

Nothing is written to disk unless you mount a volume and write to it yourself. When you are done, type `reboot` and the computer returns to its regular operating system.

## Building

You need a Linux host with a standard C toolchain, `make`, and the usual kernel build dependencies.

```sh
git clone <repository-url>
cd OneFileLinux
./build.sh
```

The build fetches the kernel source and the Alpine minimal root filesystem. It then compiles the kernel with the root filesystem embedded through `CONFIG_INITRAMFS_SOURCE` and writes `OneFileLinux.efi` to the project root.

To customise the image, chroot into the root filesystem directory before building and add packages with `apk add`. Every package increases the size of the final file, so keep an eye on the free space on your ESP.

## Removing

Delete `OneFileLinux.efi` from the ESP and remove the boot entry if you created a permanent one (`efibootmgr --delete-bootnum --bootnum XXXX` on Linux). Nothing else is left behind.

## Troubleshooting

- **The firmware refuses to start the file.** Secure Boot is probably enabled. Disable it or sign the image with your own key.
- **Black screen after selecting the entry.** Some firmware needs a different framebuffer mode; try launching from an EFI shell to see the kernel messages.
- **No network.** The adapter may need firmware that is not in the image. Add it to the root filesystem and rebuild.
- **Not enough space on the ESP.** Some vendors ship very small partitions. Remove unused files or build a smaller image.

## Contributing

Bug reports and pull requests are welcome. When reporting a boot problem, include the computer model, the firmware version and how you launched the file.

## License

See the `LICENSE` file for details.

---

I wrote this from the one-line description, so the build script name (`build.sh`), the bundled tool list and the repository URL placeholder are assumptions; check them against the actual project before you publish.
