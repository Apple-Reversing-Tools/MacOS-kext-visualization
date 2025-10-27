# macOS Kext Analysis Suite

Analysis tools for macOS Kernel Extensions with visualization.

## Screenshots

<div align="center">
  <img src="img/스크린샷 2025-10-27 오후 4.19.56.png" alt="Screenshot 1" width="600"/>
  <p>전체 Kext 분석 대시보드</p>
</div>

<div align="center">
  <img src="img/스크린샷 2025-10-27 오후 4.20.29.png" alt="Screenshot 2" width="600"/>
  <p>VM Apple Kext 의존성 그래프</p>
</div>

<div align="center">
  <img src="img/스크린샷 2025-10-27 오후 4.20.40.png" alt="Screenshot 3" width="600"/>
  <p>Host Kext 상세 정보</p>
</div>

## Quick Start

```bash
# Run full analysis
python main.py --all

# Individual tasks
python main.py --analyze      # Extract kext data
python main.py --compare      # Compare datasets
python main.py --visualize    # Generate HTML
```

## Files

- `main.py` - Main entry point
- `analyze_kexts.py` - Extract kext data from `/System/Library/Extensions`
- `compare_kexts.py` - Compare VM Apple vs Host
- `generate_visualizations.py` - Create HTML visualizations

## Output

Each dataset contains:
- `kexts_data.json` - Structured kext data
- `kexts_graph.graphml` - Dependency graph
- `kext_visualization.html` - Interactive visualization

## Requirements

- Python 3.7+
- Standard library modules only
- Web browser for HTML visualizations

## GitHub Pages Deployment

This project is configured for automatic deployment to GitHub Pages.

### Deployment Steps

1. **Push to GitHub:**
   ```bash
   git clone https://github.com/Apple-Reversing-Tools/MacOS-kext-visualization.git
   cd MacOS-kext-visualization
   
   # Copy deploy folder contents to repository root
   cp -r /path/to/deploy/* .
   
   git add .
   git commit -m "Add kext visualization files"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings > Pages
   - Source: select "GitHub Actions"
   - The site will be published automatically on push

3. **Access Your Site:**
   - URL: `https://Apple-Reversing-Tools.github.io/MacOS-kext-visualization/`
   - The `index.html` file will be automatically served as the homepage

### Manual Deployment (Alternative)

If you prefer to use the `gh-pages` branch method:

```bash
# Create and checkout gh-pages branch
git checkout --orphan gh-pages
git rm -rf .

# Copy all files from deploy folder
cp -r /path/to/deploy/* .

git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages

# Switch back to main branch
git checkout main
```

Then configure GitHub Pages to use the `gh-pages` branch as the source.
