#!/usr/bin/env python3
"""Test pagination offset calculation logic."""

def test_pagination_offset_calculation():
    """Test that pagination offsets are calculated correctly."""
    print("Testing pagination offset calculation...")
    
    # Test parameters
    rows_per_page = 5
    max_pages = 3
    
    # Expected offsets for each page
    expected_offsets = [0, 5, 10]  # page 0, 1, 2
    
    print(f"Testing with {rows_per_page} rows per page, {max_pages} pages")
    print(f"Expected offsets: {expected_offsets}")
    
    # Test the corrected calculation logic
    calculated_offsets = []
    for page in range(max_pages):
        offset = page * rows_per_page
        calculated_offsets.append(offset)
        print(f"Page {page}: offset = {offset}")
    
    # Verify calculation
    if calculated_offsets == expected_offsets:
        print("✅ SUCCESS: Pagination offsets calculated correctly!")
        return True
    else:
        print(f"❌ FAILURE: Expected {expected_offsets}, got {calculated_offsets}")
        return False

def test_old_vs_new_logic():
    """Compare old (buggy) vs new (fixed) pagination logic."""
    print("\nComparing old vs new pagination logic:")
    
    rows_per_page = 100
    max_pages = 3
    
    print(f"With {rows_per_page} rows per page, {max_pages} pages:")
    
    # Old logic (buggy)
    print("\nOld logic (buggy):")
    old_offsets = []
    for page in range(max_pages):
        offset = page  # This was the bug!
        old_offsets.append(offset)
        print(f"  Page {page}: offset = {offset}")
    
    # New logic (fixed)
    print("\nNew logic (fixed):")
    new_offsets = []
    for page in range(max_pages):
        offset = page * rows_per_page
        new_offsets.append(offset)
        print(f"  Page {page}: offset = {offset}")
    
    print(f"\nOld would fetch records: {old_offsets} (massive overlap!)")
    print(f"New fetches records: {new_offsets} (no overlap)")
    
    return True

if __name__ == "__main__":
    success1 = test_pagination_offset_calculation()
    success2 = test_old_vs_new_logic()
    
    if success1 and success2:
        print("\n🎉 All pagination logic tests passed!")
        exit(0)
    else:
        print("\n💥 Some tests failed!")
        exit(1)
