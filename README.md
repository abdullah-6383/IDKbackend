# Google Search + Gemini Relevance Filter

Single-file system that searches Google and filters links using Gemini AI for relevance.

## Usage

```powershell
python main.py
```

## Configuration

Edit `config.json` to control:
- `links_per_text`: Number of links to get per search (1-10)
- `relevance_threshold`: Minimum confidence for relevance (0.0-1.0)
- `requests_per_minute`: Gemini API rate limit (default: 10)

Edit `data/input.json` to set the topic for relevance filtering.

## How It Works

1. Extracts keywords from `data/input.json` topic
2. Reads text from `data/common.json`, `data/leftist.json`, `data/rightist.json`
3. Enhances each search query with topic keywords
4. Searches Google for each enhanced query
5. Uses Gemini 2.0 Flash to check if links are relevant to the topic
6. Checks trust score for each relevant link
7. Saves results to separate files for each source
8. Automatically handles rate limits to avoid API quota errors

## Output

Creates 3 separate files:
- `relevant_common.json` - All items from common.json
- `relevant_leftist.json` - All items from leftist.json  
- `relevant_rightist.json` - All items from rightist.json

Each file contains:
- Topic and timestamp
- All original items ordered by `combined_score` (bias_x * significance_y) descending
- For each item:
  - Original text, bias_x, significance_y, combined_score, color
  - `relevant_links` array (empty if no relevant links found)
  - For relevant links: title, URL, snippet, trust score, source type

## Rate Limiting

System automatically:
- Monitors API usage to stay under 10 requests per minute
- Waits when approaching rate limit
- Retries with longer delays on quota errors
- Prevents 429 errors

## Requirements

```powershell
pip install -r requirements.txt
```
