#!/usr/bin/env python3
"""Quick test to verify pagination fix works correctly."""

import json
import tempfile
from pathlib import Path
from harvest_highlights import harvest_highlights

def test_pagination():
    """Test that pagination works without duplicates."""
    print("Testing pagination fix...")
    
    # Use a temporary file for output
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Test with 3 pages of 5 results each
        query_string = 'body:"Planetary Data System"'
        harvest_highlights(
            query_string=query_string,
            save_path=tmp_path,
            max_num_queries=3,
            max_num_rows=5
        )
        
        # Load and analyze results
        with open(tmp_path, 'r') as f:
            results = json.load(f)
        
        # Get all document IDs
        doc_ids = list(results.keys())
        unique_ids = set(doc_ids)
        
        print(f"Total documents retrieved: {len(doc_ids)}")
        print(f"Unique documents: {len(unique_ids)}")
        print(f"Expected maximum: 15 (3 pages × 5 results)")
        
        # Check for duplicates
        if len(doc_ids) == len(unique_ids):
            print("✅ SUCCESS: No duplicate documents found!")
        else:
            duplicates = len(doc_ids) - len(unique_ids)
            print(f"❌ FAILURE: Found {duplicates} duplicate documents")
            
        # Show sample IDs for verification
        print(f"\nSample document IDs:")
        for i, doc_id in enumerate(doc_ids[:5]):
            print(f"  {i+1}. {doc_id}")
            
        return len(doc_ids) == len(unique_ids)
        
    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)

if __name__ == "__main__":
    success = test_pagination()
    exit(0 if success else 1)
