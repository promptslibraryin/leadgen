# Lead Generator Project

## Overview

This is a comprehensive Python-based lead generation tool that scrapes business data from multiple sources:
- Google Maps
- JustDial  
- Instagram

The tool accepts a keyword and city as input, scrapes business information, cleans and deduplicates the data, finds Instagram profiles, and exports results to CSV and Excel files.

## Recent Changes

- **2024-11-14**: Initial project creation
  - Implemented complete project structure with all modules
  - Created Google Maps scraper using Playwright sync API
  - Created JustDial scraper with BeautifulSoup
  - Created Instagram profile finder with website detection and Google search
  - Implemented data cleaning with phone normalization and fuzzy deduplication
  - Created dual export functionality (CSV + Excel)
  - Set up CLI interface with argument parsing
  - Installed all dependencies and Playwright browser

## Project Architecture

### Core Components

1. **CLI Interface** (`cli.py`)
   - Argument parsing for keyword, city, and limit
   - Orchestrates the scraping pipeline
   - Progress logging and error handling

2. **Scrapers** (`scrapers/`)
   - `google_maps.py`: Playwright-based Google Maps scraper
   - `justdial.py`: JustDial listings scraper
   - `instagram_finder.py`: Instagram profile detection and search

3. **Data Processing**
   - `cleaner.py`: Phone normalization, deduplication, data cleaning
   - `exporter.py`: CSV and Excel export with timestamps

4. **Utilities** (`utils/`)
   - `logger.py`: Centralized logging setup
   - `retryer.py`: Retry decorator for resilience
   - `proxies.py`: User-agent rotation and delay management

### Technology Stack

- **Python 3.11**
- **Playwright**: Browser automation for Google Maps
- **BeautifulSoup**: HTML parsing for JustDial
- **pandas**: Data manipulation and export
- **phonenumbers**: Phone number normalization
- **rapidfuzz**: Fuzzy matching for deduplication
- **pyyaml**: Configuration management

### Key Features

1. **Headless Browser Automation**: Runs Playwright in headless mode for efficiency
2. **Smart Scrolling**: Automatically scrolls Google Maps results panel
3. **Error Resilience**: Continues scraping even if individual listings fail
4. **Duplicate Detection**: Uses fuzzy matching to detect similar business names
5. **Phone Normalization**: Converts all phone numbers to E164 format
6. **Instagram Discovery**: Two-step approach (website detection + Google search)
7. **Random Delays**: Adds random delays to avoid detection
8. **User-Agent Rotation**: Rotates user agents from config file

## How to Use

### Basic Command
```bash
python cli.py --keyword "IT company" --city "Mehsana"
```

### With Custom Limit
```bash
python cli.py --keyword "restaurant" --city "Mumbai" --limit 100
```

### Skip Instagram Search
```bash
python cli.py --keyword "coffee shop" --city "Delhi" --skip-instagram
```

## Output Location

All generated files are saved in the `outputs/` directory with the format:
- `leads_{keyword}_{city}_{timestamp}.csv`
- `leads_{keyword}_{city}_{timestamp}.xlsx`

## Configuration

Browser and scraping settings can be customized in `config.yml`:
- Browser headless mode and timeout
- Scroll behavior
- Delay ranges
- User-agent list

## Development Notes

- The project uses Playwright sync API (not async) as specified
- Error handling is implemented to skip broken listings without crashing
- All imports are validated and working
- Dependencies are installed via requirements.txt
- Playwright browser (Chromium) is installed and ready
