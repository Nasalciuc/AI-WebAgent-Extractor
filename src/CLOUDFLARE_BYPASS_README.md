# Darwin.md Cloudflare Bypass Module

## Overview

This module enhances the original Darwin.md scraper with specialized functionality to bypass Cloudflare's anti-bot protection. It leverages advanced browser automation techniques to mimic human behavior and overcome protection mechanisms that typically block automated scrapers.

## Key Features

- **Visual Browser Mode**: Uses non-headless browser automation to prevent detection
- **Human-like Behavior**: Implements realistic scrolling, delays, and interaction patterns
- **Cloudflare Challenge Detection**: Automatically detects and waits for challenge resolution
- **Anti-Detection Techniques**: Neutralizes common WebDriver detection methods
- **Multiple Backend Support**: Implements bypass methods using both SeleniumBase and DrissionPage
- **Screenshot Captures**: Records visual evidence of successful bypasses for debugging
- **Modular Design**: Seamlessly integrates with the existing scraper infrastructure

## Installation

Ensure you have the base scraper installed, then:

```bash
# Clone the repository if not already done
git clone https://github.com/yourusername/AI-webagent_extractor.git
cd AI-webagent_extractor

# Install required dependencies (if not already installed)
pip install selenium seleniumbase drissionpage requests beautifulsoup4 python-dotenv
```

## Usage

### Basic Usage

```python
from darwin_scraper_cloudflare import DarwinCloudflareBypass

# Initialize the enhanced scraper
scraper = DarwinCloudflareBypass(openai_api_key="your_api_key")

# Enable anti-Cloudflare mode
scraper.enable_anti_cloudflare()

# Extract product details (will use advanced methods)
product_data = scraper.extract_product_details("https://darwin.md/some-product-url")

# Process the product data
print(f"Product name: {product_data.get('name')}")
print(f"Price: {product_data.get('price')}")
```

### Testing Cloudflare Bypass

```python
# Test if bypass works for a specific URL
test_result = scraper.test_cloudflare_bypass("https://darwin.md/telefoane/smartphone")

if test_result["success"]:
    print(f"Bypass successful using {test_result['successful_method']} method!")
    print(f"Check screenshots in: {test_result['screenshots']}")
else:
    print("Bypass failed. Check logs for details.")
```

### Running the Example Script

We've provided an example script that demonstrates the different capabilities:

```bash
python src/cloudflare_bypass_example.py
```

This will run several tests comparing normal extraction vs. anti-Cloudflare methods.

## How It Works

The Cloudflare bypass implementation uses several techniques:

1. **Visible Browser**: Uses non-headless mode to appear legitimate to Cloudflare's checks
2. **WebDriver Masking**: Removes WebDriver flags that Cloudflare looks for
3. **Realistic Timing**: Implements human-like delays between actions
4. **Challenge Detection**: Identifies when a challenge appears and waits for it
5. **User Simulation**: Performs scrolling and other interactions that mimic human behavior
6. **Modern User Agents**: Uses up-to-date browser fingerprints

## Methods

### SeleniumBase Advanced Method

This approach uses SeleniumBase with:
- Unmodified Chrome (uc mode)
- WebDriver detection bypass
- Realistic scrolling behavior
- Automatic challenge detection
- Screenshot capture for debugging

### DrissionPage Advanced Method

This approach uses DrissionPage with:
- Non-headless browsing
- Cookie preservation
- Modern user agent strings
- Human-like scroll simulation
- Challenge detection and waiting

## When to Use

Use the Cloudflare bypass functionality when:

1. You encounter HTTP 403 errors with standard extraction methods
2. You see "Access Denied" or challenge pages in your screenshots
3. Normal extraction methods return empty or partial results
4. The site has recently increased its anti-bot protection

## Important Considerations

- **Performance**: Anti-Cloudflare methods are slower than standard extraction
- **Resource Usage**: Visible browsers require more memory and CPU
- **Ethical Use**: Only use on sites where you have permission to scrape
- **Screenshots**: Check the screenshots directory for debugging evidence

## Disabling the Feature

When not needed, you can disable the anti-Cloudflare functionality:

```python
scraper.disable_anti_cloudflare()
```

This will revert to using the standard extraction methods for better performance.

## Troubleshooting

If you encounter issues with the Cloudflare bypass:

1. Check the `cloudflare_scraper.log` file for detailed error messages
2. Review the screenshots in the `screenshots` directory
3. Try using a different browser backend (SeleniumBase vs DrissionPage)
4. Consider adding additional delays with `time.sleep()` if challenges persist
5. Verify that your Chrome/Chromium version is up-to-date

## License

Same as the parent project.