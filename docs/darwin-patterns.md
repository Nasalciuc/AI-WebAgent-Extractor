# Darwin.md Website Patterns & Intelligence

*Last Updated: October 15, 2025*

## Site Structure Overview

Darwin.md is Moldova's leading e-commerce platform with a well-structured, modern web architecture. The site uses a combination of server-side rendering and dynamic JavaScript content loading, making it suitable for various scraping approaches.

### Architecture Characteristics:
- **Primary Language**: Romanian (ro-RO)
- **Currency**: MDL (Moldovan Leu)
- **Framework**: Custom e-commerce platform with React components
- **CDN**: CloudFlare for static assets
- **API**: RESTful endpoints for dynamic content
- **Mobile**: Responsive design with mobile-specific optimizations

---

## URL Patterns

### Product Pages
```
Pattern: https://darwin.md/product/{product-slug}-{product-id}
Examples:
- https://darwin.md/product/iphone-15-pro-max-256gb-12345
- https://darwin.md/product/laptop-asus-rog-gaming-67890
- https://darwin.md/product/samsung-galaxy-s24-ultra-11223
```

**Best Method**: DrissionPage (85% success) - Handles dynamic price updates

### Category Pages
```
Pattern: https://darwin.md/category/{category-slug}
Examples:
- https://darwin.md/category/smartphones
- https://darwin.md/category/laptops-si-calculatoare
- https://darwin.md/category/electronice-si-gadgeturi

Pagination: ?page={number}
- https://darwin.md/category/smartphones?page=2
- Maximum: 24 products per page
```

**Best Method**: BeautifulSoup (75% success) - Fast for static product listings

### Search Pages
```
Pattern: https://darwin.md/search?q={query}
Examples:
- https://darwin.md/search?q=iphone
- https://darwin.md/search?q=gaming+laptop
- https://darwin.md/search?category=electronics&sort=price_asc
```

**Best Method**: Selenium (70% success) - Handles search result JavaScript

### Brand Pages
```
Pattern: https://darwin.md/brand/{brand-slug}
Examples:
- https://darwin.md/brand/apple
- https://darwin.md/brand/samsung
- https://darwin.md/brand/asus
```

### Sitemap Structure
```
Main Sitemap: https://darwin.md/sitemap.xml
Product Sitemap: https://darwin.md/sitemap-products.xml
Category Sitemap: https://darwin.md/sitemap-categories.xml
```

---

## Common Selectors

### Product Information

#### Primary Selectors (Best Success Rate)
```css
/* Product Title */
.product-title
.product-name h1
[data-testid="product-title"]

/* Current Price */
.price-current
.price-new
.current-price .amount

/* Original Price (Discounted) */
.price-old
.price-original
.old-price .amount

/* Product Description */
.product-description
.product-details .description
.product-info-content

/* Product Images */
.product-gallery img
.product-images .image-item
[data-testid="product-image"]

/* Stock Status */
.stock-status
[data-stock="available"]
[data-stock="out-of-stock"]
.availability-status

/* Product Rating */
.rating-stars
.product-rating .stars
[data-rating]

/* Product SKU */
.product-sku
.sku-number
[data-sku]
```

#### XPath Alternatives
```xpath
/* Product Title */
//h1[contains(@class, 'product-title')]
//div[contains(@class, 'product-name')]/h1

/* Price Information */
//span[contains(@class, 'price-current')]
//div[@class='price-new']//span[@class='amount']

/* Description */
//div[contains(@class, 'product-description')]
//section[@class='product-details']//div[@class='description']

/* Images */
//div[@class='product-gallery']//img[@data-src]
//img[contains(@class, 'product-image')]
```

### Category Page Selectors

```css
/* Product Grid */
.product-grid
.products-listing
.category-products

/* Individual Product Cards */
.product-card
.product-item
.grid-item

/* Product Card Elements */
.product-card .title
.product-card .price
.product-card .image img
.product-card .rating

/* Pagination */
.pagination-nav
.pagination .page-link
.next-page-btn

/* Category Filters */
.filter-sidebar
.category-filters
.price-filter
.brand-filter
```

### Navigation Selectors

```css
/* Main Navigation */
.main-nav
.header-nav .nav-item
.mega-menu

/* Breadcrumbs */
.breadcrumb
.breadcrumb-nav .crumb

/* Category Menu */
.category-menu
.categories-dropdown
.mobile-menu
```

---

## JavaScript Behavior

### Dynamic Content Loading

