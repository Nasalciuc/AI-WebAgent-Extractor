#!/usr/bin/env python3
"""
Darwin.md Cloudflare Bypass Example
This script demonstrates how to use the enhanced scraper with Cloudflare bypass capabilities
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import the enhanced scraper
from darwin_scraper_cloudflare import DarwinCloudflareBypass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloudflare_example.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables for API keys
load_dotenv()

def main():
    """Main function to demonstrate Cloudflare bypass functionality"""
    print("Darwin.md Cloudflare Bypass Example")
    print("===================================")
    
    # Get API key from environment or use dummy key
    openai_api_key = os.getenv("OPENAI_API_KEY", "dummy_key")
    
    # Initialize the enhanced scraper
    print("\n[1] Initializing CloudflareBypass scraper...")
    scraper = DarwinCloudflareBypass(openai_api_key=openai_api_key)
    
    # Test URLs
    test_urls = [
        "https://darwin.md/telefoane/smartphone",  # Category page
        "https://darwin.md/telefoane/apple-iphone-15-pro-128gb",  # Product page
    ]
    
    # Example 1: Normal mode vs Anti-Cloudflare mode
    print("\n[2] Testing normal mode vs anti-Cloudflare mode...")
    
    # Test with normal mode first
    print("\n   [2.1] Using normal extraction mode:")
    normal_results = []
    for url in test_urls:
        print(f"      Testing {url}...")
        try:
            start_time = datetime.now()
            result = scraper._extract_product_details_impl(url)
            duration = (datetime.now() - start_time).total_seconds()
            success = not result.get("error")
            normal_results.append((url, success, duration, result.get("extraction_method", "unknown")))
            status = "✅ Success" if success else f"❌ Failed: {result.get('error')}"
            print(f"      {status} (Method: {result.get('extraction_method', 'unknown')}, Time: {duration:.2f}s)")
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
    
    # Enable anti-Cloudflare mode and test again
    print("\n   [2.2] Enabling anti-Cloudflare mode:")
    scraper.enable_anti_cloudflare()
    cf_results = []
    for url in test_urls:
        print(f"      Testing {url}...")
        try:
            start_time = datetime.now()
            result = scraper._extract_product_details_impl(url)
            duration = (datetime.now() - start_time).total_seconds()
            success = not result.get("error")
            cf_results.append((url, success, duration, result.get("extraction_method", "unknown")))
            status = "✅ Success" if success else f"❌ Failed: {result.get('error')}"
            print(f"      {status} (Method: {result.get('extraction_method', 'unknown')}, Time: {duration:.2f}s)")
        except Exception as e:
            print(f"      ❌ Exception: {str(e)}")
    
    # Example 2: Full product extraction with anti-Cloudflare mode
    print("\n[3] Extracting product details with anti-Cloudflare mode...")
    product_url = "https://darwin.md/telefoane/apple-iphone-15-pro-128gb"
    print(f"   Extracting: {product_url}")
    try:
        result = scraper.extract_product_details(product_url)
        if not result.get("error"):
            print("   ✅ Product extracted successfully:")
            for key, value in result.items():
                if key in ["name", "price", "category", "availability", "extraction_method"]:
                    print(f"      {key}: {value}")
        else:
            print(f"   ❌ Failed to extract product: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Example 3: Run specific Cloudflare bypass test
    print("\n[4] Running dedicated Cloudflare bypass test...")
    test_result = scraper.test_cloudflare_bypass(product_url)
    print(f"   Test URL: {product_url}")
    print(f"   Success: {'✅ Yes' if test_result['success'] else '❌ No'}")
    print(f"   Successful method: {test_result['successful_method']}")
    print(f"   Screenshots captured: {len(test_result['screenshots'])}")
    if test_result['screenshots']:
        print(f"   Latest screenshot: {test_result['screenshots'][-1]}")
    
    # Summary
    print("\n[5] Summary:")
    print("   Normal mode results:")
    for url, success, duration, method in normal_results:
        print(f"      {'✅' if success else '❌'} {url.split('/')[-1]} - Method: {method}, Time: {duration:.2f}s")
    
    print("   Anti-Cloudflare mode results:")
    for url, success, duration, method in cf_results:
        print(f"      {'✅' if success else '❌'} {url.split('/')[-1]} - Method: {method}, Time: {duration:.2f}s")
    
    print("\nCheck the 'screenshots' directory for visual confirmation of the tests")

if __name__ == "__main__":
    main()