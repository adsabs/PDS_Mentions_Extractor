"""Script for harvesting Solr highlights of Planetary Data System (PDS) mentions.

This script searches for PDS mentions in scientific literature and saves the highlights
to JSON files for further analysis.
"""

from typing import List, Optional
import argparse
import pandas as pd
from pathlib import Path

# Local imports
from harvest_highlights import harvest_highlights

def build_query_string(terms: List[str]) -> str:
    """Build a Solr query string from a list of search terms.
    
    Args:
        terms: List of search terms to include in the query
        
    Returns:
        A properly formatted Solr query string
    """
    # Filter out any None/NaN values and join with OR
    valid_terms = [term for term in terms if pd.notna(term)]
    if not valid_terms:
        raise ValueError("No valid search terms provided")
    
    # Join terms with OR and wrap in quotes
    terms_str = ' OR '.join(f'"{term}"' for term in valid_terms)
    return f'full:({terms_str})'

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Search for PDS mentions in scientific literature using NASA ADS API"
    )
    parser.add_argument(
        "--search-term",
        type=str,
        default="Planetary Data System",
        help="Search term to look for (default: 'Planetary Data System')"
    )
    parser.add_argument(
        "--search-field",
        type=str,
        choices=["body", "full", "title", "abstract"],
        default="body",
        help="Field to search in (default: body)"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Maximum number of pages to retrieve (default: 1)"
    )
    parser.add_argument(
        "--rows-per-page",
        type=int,
        default=100,
        help="Number of results per page (default: 100, max: 2000)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./pds_mentions_results",
        help="Directory to save results (default: ./pds_mentions_results)"
    )
    return parser.parse_args()

def main() -> None:
    """Main execution function for harvesting PDS mentions."""
    args = parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build output filename
    output_file = output_dir / f"{args.search_field}_{args.search_term.replace(' ', '')}.json"
    
    # Build query string
    query_string = f'{args.search_field}:"{args.search_term}"'
    
    # Execute the search
    harvest_highlights(
        query_string=query_string,
        save_path=str(output_file),
        max_num_queries=args.max_pages,
        max_num_rows=args.rows_per_page
    )

if __name__ == "__main__":
    main()