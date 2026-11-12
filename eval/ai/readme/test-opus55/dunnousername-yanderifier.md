<invoke name="Write">
<parameter name="file_path">C:\Users\jesus\AppData\Local\Temp\quiron-gen-sil7hn_l\README.md</parameter>
<parameter name="content"># yanderifier

**First-Order-Wrapper** (formerly known as **Yanderify**) is a front-end tool for [first-order-motion](https://github.com/AliaksandrSiarohin/first-order-model). It aims to make using first-order-motion face animation accessible to everyone, for education and entertainment.

Give it a single still image of a face and a "driving" video, and it produces a new video in which the face in the image moves, blinks, and talks like the person in the video. No command line, no notebook, and no machine learning background required.

---

## Features

- **Simple graphical interface** – pick an image, pick a video, press start.
- **Automatic preprocessing** – input images and videos are resized and cropped to the format the model expects.
- **GPU acceleration** – uses a CUDA-capable NVIDIA GPU when available, with a CPU fallback for everyone else.
- **Audio passthrough** – the soundtrack from the driving video is preserved in the output.
- **Relative and absolute motion modes** – choose whether to transfer motion relative to the first frame (usually more natural) or use absolute keypoint positions.
- **Bundled checkpoint** – the pretrained face model is downloaded and set up for you.

## Requirements

- Windows 10/11 (Linux and macOS can run from source)
- Python 3.8 or newer when running from source
- [FFmpeg](https://ffmpeg.org/) available on your `PATH`
- Optional: an NVIDIA GPU with recent drivers for much faster rendering

## Installation

### Prebuilt release

1. Download the latest release archive from the Releases page.
2. Extract it to a folder of your choice.
3. Run `yanderifier.exe`.

### From source

```bash
git clone <repository-url> yanderifier
cd yanderifier
python -m venv venv
venv\Scripts\activate        # on Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python main.py
```

On first launch, the pretrained model checkpoint will be downloaded automatically.

## Usage

1. **Choose a source image.** A clear, front-facing photo with the face roughly centered works best.
2. **Choose a driving video.** Short clips of a single person talking or making expressions give the cleanest results.
3. **Pick an output path** for the finished video.
4. **Select options** such as relative motion and GPU/CPU mode.
5. Click **Start** and wait for the progress bar to finish.

### Tips for better results

- Match the head pose of the image and the first frame of the video as closely as possible.
- Avoid heavy occlusion (hands, hair, glasses glare) over the face.
- Keep the head fairly still in frame; large movements cause distortion.
- Crop the driving video so the face fills most of the frame.

## Responsible use

This tool is intended for education, research, and harmless fun. Do not use it to impersonate, deceive, harass, or create content of real people without their consent. Clearly label generated media as synthetic. You are responsible for complying with the laws of your jurisdiction.

## Credits

- The underlying model is **First Order Motion Model for Image Animation** by Aliaksandr Siarohin, Stéphane Lathuilière, Sergey Tulyakov, Elisa Ricci, and Nicu Sebe (NeurIPS 2019).
- Thanks to everyone who has reported bugs, tested builds, and contributed improvements.

## License

See [`LICENSE`](LICENSE) for this project's license. The first-order-motion model and its pretrained weights are subject to their own license terms; please review them before redistributing or using the outputs commercially.
</parameter>
</invoke>
*Tool result unavailable — the tool call may have failed or been cancelled.*
