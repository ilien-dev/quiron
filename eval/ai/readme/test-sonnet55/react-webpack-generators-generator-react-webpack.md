# generator-react-webpack

> Yeoman generator for ReactJS and Webpack

generator-react-webpack scaffolds a modern React application with a working Webpack build, a development server with hot reloading, and a test setup, so you can start writing components instead of wiring up tooling.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Sub-generators](#sub-generators)
- [Project Structure](#project-structure)
- [npm Scripts](#npm-scripts)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- **React-ready setup**: JSX and modern JavaScript compiled through Babel.
- **Webpack build**: separate development and production configurations.
- **Hot module replacement**: edit a component and see the change without a full page reload.
- **Component scaffolding**: generate components, with matching styles and tests, from the command line.
- **Testing included**: a preconfigured test runner with a sample test.
- **Production builds**: minified, hashed bundles ready to deploy.

## Requirements

- [Node.js](https://nodejs.org/) (current LTS recommended)
- npm (bundled with Node.js) or Yarn
- [Yeoman](https://yeoman.io/)

## Installation

Install Yeoman and the generator globally:

```bash
npm install -g yo generator-react-webpack
```

If you prefer not to install globally, you can run the generator with `npx`:

```bash
npx -p yo -p generator-react-webpack yo react-webpack
```

## Quick Start

Create a directory for your project, move into it, and run the generator:

```bash
mkdir my-app
cd my-app
yo react-webpack
```

The generator will ask a few questions about your project, then install dependencies. When it finishes, start the development server:

```bash
npm start
```

Open the address printed in your terminal (usually `http://localhost:8000`) and start editing files in `src/`. The browser refreshes as you save.

## Sub-generators

Once a project exists, use the sub-generators to add to it. Run them from the project root.

### Component

```bash
yo react-webpack:component my-component
```

Creates a new component along with its stylesheet and a test file.

### Nested components

Use a path to place a component in a subfolder:

```bash
yo react-webpack:component forms/login-form
```

### Stateless components

If a component does not need state or lifecycle methods, generate it as a function component:

```bash
yo react-webpack:component my-component --stateless
```

Run `yo react-webpack --help` to see every available option.

## Project Structure

A freshly generated project looks like this:

```
my-app/
├── cfg/                # Webpack configs per environment
├── src/
│   ├── components/     # React components
│   ├── styles/         # Global and shared styles
│   ├── images/         # Static images
│   └── index.js        # Application entry point
├── test/               # Tests and test configuration
├── package.json
└── README.md
```

Exact contents may vary slightly depending on the options you choose during generation.

## npm Scripts

| Script | Description |
| --- | --- |
| `npm start` | Starts the development server with hot reloading |
| `npm run build` | Creates an optimized production build in `dist/` |
| `npm test` | Runs the test suite |
| `npm run lint` | Checks code style |
| `npm run clean` | Removes build output |

## Configuration

Webpack settings live in the `cfg/` directory of your generated project. Typical customizations include:

- **Ports and hosts**: change the development server address in the dev configuration.
- **Loaders**: add loaders for other file types, such as Sass or SVG, by extending the module rules.
- **Aliases**: define import aliases so you can write `import Button from 'components/Button'` instead of long relative paths.
- **Environment variables**: expose values to your code with Webpack's `DefinePlugin`.

Because the configuration is plain JavaScript and lives in your project, you can change anything without ejecting or forking the generator.

## Contributing

Contributions are welcome. To work on the generator locally:

1. Fork and clone the repository.
2. Install dependencies with `npm install`.
3. Link the package so Yeoman can find it: `npm link`.
4. Run `yo react-webpack` in a scratch directory to try your changes.
5. Run `npm test` before opening a pull request.

Please open an issue before starting large changes so we can discuss the approach. Keep pull requests focused, and include tests for new behavior.

### Reporting issues

When filing a bug, include your Node.js and npm versions, your operating system, the exact command you ran, and the full error output. This makes problems much faster to reproduce.

## License

Released under the MIT License. See the `LICENSE` file for details.
