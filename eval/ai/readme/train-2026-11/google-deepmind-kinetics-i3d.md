# kinetics-i3d

A convolutional neural network for video classification, trained on the [Kinetics](https://deepmind.google/science/kinetics/) dataset. The model is based on the Inflated 3D ConvNet (I3D) architecture, which extends 2D image classifiers to spatiotemporal video understanding.

## Overview

Video classification requires a model to recognize actions from both appearance and motion across frames. This project implements an I3D network that:

- Takes short clips of RGB frames (and optionally optical flow) as input.
- Uses 3D convolutions to learn spatial and temporal features jointly.
- Predicts one action label per clip from the Kinetics label set.
- Supports training from scratch, fine-tuning from pretrained weights, and single-clip or sliding-window inference on full videos.

The implementation focuses on reproducible training, clear configuration, and straightforward evaluation on Kinetics validation splits.

## Features

- **Inflated 3D architecture.** Filters from a 2D Inception-v1 backbone are inflated into 3D kernels, so pretrained image weights can initialize the video model.
- **Two-stream support.** Separate RGB and optical-flow streams can be trained independently and fused at the score level.
- **Configurable input pipeline.** Frame sampling rate, clip length, crop size, and augmentation are set in a config file.
- **Mixed-precision training.** Optional automatic mixed precision reduces memory use and training time on supported GPUs.
- **Checkpointing and resume.** Training state is saved periodically and can be resumed after interruption.
- **Evaluation tools.** Top-1 and top-5 accuracy, per-class accuracy, and confusion matrices are computed on validation data.
- **Video-level inference.** Predictions can be averaged over multiple temporal and spatial crops for more stable results.

## Architecture

The network follows the I3D design:

1. **Stem.** A 7×7×7 convolution with temporal stride 2, followed by max pooling.
2. **Inception-3D blocks.** Nine inception modules with parallel 1×1×1, 3×3×3, and pooled branches. Temporal pooling is applied at selected stages.
3. **Head.** Global average pooling over space and time, dropout, and a 1×1×1 convolution producing class logits. Logits are averaged over time to produce clip-level predictions.

Default input is 64 frames at 224×224 pixels with three color channels. Flow streams take two-channel optical flow (x and y components) at the same resolution.

## Dataset

This project uses the Kinetics-400 dataset, which contains about 400 human action classes drawn from YouTube videos. Each clip is roughly ten seconds long.

Kinetics is distributed as video URLs and annotation files rather than as raw videos. You must download the videos yourself and comply with the terms of use of the original sources. Some URLs may no longer be available, so the usable training and validation sets may be smaller than the published counts.

### Preparing the data

1. Obtain the annotation files (`train.csv`, `val.csv`, `test.csv`) from the official Kinetics release.
2. Download the videos with the provided downloader script or a tool of your choice.
3. Trim each video to its annotated segment and resample to a fixed frame rate (25 fps is the default).
4. Optionally precompute optical flow with a tool such as TV-L1 or a learned flow model. Flow precomputation is slow but substantially speeds up training.
5. Place the processed data under `data/kinetics400/` with the directory layout described in the configuration reference below.

Verify the layout with:

```bash
python tools/check_dataset.py --root data/kinetics400
```

The script reports missing files, unreadable videos, and class imbalance.

## Requirements

- Python 3.9 or later
- PyTorch 1.12 or later, with CUDA support recommended
- A GPU with at least 16 GB of memory for batch sizes used in the default configuration
- FFmpeg, for video decoding
- Roughly 500 GB of free disk space for the full Kinetics-400 dataset with precomputed flow

Other dependencies are listed in `requirements.txt`.

## Installation

Clone the repository and create a virtual environment:

```bash
git clone <repository-url> kinetics-i3d
cd kinetics-i3d
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Confirm that PyTorch can see your GPU:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## Usage

### Training

Train the RGB stream from scratch with the default configuration:

```bash
python train.py --config configs/i3d_rgb_kinetics400.yaml
```

To initialize from ImageNet-inflated weights, set `model.init_weights` in the config. To train the flow stream, use `configs/i3d_flow_kinetics400.yaml`.

Command-line flags override config values:

```bash
python train.py --config configs/i3d_rgb_kinetics400.yaml \
    --batch-size 8 \
    --lr 0.01 \
    --epochs 100
```

Training logs are written to `runs/<experiment-name>/`. Checkpoints are saved to `runs/<experiment-name>/checkpoints/`.

### Resuming training

```bash
python train.py --config configs/i3d_rgb_kinetics400.yaml --resume runs/<experiment-name>/checkpoints/last.pt
```

### Evaluation

Evaluate a trained checkpoint on the validation split:

```bash
python evaluate.py \
    --config configs/i3d_rgb_kinetics400.yaml \
    --checkpoint runs/<experiment-name>/checkpoints/best.pt \
    --split val
```

To combine the two streams, provide both checkpoints:

```bash
python evaluate.py \
    --config configs/i3d_rgb_kinetics400.yaml \
    --checkpoint runs/rgb/checkpoints/best.pt \
    --flow-checkpoint runs/flow/checkpoints/best.pt \
    --fusion-weight 0.5 \
    --split val
```

Results are written to `runs/<experiment-name>/eval/` as JSON and CSV files.

### Inference on a video

Classify a single video file:

```bash
python predict.py \
    --config configs/i3d_rgb_kinetics400.yaml \
    --checkpoint runs/<experiment-name>/checkpoints/best.pt \
    --video path/to/video.mp4 \
    --top-k 5
```

The script samples several clips across the video, averages their predictions, and prints the top-k labels with confidence scores.

## Configuration reference

Configuration files are YAML. The main sections are:

- `data`: dataset root, annotation files, frame rate, clip length, and crop size.
- `augmentation`: random crop, horizontal flip, color jitter, and temporal jitter settings.
- `model`: stream type (`rgb` or `flow`), number of classes, dropout rate, and initialization weights.
- `optim`: optimizer (SGD or AdamW), learning rate, weight decay, momentum, and learning-rate schedule.
- `train`: batch size, number of epochs, gradient accumulation steps, mixed-precision flag, and number of data-loader workers.
- `eval`: number of temporal and spatial crops used at test time.

The expected dataset layout is:

```
data/kinetics400/
├── annotations/
│   ├── train.csv
│   ├── val.csv
│   └── test.csv
├── videos/
│   ├── train/
│   └── val/
└── flow/            # optional, required for flow stream
    ├── train/
    └── val/
```

## Project structure

```
kinetics-i3d/
├── configs/          # YAML experiment configurations
├── data/             # Dataset loaders and transforms
├── models/           # I3D network definition and inflation utilities
├── tools/            # Dataset checks, flow precomputation, conversion scripts
├── train.py          # Training entry point
├── evaluate.py       # Validation and test evaluation
├── predict.py        # Single-video inference
├── requirements.txt
└── README.md
```

## Results

Reference results on Kinetics-400 validation, using 10 temporal clips and 3 spatial crops per video:

| Model | Input | Top-1 accuracy | Top-5 accuracy |
|-------|-------|----------------|----------------|
| I3D (RGB) | 64 frames, 224×224 | _to be filled_ | _to be filled_ |
| I3D (Flow) | 64 frames, 224×224 | _to be filled_ | _to be filled_ |
| I3D (Two-stream) | RGB + Flow | _to be filled_ | _to be filled_ |

Fill in these values from your own evaluation runs. Results depend on the subset of videos that remain downloadable, so report the number of valid training and validation videos alongside your scores.

## Tips for good results

- **Start from pretrained weights** when possible. Training from scratch needs many epochs and a large amount of compute.
- **Precompute optical flow** if you plan to train the flow stream. On-the-fly flow estimation is much slower.
- **Use gradient accumulation** when GPU memory is limited. Effective batch size is `batch-size × accumulation-steps`.
- **Monitor validation accuracy** rather than training loss to detect overfitting early.
- **Check class balance** with `tools/check_dataset.py` before comparing runs, since missing videos can skew per-class results.

## Troubleshooting

- **Out-of-memory errors.** Reduce `--batch-size`, lower the crop size, or enable mixed precision.
- **Slow data loading.** Increase `num_workers`, store frames as pre-decoded arrays, or move the dataset to a faster disk.
- **Video decode failures.** Confirm FFmpeg is on your `PATH` and that the video codec is supported. Videos that fail are logged to `runs/<experiment-name>/bad_videos.txt`.
- **NaN loss.** Lower the learning rate or enable gradient clipping (`optim.grad_clip` in the config).

## Citation

If you use this code or the I3D architecture in your research, please cite the original paper:

```bibtex
@inproceedings{carreira2017quo,
  title     = {Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset},
  author    = {Carreira, Joao and Zisserman, Andrew},
  booktitle = {Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  year      = {2017}
}
```

Please also cite the Kinetics dataset:

```bibtex
@article{kay2017kinetics,
  title   = {The Kinetics Human Action Video Dataset},
  author  = {Kay, Will and Carreira, Joao and Simonyan, Karen and Zhang, Brian and Hillier, Chloe and Vijayanarasimhan, Sudheendra and Viola, Fabio and Green, Tim and Back, Trevor and Natsev, Paul and Suleyman, Mustafa and Zisserman, Andrew},
  journal = {arXiv preprint arXiv:1705.06950},
  year    = {2017}
}
```

## License

Specify the license for this project here (for example, MIT or Apache 2.0). Kinetics videos and annotations are subject to their own terms of use and are not covered by this license.

## Acknowledgments

- The I3D architecture and Kinetics dataset were introduced by DeepMind.
- Pretrained weights and inflation methods follow the approach described in the original paper.
