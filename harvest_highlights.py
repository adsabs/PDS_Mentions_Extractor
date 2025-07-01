"""Module for harvesting highlights from the NASA ADS Solr API.

This module provides functions to harvest and save highlights from scientific literature
searches using the NASA ADS Solr API.
"""

from typing import Dict, Any, Optional
import json
import logging
import time
from pathlib import Path
import requests
from requests.exceptions import RequestException, HTTPError, Timeout
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from query_solr import query_solr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),  # Increase retry attempts
    wait=wait_exponential(multiplier=2, min=4, max=60),  # Longer waits between retries
    retry=retry_if_exception_type((Timeout, RequestException)),  # Only retry on timeouts and network errors
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
def _make_solr_query(query_params: Dict[str, Any]) -> Dict[str, Any]:
    """Make a Solr query with retry logic.
    
    Args:
        query_params: Dictionary of query parameters
        
    Returns:
        Dict[str, Any]: The parsed JSON response
        
    Raises:
        RequestException: If the request fails after retries
        ValueError: If the response is invalid
    """
    try:
        results = query_solr(query_params)
        return results.json()
    except (RequestException, HTTPError) as e:
        logger.error(f"Solr query failed: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid response from Solr: {e}")
        raise

def harvest_highlights(
    query_string: str,
    save_path: Optional[str] = None,
    max_num_queries: int = 100,
    max_num_rows: int = 100
) -> None:
    """Harvest highlights from Solr for a given query and save them locally.
    
    Args:
        query_string: The Solr query string
        save_path: Path where to save the JSON results. If None, only prints match count
        max_num_queries: Maximum number of queries to make (default: 100)
        max_num_rows: Number of rows to retrieve per query (default: 100, max: 2000)
        
    Raises:
        ValueError: If query parameters are invalid
        RequestException: If API requests fail
        IOError: If saving results fails
    """
    if max_num_rows > 2000:
        raise ValueError("max_num_rows cannot exceed 2000")
        
    # Construct query parameters
    if save_path is None:
        query_params = {
            "q": query_string,
            "fl": "author,title,pubyear,doi",
            "hl": "false",
            "rows": 5,
            "start": 0,
            "sort": "score desc",
        }
    else:
        query_params = {
            "q": query_string,
            "fl": ("abstract,ack,aff,aff_id,alternate_bibcode,alternate_title,arxiv_class,"
                   "author,author_count,author_norm,bibcode,bibgroup,bibstem,citation,"
                   "citation_count,cite_read_boost,classic_factor,comment,copyright,data,"
                   "database,date,doctype,doi,eid,entdate,entry_date,esources,facility,"
                   "first_author,first_author_norm,grant,grant_agencies,grant_id,id,"
                   "identifier,indexstamp,inst,isbn,issn,issue,keyword,keyword_norm,"
                   "keyword_schema,lang,links_data,nedid,nedtype,orcid_pub,orcid_other,"
                   "orcid_user,page,page_count,page_range,property,pub,pub_raw,pubdate,"
                   "pubnote,read_count,reference,simbid,title,vizier,volume,year"),
            "hl": "true",
            "hl.fl": "body,abstract,ack,title",
            "hl.snippets": 4,
            "hl.fragsize": 100,
            "rows": max_num_rows,
            "start": 0,
            "sort": "score desc",
        }

    try:
        # Make the first query
        logger.info("Harvesting the first page")
        results_json = _make_solr_query(query_params)
        
        # Get total number of matches
        total = results_json['response']['numFound']
        logger.info(f"Found {total} matches in SciX")
        
        if save_path is None:
            logger.info("No output file provided - exiting")
            return
            
        # Initialize highlights dictionary
        highlights = results_json['highlighting']
        
        # Add source information to highlights
        for doc in results_json['response']['docs']:
            doc_id = doc['id']
            if doc_id not in highlights:
                highlights[doc_id] = {}
                
            highlights[doc_id]['source'] = {
                'bibcode': doc['bibcode'],
                'title': doc['title'],
                'author': doc['author'],
                'pubdate': doc['pubdate'],
                'doctype': doc['doctype'],
                'property': doc['property'],
                'doi': doc.get('doi'),
                'grant': doc.get('grant')
            }
            
        # Harvest remaining pages
        page = 1
        consecutive_timeouts = 0
        max_consecutive_timeouts = 3
        
        while page < max_num_queries and page * query_params['rows'] < total:
            query_params['start'] = page * query_params['rows']
            
            try:
                logger.info(f"Harvesting page {page}")
                results_json = _make_solr_query(query_params)
                
                # Reset consecutive timeouts counter on success
                consecutive_timeouts = 0
                
                # Add new highlights
                highlights.update(results_json['highlighting'])
                
                # Add source information
                for doc in results_json['response']['docs']:
                    doc_id = doc['id']
                    if doc_id not in highlights:
                        highlights[doc_id] = {}
                        
                    highlights[doc_id]['source'] = {
                        'bibcode': doc['bibcode'],
                        'title': doc['title'],
                        'author': doc['author'],
                        'pubdate': doc['pubdate'],
                        'doctype': doc['doctype'],
                        'property': doc['property'],
                        'doi': doc.get('doi'),
                        'grant': doc.get('grant')
                    }
                    
                page += 1
                
                # Add a longer delay between requests to avoid timeouts
                # Increase delay if we've had timeouts
                delay = 2.0 + (consecutive_timeouts * 1.0)  # 2s base + 1s per timeout
                logger.info(f"Waiting {delay:.1f} seconds before next request")
                time.sleep(delay)
                
            except Timeout as e:
                consecutive_timeouts += 1
                logger.warning(f"Timeout on page {page} (consecutive timeout #{consecutive_timeouts})")
                
                if consecutive_timeouts >= max_consecutive_timeouts:
                    logger.error("Too many consecutive timeouts, saving partial results and exiting")
                    break
                    
                # Add extra delay after timeout
                delay = 5.0 * consecutive_timeouts
                logger.info(f"Waiting {delay:.1f} seconds after timeout")
                time.sleep(delay)
                continue
                
            except (RequestException, HTTPError) as e:
                logger.error(f"Failed to harvest page {page}: {e}")
                raise
                
        # Save results
        try:
            output_path = Path(save_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w") as f:
                json.dump(highlights, f, indent=4)
            logger.info(f"Saved results to {save_path}")
            
            if consecutive_timeouts > 0:
                logger.warning(f"Saved partial results after {consecutive_timeouts} consecutive timeouts")
            
        except IOError as e:
            logger.error(f"Failed to save results: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Harvesting failed: {e}")
        raise

