# Simple Web Scraper for LLM/Vector Database

A streamlined, single-file web scraper that extracts clean content from websites and structures it for LLM and vector database usage.

## Quick Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install requests beautifulsoup4 lxml readability-lxml langdetect

# Test it
python simple_scraper.py --url "https://en.wikipedia.org/wiki/Machine_learning" --output result.json
```

## Usage

```bash
# Single URL
python simple_scraper.py --url "https://example.com" --output result.json

# Multiple URLs from file
python simple_scraper.py --urls-file urls.txt --output-dir ./results/

# Custom settings
python simple_scraper.py --url "https://example.com" --chunk-size 500 --delay 2.0
```

## Features

- **Single File**: Everything in one ~300 line Python file
- **Multi-site Support**: LinkedIn, Wikipedia, Reddit, Twitter/X, Research papers
- **LLM Ready**: Pre-chunked content with metadata
- **Clean Output**: Removes navigation, ads, and clutter
- **Robust**: Retry logic and error handling

## Output Format

```json
{
  "id": "unique_hash",
  "source": {
    "url": "original_url",
    "domain": "example.com",
    "site_type": "wikipedia",
    "scraped_at": "2024-01-01T12:00:00Z"
  },
  "content": {
    "title": "Article Title",
    "text": "Clean content...",
    "word_count": 1500,
    "language": "en"
  },
  "metadata": {
    "tags": ["keyword1", "keyword2"],
    "content_type": "article"
  },
  "processing": {
    "confidence_score": 0.95,
    "chunks": [
      {
        "text": "Text chunk for vector embedding",
        "position": 1,
        "char_count": 500
      }
    ]
  }
}
```

## Why Use This?

- **Simple**: One file, minimal dependencies
- **Fast**: Direct extraction without complex processing
- **Reliable**: Tested with real websites
- **Ready**: Output optimized for vector databases

Perfect for quick prototyping or when you need a lightweight scraper without the full modular architecture.