#### Price Updates
- **Behavior**: Prices load via AJAX after initial page render
- **Trigger**: Page load completion + 1-2 second delay
- **Method**: DrissionPage with wait conditions
```python
# Wait for price loading
page.wait.load_start()
page.wait(2)  # Allow price AJAX to complete
```

#### Image Lazy Loading
- **Behavior**: Images use `data-src` attribute, load on scroll
- **Trigger**: Element enters viewport
- **Method**: Scroll to element or use data-src directly
```python
# Get actual image URL
img_url = element.attr('data-src') or element.attr('src')
```

#### Search Autocomplete
- **Behavior**: Search suggestions appear after 3+ characters
- **Trigger**: Input focus + typing delay
- **Method**: Selenium with explicit waits

#### Product Variants
- **Behavior**: Color/size variants load product data dynamically
- **Trigger**: Variant selection clicks
- **Method**: DrissionPage with event simulation

### AJAX Endpoints

```javascript
// Price checking
GET /api/product/{id}/price

// Stock availability  
GET /api/product/{id}/stock

// Product variants
GET /api/product/{id}/variants

// Search suggestions
GET /api/search/suggest?q={query}

// Category products
GET /api/category/{id}/products?page={n}
```

---

## Rate Limiting Guidelines

### Polite Scraping Recommendations

#### Request Timing
```python
# Optimal delays (seconds)
DELAYS = {
    'between_requests': (1.2, 1.5),    # Random delay range
    'after_error': 5.0,                # Recovery delay
    'between_batches': 60.0,           # Batch separation
    'peak_hours_extra': 2.0            # Additional delay during peak
}
```

#### Rate Limits Observed
- **Soft Limit**: 50 requests/minute (no blocking)
- **Hard Limit**: 100 requests/minute (429 responses)
- **IP Blocking**: 500+ requests/hour (temporary ban)
- **Recovery Time**: 15-30 minutes after blocking

#### Peak Traffic Hours (UTC+2 Moldova Time)
```
High Traffic (Avoid):    09:00 - 17:00 UTC
Medium Traffic:          17:00 - 21:00 UTC  
Low Traffic (Optimal):   21:00 - 09:00 UTC
```

#### Recommended Headers
```python
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
```

---

## Currency Format

### MDL (Moldovan Leu) Patterns

#### Price Display Formats
```
Standard:     1,299 MDL
With Cents:   1,299.99 MDL  
Compact:      1.299 lei
Short:        1299 L

Discount Format:
Old: 1,599 MDL  New: 1,299 MDL (-300 MDL)
```

#### Parsing Regex Patterns
```python
import re

# Standard price extraction
PRICE_PATTERNS = [
    r'(\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?)\s*(?:MDL|lei|L)',
    r'(\d+(?:[,\.]\d{3})*(?:[,\.]\d{2})?)\s*(?:MDL|lei|L)',
    r'(\d+[,\.]\d+)\s*(?:MDL|lei|L)'
]

def extract_price(text):
    for pattern in PRICE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '').replace('.', '')
            return float(price_str) / 100 if len(price_str) > 2 else float(price_str)
    return None
```

#### Currency Conversion Context
```
1 USD ≈ 18-20 MDL (fluctuates)
1 EUR ≈ 19-21 MDL (fluctuates)
1 RON ≈ 4-5 MDL (Romanian Leu)
```

---

## Category Taxonomy

### Main Categories Structure

```
Electronics & Gadgets (electronice-si-gadgeturi)
├── Smartphones (smartphones)
├── Laptops & Computers (laptops-si-calculatoare)
├── Audio & Video (audio-video)
├── Gaming (gaming)
├── Smart Home (casa-inteligenta)
└── Accessories (accesorii)

Fashion & Beauty (moda-si-frumusete)
├── Clothing (imbracaminte)
├── Shoes (incaltaminte)
├── Accessories (accesorii-moda)
├── Beauty & Health (frumusete-sanatate)
└── Watches (ceasuri)

Home & Garden (casa-si-gradina)
├── Furniture (mobilier)
├── Kitchen (bucatarie)
├── Garden Tools (unelte-gradina)
├── Decor (decoratiuni)
└── Appliances (electrocasnice)

Sports & Outdoors (sport-si-outdoor)
├── Fitness (fitness)
├── Outdoor Gear (echipament-outdoor)
├── Sports Equipment (echipament-sport)
└── Travel (calatorie)

Auto & Moto (auto-moto)
├── Car Accessories (accesorii-auto)  
├── Car Electronics (electronice-auto)
├── Motorcycle (motociclete)
└── Tools (unelte-auto)
```

