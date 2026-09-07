# Beyblade X Combo Visualizer

A dynamic, interactive visualization tool for exploring Beyblade X winning combo data. This tool allows you to filter and sort WBO organized event data by parts, date, placements, and ranked status.

## How to Run

Because this visualizer fetches data locally using the JavaScript `fetch()` API (`../compiled_data/extracted_data.json` and `../wbo_bbx_parts.json`), **it cannot be opened directly from your file explorer** (i.e., double-clicking `index.html`). You must serve it using a local web server.

Here are a few easy ways to run the visualizer:

### Method 1: Using `npx serve` (Recommended)
If you have Node.js installed, you can serve the root directory of the archive.
1. Open your terminal and navigate to the root directory (`WBO-BBX-Winning-Combos-Data-Archive`).
2. Run the following command:
   ```bash
   npx serve . -p 3456
   ```
3. Open your browser and navigate to: [http://localhost:3456/combo-visualizer/](http://localhost:3456/combo-visualizer/)

### Method 2: Python Local Server
If you have Python installed, you can use its built-in HTTP server.
1. Open your terminal and navigate to the root directory (`WBO-BBX-Winning-Combos-Data-Archive`).
2. Run the following command:
   ```bash
   python -m http.server 3456
   ```
3. Open your browser and navigate to: [http://localhost:3456/combo-visualizer/](http://localhost:3456/combo-visualizer/)

### Method 3: VS Code Live Server
If you are using Visual Studio Code:
1. Install the **Live Server** extension by Ritwick Dey.
2. Open the root directory in VS Code.
3. Right-click on `combo-visualizer/index.html` and select **"Open with Live Server"**.

## Features
- **View By Categories**: Group the data by Full Combos, Blades, Ratchets, Bits, Lock Chips, etc.
- **Deep Dives**: Click on any rank item to expand it and see the top associated components (e.g., clicking on a Blade will show the top Combos using that Blade).
- **Export to CSV**: Export your current customized view straight to a CSV file for spreadsheet analysis. Full Combos are automatically broken down into their individual components!
- **Extensive Filters**: Filter by event Ranked Status, Placements, and highly customizable Date Ranges.
