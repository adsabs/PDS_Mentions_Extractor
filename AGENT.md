# PDS Mentions Extractor Agent Guide

## Build/Lint/Test Commands
- **Run script**: `python pds_scix_api_highlights.py [options]`
- **Run with custom params**: `python pds_scix_api_highlights.py --search-term "term" --max-pages 5 --rows-per-page 200`
- **Install dependencies**: `pip install -r requirements.txt`
- **Test API connection**: Run any script - they have built-in error handling and logging
- **No formal test suite** - validate by running scripts with different parameters

## Architecture
- **Main entry point**: `pds_scix_api_highlights.py` - CLI interface for searching PDS mentions  
- **Core harvesting**: `harvest_highlights.py` - fetches data from NASA ADS API with retry logic
- **API interface**: `query_solr.py` - handles NASA ADS Solr API requests with authentication
- **Config**: `local_config_jarmak.py` (user-specific) contains NASA ADS API token
- **Output**: JSON files saved to `./pds_mentions_results/` directory

## Code Style & Conventions
- **Type hints**: Use typing module imports (Dict, List, Optional, Any)
- **Docstrings**: Google-style docstrings with Args/Returns/Raises sections
- **Error handling**: Comprehensive exception handling with logging, retry decorators from tenacity
- **Imports**: Group standard library, third-party, then local imports with blank lines
- **Logging**: Use module-level logger with descriptive messages
- **Naming**: snake_case for functions/variables, descriptive parameter names
- **File paths**: Use pathlib.Path for file operations
- **API timeouts**: Use reasonable timeouts (10s connect, 60s read) with exponential backoff
