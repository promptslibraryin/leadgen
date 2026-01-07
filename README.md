# Lead Generator

An advanced Python-based lead generation tool that automatically scrapes business leads from multiple sources including Google Maps, JustDial, and Instagram.

## Features

- **Multi-Source Scraping**: Collects data from Google Maps, JustDial, and Instagram
- **Smart Data Cleaning**: Normalizes phone numbers, deduplicates entries, and merges results
- **Instagram Detection**: Automatically finds Instagram profiles from websites or Google search
- **Dual Export**: Generates both CSV and Excel files with timestamped filenames
- **Production-Ready**: Includes retry logic, error handling, and headless browser automation
- **Configurable**: YAML-based configuration for browser settings and scraping parameters

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browser

```bash
python -m playwright install chromium
```

## Usage

### Basic Command

```bash
python cli.py --keyword "IT company" --city "Mehsana"
```

### Advanced Usage

```bash
python cli.py --keyword "restaurant" --city "Mumbai" --limit 100
```

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--keyword` | `-k` | Business keyword to search for (e.g., "IT company", "restaurant") | Required |
| `--city` | `-c` | City to search in (e.g., "Mehsana", "Mumbai") | Required |
| `--limit` | `-l` | Maximum number of leads to scrape | 50 |
| `--skip-instagram` | - | Skip Instagram profile search | False |

### Examples

```bash
# Search for IT companies in Mehsana
python cli.py --keyword "IT company" --city "Mehsana"

# Search for restaurants in Mumbai with limit of 100
python cli.py --keyword "restaurant" --city "Mumbai" --limit 100

# Search without Instagram lookup
python cli.py --keyword "coffee shop" --city "Delhi" --skip-instagram
```

## Output

The tool generates two files in the `outputs/` directory:

- `leads_{keyword}_{city}_{timestamp}.csv` - CSV format
- `leads_{keyword}_{city}_{timestamp}.xlsx` - Excel format

### Output Fields

- **name**: Business name
- **phone**: Normalized phone number (E164 format)
- **website**: Business website URL
- **address**: Business address
- **instagram**: Instagram profile URL
- **maps_url**: Google Maps URL
- **source**: Data source (Google Maps / JustDial)

## Project Structure

```
lead-generator/
├── cli.py                 # Main CLI interface
├── requirements.txt       # Python dependencies
├── config.yml            # Configuration settings
├── README.md             # Documentation
├── utils/                # Utility modules
│   ├── logger.py         # Logging setup
│   ├── retryer.py        # Retry decorator
│   └── proxies.py        # User-agent rotation
├── scrapers/             # Scraping modules
│   ├── google_maps.py    # Google Maps scraper
│   ├── justdial.py       # JustDial scraper
│   └── instagram_finder.py # Instagram profile finder
├── cleaner.py            # Data cleaning and deduplication
├── exporter.py           # CSV/Excel export
├── outputs/              # Generated lead files
└── db/                   # Database storage (optional)
```

## Configuration

Edit `config.yml` to customize browser and scraping settings:

```yaml
browser:
  headless: true          # Run browser in headless mode
  timeout: 20            # Page load timeout in seconds
  max_scroll: 10         # Maximum scroll attempts

scraping:
  delay_min: 0.5         # Minimum delay between requests
  delay_max: 2.0         # Maximum delay between requests
  max_retries: 3         # Maximum retry attempts
```

## How It Works

1. **Google Maps Scraping**: Searches for businesses using the keyword and city, scrolls through results, and extracts detailed information from each place page.

2. **JustDial Scraping**: Searches JustDial listings and extracts business information from listing cards.

3. **Data Cleaning**: Normalizes phone numbers to E164 format, removes duplicates using fuzzy matching, and cleans URLs.

4. **Instagram Finding**: Attempts to find Instagram profiles by:
   - Detecting Instagram links from business websites
   - Google searching for "{Business Name} Instagram"
   - Extracting and validating Instagram URLs

5. **Export**: Saves cleaned and merged data to both CSV and Excel formats with proper formatting.

## Notes

- The tool runs in headless mode by default for better performance
- Random delays are added between requests to avoid rate limiting
- Duplicate entries are automatically removed using fuzzy name matching
- Invalid phone numbers and blank entries are filtered out
- All errors are logged but don't stop the scraping process

## Requirements

- Python 3.8+
- Playwright (with Chromium browser)
- See `requirements.txt` for complete list

## Troubleshooting

### Browser Installation Issues

If you encounter issues with Playwright:
```bash
python -m playwright install --force chromium
```

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### No Results Found

- Check your internet connection
- Verify the keyword and city are spelled correctly
- Try increasing the limit parameter
- Check if the websites are accessible from your location

## License

This project is for educational and research purposes only. Please respect the terms of service of the websites being scraped.
