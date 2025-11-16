#!/usr/bin/env python3
"""Test script to verify API optimization and caching"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_api_endpoint():
    """Test the API endpoint response time"""
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/data")
    duration = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        return duration, data.get('cookie_count', 0)
    return duration, None

def test_concurrent_requests(num_requests=10):
    """Test multiple concurrent requests to check caching"""
    print(f"Testing {num_requests} concurrent requests...")
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        start = time.time()
        futures = [executor.submit(test_api_endpoint) for _ in range(num_requests)]
        results = [future.result() for future in futures]
        total_time = time.time() - start
    
    durations = [r[0] for r in results]
    avg_duration = sum(durations) / len(durations)
    
    print(f"Total time for {num_requests} requests: {total_time:.3f}s")
    print(f"Average response time: {avg_duration:.3f}s")
    print(f"Min/Max response time: {min(durations):.3f}s / {max(durations):.3f}s")
    
    # Check if all requests got the same data (cached)
    cookie_counts = [r[1] for r in results if r[1] is not None]
    if cookie_counts and len(set(cookie_counts)) == 1:
        print("✓ All requests returned the same data (caching working)")
    else:
        print("✗ Requests returned different data (caching issue)")

def test_cache_expiration():
    """Test that cache expires after 0.5 seconds"""
    print("\nTesting cache expiration...")
    
    # First request
    _, count1 = test_api_endpoint()
    print(f"First request: {count1} cookies")
    
    # Immediate second request (should be cached)
    start = time.time()
    _, count2 = test_api_endpoint()
    duration2 = time.time() - start
    print(f"Immediate second request: {count2} cookies (took {duration2:.3f}s)")
    
    # Wait for cache to expire
    time.sleep(0.6)
    
    # Third request (should be fresh)
    start = time.time()
    _, count3 = test_api_endpoint()
    duration3 = time.time() - start
    print(f"After cache expiry: {count3} cookies (took {duration3:.3f}s)")
    
    if duration2 < duration3 * 0.5:  # Cached request should be much faster
        print("✓ Cache is working correctly")
    else:
        print("✗ Cache might not be working properly")

def main():
    print("API Optimization Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"✓ Server is running at {BASE_URL}")
    except:
        print(f"✗ Server is not running at {BASE_URL}")
        print("Please start the Flask app first: python app.py")
        return
    
    # Run tests
    test_concurrent_requests()
    test_cache_expiration()
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    main()
