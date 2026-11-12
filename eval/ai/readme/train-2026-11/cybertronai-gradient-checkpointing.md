# gradient-checkpointing

**Make huge neural nets fit in memory.**

`gradient-checkpointing` trades a small amount of extra compute for a large reduction in activation memory during training. Instead of storing every intermediate activation for the backward pass, it stores a few and recomputes the rest on demand. You can train deeper models, use larger batch sizes, or fit longer sequences on the hardware you already have.

---

## Table of contents

- [Why this exists](#why-this-exists)
- [How it works](#how-it-works)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Usage](#usage)
- [Choosing a checkpointing strategy](#choosing-a-checkpointing-strategy)
- [Performance expectations](#performance-expectations)
- [Caveats and gotchas](#caveats-and-gotchas)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## Why this exists

When you train a neural network, most GPU memory is not consumed by the weights. It is consumed by **activations**: the intermediate outputs of every layer, kept alive so that backpropagation can compute gradients. Activation memory grows linearly with depth and with batch size, and for transformers it also grows with sequence length. This is usually what produces the dreaded `CUDA out of memory` error.

The usual workarounds all have costs:

- **Smaller batch size** hurts throughput and can change optimization behavior.
- **Smaller model** changes what you are trying to build.
- **More GPUs** is expensive and not always available.

Gradient checkpointing (also called activation checkpointing or rematerialization) is a different trade. You pay roughly one extra forward pass of compute, and in return activation memory drops dramatically, often from O(n) to O(√n) in the number of layers.

## How it works

In a standard backward pass, every layer's activations from the forward pass are kept in memory until the gradient for that layer is computed.

With checkpointing, the network is split into **segments**:

1. During the forward pass, only the inputs at segment boundaries (the *checkpoints*) are saved. Activations inside each segment are discarded as soon as they are no longer needed.
2. During the backward pass, when gradients are needed for a segment, its forward computation is **re-run** from the saved checkpoint. This regenerates the activations just in time.
3. Gradients are computed for that segment, then the regenerated activations are freed again.

At any moment, memory holds the checkpoints plus the activations of *one* segment, rather than the activations of the entire network.

## Installation

```bash
pip install gradient-checkpointing
```

From source:

```bash
git clone <repository-url>
cd gradient-checkpointing
pip install -e .
```

**Requirements**

- Python 3.9+
- PyTorch 2.0+
- A CUDA-capable GPU is recommended, but CPU training is supported

## Quick start

Wrap the part of your model that is memory-hungry:

```python
import torch
import torch.nn as nn
from gradient_checkpointing import checkpoint_sequential

model = nn.Sequential(
    *[nn.Sequential(nn.Linear(4096, 4096), nn.GELU()) for _ in range(48)]
).cuda()

x = torch.randn(32, 4096, device="cuda", requires_grad=True)

# Split the 48 blocks into 6 checkpointed segments
out = checkpoint_sequential(model, segments=6, inputs=x)
out.sum().backward()
```

That is the whole change. The training loop, optimizer, and loss function stay exactly as they were.

## Usage

### Checkpointing a single module

Use `checkpoint` to wrap any callable whose internal activations you want to discard:

```python
from gradient_checkpointing import checkpoint

class Block(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, 8, batch_first=True)
        self.mlp = nn.Sequential(nn.Linear(dim, 4 * dim), nn.GELU(), nn.Linear(4 * dim, dim))

    def forward(self, x):
        x = x + self.attn(x, x, x, need_weights=False)[0]
        return x + self.mlp(x)

class Model(nn.Module):
    def __init__(self, dim=1024, depth=24):
        super().__init__()
        self.blocks = nn.ModuleList(Block(dim) for _ in range(depth))

    def forward(self, x):
        for block in self.blocks:
            x = checkpoint(block, x)
        return x
```

### Checkpointing sequential models

`checkpoint_sequential(module, segments, inputs)` divides an `nn.Sequential` into the requested number of segments and checkpoints each one.

### Automatic wrapping

For models built from repeated blocks, you can wrap them without editing the model code:

```python
from gradient_checkpointing import apply_checkpointing

apply_checkpointing(model, target_modules=(Block,))
```

Every instance of `Block` inside `model` is now checkpointed. Call `remove_checkpointing(model)` to undo it, which is useful for comparing memory and speed.

### Mixed precision

Checkpointing works with `torch.autocast` and gradient scalers. The recomputation step restores the autocast state that was active during the original forward pass, so the regenerated activations match.

```python
with torch.autocast("cuda", dtype=torch.bfloat16):
    loss = model(x).float().mean()
loss.backward()
```

### Reproducibility with randomness

Layers such as dropout must produce the *same* random mask during recomputation as they did in the original forward pass. By default, `gradient-checkpointing` saves and restores the RNG state for each checkpointed segment. If you know a segment has no stochastic operations, you can skip this overhead:

```python
checkpoint(block, x, preserve_rng_state=False)
```

## Choosing a checkpointing strategy

| Strategy | Memory saved | Extra compute | When to use |
|---|---|---|---|
| Every block | Highest | ~30-35% | You are badly out of memory |
| Every *k*-th block | Moderate | ~15-25% | Balanced default |
| Selective (attention only) | Moderate to high for long sequences | Low | Transformers with large sequence lengths |
| None | None | None | Everything already fits |

Rules of thumb:

- **Start with the segment count near √(number of layers).** This is the classic optimum for uniform layers.
- **Checkpoint the expensive-in-memory, cheap-to-recompute operations first.** Attention score matrices and elementwise activations are good candidates. Large matrix multiplications are costly to recompute.
- **Measure.** Optimal settings depend on your model, hardware, and batch size.

## Performance expectations

Exact numbers depend heavily on architecture, precision, and hardware, so benchmark your own workload. In general you can expect:

- **Activation memory** drops from growing linearly with depth to growing roughly with the square root of depth when segments are chosen well.
- **Training time** increases because of the additional forward computation. Overhead is commonly in the range of 20-35% when checkpointing every block, and less with selective strategies.
- **Larger batches** enabled by the freed memory often recover some or all of the lost throughput.

To measure your own results:

```python
from gradient_checkpointing.profiling import memory_report

with memory_report() as report:
    loss = model(x).sum()
    loss.backward()

print(report)  # peak allocated memory, recomputed FLOPs, wall time
```

## Caveats and gotchas

- **Inputs must require grad, or use the non-reentrant mode.** With reentrant checkpointing, if none of the inputs require gradients, the checkpointed segment receives no gradients. The default in this library is non-reentrant, which avoids this problem.
- **Side effects run twice.** Anything inside a checkpointed function that mutates state (logging, counters, in-place updates to buffers) executes again during recomputation. Keep checkpointed code free of side effects.
- **BatchNorm running statistics** are updated during both the forward pass and the recomputation. Prefer LayerNorm or GroupNorm in checkpointed regions, or freeze the statistics.
- **Non-determinism.** Non-deterministic kernels can yield slightly different values on recomputation. This is rarely an issue in practice but can matter when debugging numerical differences.
- **Gradient accumulation and DDP** are supported, but wrap checkpointed regions inside the module being parallelized rather than around the parallel wrapper.

## FAQ

**Does checkpointing change the results?**
Mathematically, no. Gradients are identical to those from standard backpropagation, up to floating-point non-determinism.

**Can I combine it with other memory techniques?**
Yes. It composes well with mixed precision, gradient accumulation, optimizer state sharding, and CPU offloading.

**Does it help at inference time?**
No. Inference does not store activations for backward, so there is nothing to save.

**Why is my training slower?**
That is the intended trade. If the slowdown is larger than expected, try checkpointing fewer segments or switching to a selective strategy.

**How many segments should I use?**
Begin with about √(layers), then adjust based on measured peak memory and step time.

## Contributing

Contributions are welcome. To get started:

1. Fork the repository and create a feature branch.
2. Install development dependencies: `pip install -e ".[dev]"`
3. Add tests for any new behavior and run them with `pytest`.
4. Run the formatter and linter before opening a pull request.
5. Describe the motivation and the measured memory and speed impact in your PR.

Bug reports with a minimal reproducing script are especially helpful.

## License

Released under the MIT License. See `LICENSE` for details.
