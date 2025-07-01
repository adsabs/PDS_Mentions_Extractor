# PDS Mentions Extractor

A Python tool for extracting mentions of the Planetary Data System (PDS) from scientific literature using the NASA ADS API.

## Features

- Search for PDS mentions in scientific literature
- Extract highlights and context around mentions
- Save results in JSON format for further analysis
- Configurable search parameters
- Robust error handling and retry logic
- Rate limiting to avoid API timeouts

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/PDS_Mentions_Extractor.git
cd PDS_Mentions_Extractor
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Get a NASA ADS API token:
   - Go to https://ui.adsabs.harvard.edu/
   - Create an account or log in
   - Go to your profile settings
   - Generate an API token
   - Create a file named `local_config_jarmak.py` in the project directory
   - Add your token as a single line in the file

## Usage

Basic usage with default settings (searches in body text, retrieves first page of results):
```bash
python pds_scix_api_highlights.py
```

Search with custom parameters:
```bash
python pds_scix_api_highlights.py \
    --search-term "Planetary Data System" \
    --search-field body \
    --max-pages 5 \
    --rows-per-page 200 \
    --output-dir ./my_results
```

### Command Line Arguments

- `--search-term`: The term to search for (default: "Planetary Data System")
- `--search-field`: Field to search in (choices: body, full, title, abstract; default: body)
- `--max-pages`: Maximum number of pages to retrieve (default: 1)
- `--rows-per-page`: Number of results per page (default: 100, max: 2000)
- `--output-dir`: Directory to save results (default: ./pds_mentions_results)

### Output Format

Results are saved in JSON format with the following structure:
```json
{
    "document_id": {
        "highlighted_text": [...],
        "source": {
            "bibcode": "...",
            "title": "...",
            "author": [...],
            "pubdate": "...",
            "doctype": "...",
            "property": [...],
            "doi": "...",
            "grant": [...]
        }
    }
}
```

## Error Handling

The script includes robust error handling:
- Automatic retries for failed requests
- Rate limiting to avoid API timeouts
- Partial results saving if the script is interrupted
- Detailed logging of operations and errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NASA ADS API for providing access to scientific literature
- Planetary Data System for their valuable scientific data 