# Lead Generator - Quick Start Guide

## 🚀 Quick Start

### Run Your First Lead Generation

```bash
python cli.py --keyword "IT company" --city "Mehsana"
```

This will:
1. Scrape Google Maps for businesses
2. Scrape JustDial for additional listings
3. Find Instagram profiles for each business
4. Clean and deduplicate the data
5. Export results to CSV and Excel in the `outputs/` folder

## 📋 Common Commands

### Basic Usage
```bash
python cli.py --keyword "restaurant" --city "Mumbai"
```

### With Custom Limit
```bash
python cli.py --keyword "coffee shop" --city "Delhi" --limit 100
```

### Skip Instagram Search (Faster)
```bash
python cli.py --keyword "hotel" --city "Bangalore" --skip-instagram
```

### Get Help
```bash
python cli.py --help
```

## 📂 Output Location

All generated files are saved in `outputs/` directory:
- `leads_{keyword}_{city}_{timestamp}.csv`
- `leads_{keyword}_{city}_{timestamp}.xlsx`

## 🔧 Configuration

Edit `config.yml` to customize:
- Browser headless mode
- Page timeout
- Scroll behavior
- Retry attempts
- Delay ranges
- User agents

## 📊 Output Fields

Each lead includes:
- **name**: Business name
- **phone**: Normalized phone number (E164 format)
- **website**: Business website URL
- **address**: Business address
- **instagram**: Instagram profile URL
- **maps_url**: Google Maps URL
- **source**: Data source (Google Maps / JustDial)

## 💡 Tips

1. **Start Small**: Use `--limit 10` to test before running large scrapes
2. **Skip Instagram**: Use `--skip-instagram` for faster results if you don't need social profiles
3. **Check Config**: Adjust delays and retries in `config.yml` for optimal performance
4. **Output Files**: Check the `outputs/` folder for all generated files

## ⚙️ Requirements

All dependencies are already installed. If you need to reinstall:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## 🎯 Examples

### E-commerce Businesses
```bash
python cli.py --keyword "electronics shop" --city "Chennai" --limit 50
```

### Service Providers
```bash
python cli.py --keyword "digital marketing agency" --city "Pune" --limit 30
```

### Restaurants
```bash
python cli.py --keyword "fine dining" --city "Goa" --limit 25
```

## 📝 Notes

- The tool runs in headless mode by default (no browser window)
- Random delays are added between requests to avoid rate limiting
- Duplicates are automatically removed using fuzzy matching
- Invalid entries are filtered out automatically
- All errors are logged but don't stop the scraping process

For more details, see [README.md](README.md)
