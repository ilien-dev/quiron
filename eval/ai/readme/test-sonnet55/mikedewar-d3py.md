# d3py

**A plotting library for Python, based on D3.**

d3py brings the declarative, data-driven approach of D3.js to Python. You describe your data and how it maps to visual marks, and d3py generates clean, interactive SVG charts. View them in a notebook, export them as standalone HTML, or embed them in a web app.

## Why d3py?

D3 is one of the most expressive visualization tools available, but using it means writing JavaScript. Many Python plotting libraries offer ready-made chart types with little room for custom designs. d3py aims for the middle ground:

- **Data-driven.** Bind a DataFrame, list, or NumPy array to marks and let scales do the work.
- **Composable.** Scales, axes, marks, and layouts are separate pieces that you combine.
- **Interactive by default.** Tooltips, zoom, pan, and brushing work without any JavaScript.
- **Portable output.** Charts are plain SVG plus a small runtime, so they work anywhere a browser does.
- **Familiar concepts.** If you know D3's scales, selections, and joins, the API will feel natural.

## Installation

```bash
pip install d3py
```

d3py requires Python 3.9 or newer. Optional extras add integrations:

```bash
pip install "d3py[pandas]"    # DataFrame support
pip install "d3py[jupyter]"   # inline notebook rendering
```

## Quick start

```python
import d3py
import pandas as pd

df = pd.read_csv("penguins.csv")

chart = (
    d3py.Chart(df, width=640, height=400)
    .x("bill_length_mm", scale="linear")
    .y("body_mass_g", scale="linear")
    .color("species", scheme="category10")
    .mark_point(size=40, opacity=0.8)
    .axis("x", label="Bill length (mm)")
    .axis("y", label="Body mass (g)")
    .tooltip(["species", "island"])
)

chart.show()               # open in a browser or render inline in Jupyter
chart.save("penguins.html")
```

## Core concepts

**Chart.** The container that holds your data, dimensions, and margins. Every other piece attaches to it.

**Scales.** Functions that map data values to visual values. d3py supports linear, log, power, time, ordinal, and band scales, plus D3's color schemes.

**Marks.** The shapes drawn for each row of data: `mark_point`, `mark_line`, `mark_bar`, `mark_area`, `mark_text`, and `mark_rule`. Marks can be layered in a single chart.

**Axes and legends.** Generated from your scales, and customizable through tick count, format, and label options.

**Layouts.** Higher-level helpers for stacks, histograms, treemaps, force-directed graphs, and chord diagrams.

**Interactions.** Add behaviors such as `.zoom()`, `.brush()`, and `.tooltip()`, then link them across charts to build coordinated views.

## More examples

A line chart with multiple series:

```python
d3py.Chart(stocks).x("date", scale="time").y("close").color("symbol").mark_line().show()
```

A histogram with automatic binning:

```python
d3py.Chart(df).x("body_mass_g").histogram(bins=20).mark_bar().show()
```

Two charts linked by a shared brush:

```python
scatter = d3py.Chart(df).x("bill_length_mm").y("flipper_length_mm").mark_point().brush(name="sel")
bars = d3py.Chart(df).x("species").count().mark_bar().filter_by("sel")

d3py.hconcat(scatter, bars).show()
```

## Rendering and export

d3py renders to SVG in the browser. From the same chart object you can:

- `chart.show()` to display it interactively
- `chart.save("chart.html")` to write a self-contained HTML file
- `chart.save("chart.svg")` to write static SVG
- `chart.to_json()` to get the chart specification for use in your own apps

PNG and PDF export are available when a headless browser is installed (`pip install "d3py[export]"`).

## Working in Jupyter

With the `jupyter` extra installed, charts display inline when they are the last expression in a cell. Interactions such as selections are readable from Python, so you can use a brushed region to filter a DataFrame:

```python
selected = scatter.selection("sel")
df.loc[selected.indices]
```

## Customization

Because d3py follows D3's model, you can drop down a level when the built-in options are not enough. Pass custom scale domains and ranges, supply your own formatting functions, or inject raw D3 code with `chart.extend(js="...")`. Themes are plain dictionaries, so sharing a consistent style across a project takes a few lines:

```python
d3py.themes.register("report", {"font": "Inter", "grid": True, "palette": "tableau10"})
chart.theme("report")
```

## Roadmap

- Geographic projections and map layers
- Animated transitions between data updates
- Accessibility improvements, including ARIA labels and keyboard navigation
- A gallery site with runnable examples

## Contributing

Contributions are welcome. To get started:

```bash
git clone https://github.com/your-org/d3py.git
cd d3py
pip install -e ".[dev]"
pytest
```

Please open an issue before starting large changes so we can discuss the design. Bug reports with a minimal reproducible example are especially helpful.

## License

d3py is released under the MIT License. D3 is © Mike Bostock and contributors and is distributed under the ISC License.

---

The README is about 720 words. The API shown (method names, extras, export options) is illustrative since I had no source to check, so adjust it to match the real library. I also corrected "plottling" to "plotting" in the tagline, and the clone URL is a placeholder.