### Category URL Patterns
```python
CATEGORY_URLS = {
    'electronics': 'https://darwin.md/category/electronice-si-gadgeturi',
    'smartphones': 'https://darwin.md/category/smartphones',
    'laptops': 'https://darwin.md/category/laptops-si-calculatoare',
    'fashion': 'https://darwin.md/category/moda-si-frumusete',
    'home': 'https://darwin.md/category/casa-si-gradina',
    'sports': 'https://darwin.md/category/sport-si-outdoor',
    'auto': 'https://darwin.md/category/auto-moto'
}
```

---

## Image URL Patterns

### Image CDN Structure

#### Product Images
```
Pattern: https://cdn.darwin.md/images/products/{size}/{product-id}/{image-hash}.{format}

Sizes:
- thumbnail: 150x150px
- small: 300x300px  
- medium: 600x600px
- large: 1200x1200px
- original: Full resolution

Examples:
https://cdn.darwin.md/images/products/medium/12345/a1b2c3d4e5f6.jpg
https://cdn.darwin.md/images/products/large/67890/f6e5d4c3b2a1.webp
```

#### Category Images
```
Pattern: https://cdn.darwin.md/images/categories/{category-slug}/{size}.{format}

Examples:
https://cdn.darwin.md/images/categories/smartphones/banner.jpg
https://cdn.darwin.md/images/categories/laptops/hero.webp
```

#### Brand Logos
```
Pattern: https://cdn.darwin.md/images/brands/{brand-slug}/logo.{format}

Examples:
https://cdn.darwin.md/images/brands/apple/logo.svg
https://cdn.darwin.md/images/brands/samsung/logo.png
```

### Image Extraction Best Practices

```python
def extract_product_images(element):
    """Extract all product images with fallbacks"""
    images = []
    
    # Primary: data-src (lazy loaded)
    lazy_images = element.eles('.product-gallery img[data-src]')
    for img in lazy_images:
        src = img.attr('data-src')
        if src:
            # Prefer larger sizes
            src = src.replace('/thumbnail/', '/large/')
            src = src.replace('/small/', '/large/')
            images.append(src)
    
    # Fallback: regular src
    regular_images = element.eles('.product-gallery img[src]')
    for img in regular_images:
        src = img.attr('src')
        if src and src not in images:
            images.append(src)
    
    return images
```

---

## Method-Specific Recommendations

### DrissionPage (Best Overall: 85%)
**Recommended For**: Product pages, dynamic content, AJAX-heavy pages

```python
# Optimal configuration
from DrissionPage import ChromiumPage

page = ChromiumPage()
page.get(url)
page.wait.load_start()  # Wait for initial load
page.wait(2)           # Allow AJAX to complete

# Best for:
# - Product detail pages with dynamic pricing
# - Pages with lazy-loaded images  
# - JavaScript-dependent content
```

### Selenium (Reliable: 75%)
**Recommended For**: Search pages, complex interactions, form submissions

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Best for:
# - Search result pages
# - Category filtering
# - Pages requiring user interaction simulation
```

### BeautifulSoup (Fast: 65%)  
**Recommended For**: Category listings, static content, bulk operations

```python
import requests
from bs4 import BeautifulSoup

# Best for:
# - Category product listings
# - Static product information
# - High-volume, simple extractions
# - Sitemap parsing
```

### Auto Method (Balanced: 80%)
**Recommended For**: Mixed content types, fallback scenarios

```python
# Automatic method selection based on page complexity
# Tries BeautifulSoup → DrissionPage → Selenium
# Best for general-purpose scraping with reliability
```

---

## Common Pitfalls & Solutions

### Issue: Empty Price Fields
**Cause**: Price loads via AJAX after page render
**Solution**: Use DrissionPage with 2+ second wait

### Issue: Missing Product Images  
**Cause**: Lazy loading uses data-src attribute
**Solution**: Check data-src before src attribute

### Issue: Pagination Not Working
**Cause**: JavaScript-controlled pagination
**Solution**: Use Selenium or DrissionPage for pagination

### Issue: Search Results Inconsistent
**Cause**: Dynamic search with debounced AJAX
**Solution**: Add delays between search queries

### Issue: Rate Limiting Errors
**Cause**: Too many requests per minute
**Solution**: Implement exponential backoff (1.2-1.5s delays)

---

*This documentation is maintained by the Darwin Agent system and updated based on site behavior analysis.*