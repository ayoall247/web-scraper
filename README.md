# Web Scraper for LLM/Vector Database

A robust, modular web scraper designed to extract clean content from various websites and structure it optimally for LLM and vector database usage.

## 📁 Two Versions Available

- **`scraper.py`** - Full modular architecture with specialized extractors (recommended for production)
- **`simple_scraper.py`** - Single-file version (~300 lines) for quick prototyping

Choose the version that fits your needs. Both produce the same LLM-optimized JSON output.

## Features

- **Multi-site Support**: Specialized extractors for LinkedIn, Reddit, Twitter/X, Wikipedia, and research papers
- **LLM-Optimized Output**: Clean text with structured metadata and pre-chunked content
- **Robust Error Handling**: Retry mechanisms, rate limiting, and graceful degradation
- **Extensible Architecture**: Easy to add new site extractors
- **Content Quality Scoring**: Confidence scores for extraction quality assessment

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Single URL Scraping

```bash
python scraper.py --url "https://www.linkedin.com/blog/engineering/trust-and-safety/viral-spam-content-detection-at-linkedin" --output result.json
```

### Multiple URLs from File

Create a file `urls.txt` with one URL per line:
```
https://www.linkedin.com/blog/engineering/...
https://en.wikipedia.org/wiki/Machine_learning
https://www.reddit.com/r/MachineLearning/...
```

Then run:
```bash
python scraper.py --urls-file urls.txt --output-dir ./results/
```

### Command Line Options

- `--url`: Single URL to scrape
- `--urls-file`: File containing URLs (one per line)
- `--output`: Output JSON file path
- `--output-dir`: Output directory for multiple files
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--retries`: Number of retry attempts (default: 3)
- `--chunk-size`: Text chunk size for processing (default: 1000)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Output Format

The scraper outputs JSON in a format optimized for LLM and vector database usage:

```json
{
  "id": "unique_content_hash",
  "source": {
    "url": "original_url",
    "domain": "example.com",
    "site_type": "linkedin",
    "scraped_at": "2024-01-01T12:00:00Z"
  },
  "content": {
    "title": "Article Title",
    "text": "Clean main content text...",
    "word_count": 1500,
    "language": "en",
    "images": [
      {
        "alt_text": "Image description",
        "caption": "Image caption if available"
      }
    ]
  },
  "metadata": {
    "author": "Author Name",
    "publish_date": "2024-01-01",
    "tags": ["keyword1", "keyword2"],
    "content_type": "article"
  },
  "processing": {
    "extraction_method": "site_specific",
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

## Supported Sites

- **LinkedIn**: Blog posts and articles
- **Reddit**: Posts and top comments
- **Twitter/X**: Tweets and threads
- **Wikipedia**: Articles and encyclopedia entries
- **Research Papers**: arXiv, IEEE, ACM, Nature, Science, etc.
- **Generic**: Any website using readability algorithms

## Architecture

The scraper uses a modular architecture with:

- **Site Detection**: Automatically identifies website type
- **Specialized Extractors**: Custom logic for each site type
- **Content Processing**: Cleans and structures content for LLM usage
- **Error Handling**: Robust retry and fallback mechanisms

## Testing

Run the test script to verify functionality:

```bash
python test_scraper.py
```

This will test the scraper with the LinkedIn blog example and save results to `test_result.json`.

## Example Usage in Python

```python
from scraper import WebScraper

# Initialize scraper
scraper = WebScraper(delay=1.0, retries=3, chunk_size=1000)

# Scrape a single URL
result = scraper.scrape_url("https://example.com/article")

if result:
    print(f"Title: {result['content']['title']}")
    print(f"Word count: {result['content']['word_count']}")
    print(f"Confidence: {result['processing']['confidence_score']}")
    
    # Access pre-chunked content for vector embedding
    for chunk in result['processing']['chunks']:
        print(f"Chunk {chunk['position']}: {chunk['text'][:100]}...")
```

## Benefits for LLM/Vector Database Pipelines

1. **Pre-chunked Content**: Text is already split into optimal chunks for vector embedding
2. **Clean Text**: Removes navigation, ads, and irrelevant content
3. **Structured Metadata**: Rich metadata for filtering and context
4. **Quality Scoring**: Confidence scores help filter low-quality extractions
5. **Consistent Format**: Standardized JSON regardless of source site
6. **Language Detection**: Automatic language identification
7. **Image Descriptions**: Alt text and captions extracted for multimodal use

## Contributing

To add support for a new website:

1. Create a new extractor in `extractors/` inheriting from `BaseExtractor`
2. Add site detection patterns to `SiteDetector`
3. Register the extractor in `ExtractorFactory`

## License

MIT License - see LICENSE file for details.
