# IAMDinosaur 🦄

> An Artificial Intelligence to teach Google's Dinosaur to jump cactus.

IAMDinosaur is a small neuroevolution experiment. It watches Chrome's offline dinosaur game, feeds what it sees into a tiny neural network, and uses a genetic algorithm to breed better players until the dinosaur can run for a very long time.

No human plays, and there is no labelled training data. There is only a population of random brains, a score, and natural selection.

## Features

- Plays the real game in your browser by reading the screen and sending key presses
- Small feed-forward neural network for each dinosaur
- Genetic algorithm with selection, crossover, and mutation
- Configurable population size, mutation rate, and network shape
- Saves the best genome so you can resume training or replay a champion
- Runs on Windows, macOS, and Linux

## How It Works

1. **Vision.** The program captures the game area and scans a few rows of pixels ahead of the dinosaur. Dark pixels are obstacles. From these it estimates the distance to the next obstacle, its width and height, and the current game speed.
2. **Decision.** Those values go into a neural network with one hidden layer. A single output decides the action: above the threshold the dinosaur jumps, otherwise it keeps running.
3. **Evaluation.** Each genome plays one run. Its fitness is how far it got before crashing.
4. **Evolution.** When a generation ends, the best performers are kept. Their weights are combined (crossover) and randomly perturbed (mutation) to create the next generation.
5. **Repeat.** Over a few dozen generations the population usually learns to time its jumps and handle faster speeds.

## Requirements

- Node.js 18 or newer
- Google Chrome (or any browser that shows the offline dinosaur game)
- Permission for the app to capture the screen and simulate keyboard input
- A display at 100% scaling is recommended, since scaling can shift pixel positions

## Installation

```bash
git clone https://github.com/<your-user>/IAMDinosaur.git
cd IAMDinosaur
npm install
```

## Usage

1. Open Chrome and go to `chrome://dino`, or disconnect from the internet and open any page.
2. Place the game window where the script can see it and keep it in the foreground.
3. Start the trainer:

```bash
npm start
```

4. Press the spacebar once to begin. The AI takes over from there and prints the generation number, best score, and average score to the console.

To replay the best saved genome without training:

```bash
npm run play
```

## Configuration

Settings live in `config.js`:

| Option | Description | Default |
| --- | --- | --- |
| `populationSize` | Dinosaurs per generation | `12` |
| `hiddenNodes` | Neurons in the hidden layer | `6` |
| `mutationRate` | Chance that a weight is mutated | `0.1` |
| `mutationRange` | Maximum change applied to a weight | `0.5` |
| `eliteCount` | Top genomes copied unchanged | `2` |
| `jumpThreshold` | Output value that triggers a jump | `0.55` |

Larger populations learn in fewer generations but take longer to play each one. If progress stalls, try a higher mutation rate.

## Project Structure

```
IAMDinosaur/
├── src/
│   ├── vision.js      # Screen capture and obstacle detection
│   ├── network.js     # Neural network implementation
│   ├── genetics.js    # Selection, crossover, mutation
│   ├── controller.js  # Keyboard input
│   └── index.js       # Main training loop
├── config.js
├── genomes/           # Saved champions
└── package.json
```

## Troubleshooting

- **The dinosaur never jumps.** Check that the capture region lines up with the game. Log the detected pixels to confirm obstacles are visible.
- **It crashes into the first cactus every time.** Lower `jumpThreshold` or raise `mutationRate` so early generations explore more.
- **Game over is not detected.** Dark mode and custom themes invert the colors. Use the default light theme.
- **Key presses do nothing.** Make sure the browser window has focus and that your OS allows input simulation.

## Roadmap

- Support for ducking under birds
- Headless mode with a simulated game for much faster training
- Training charts for fitness per generation
- Export and import of genomes between machines

## Contributing

Issues and pull requests are welcome. Please open an issue to discuss larger changes first, keep commits focused, and include a short note on how you tested your change.

## License

Released under the MIT License. See `LICENSE` for details.

## Acknowledgements

Inspired by the NEAT and neuroevolution literature, and by everyone who has ever taught a computer to play a game it was never told the rules of. And of course, thanks to the little dinosaur for being a patient test subject.

---

The file layout, commands, and config values above are placeholders, so adjust them to match your actual code. I can save this as `README.md` if you want.
