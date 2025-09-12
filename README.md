# Darwin.md Product Scraper

A comprehensive Python-based web scraping and analysis solution specifically designed for Darwin.md. This project implements advanced scraping techniques, parallel processing, and detailed product analysis capabilities to extract, process, and analyze product data efficiently.

## 🌟 Key Features

### Data Extraction
- **Multi-Method Scraping**
  - BeautifulSoup4 for HTML parsing
  - Advanced selector patterns for reliable data extraction
  - Fallback mechanisms for different page structures
  
- **Comprehensive Product Details**
  - Full product specifications
  - Price history tracking
  - Image URLs and metadata
  - Category hierarchies
  - Brand and model information
  - Technical specifications
  - Availability status
  - Product variants

### Processing Capabilities
- **Parallel Processing**
  - Multi-threaded extraction using ThreadPoolExecutor
  - Configurable worker pool size
  - Batch processing with progress tracking
  - Automatic workload distribution

- **Smart Rate Limiting**
  - Adaptive request throttling
  - Server-friendly access patterns
  - Automatic retry mechanism
  - Connection pool management

### Data Analysis
- **Product Categorization**
  - Hierarchical category analysis
  - Brand/model pattern recognition
  - Product attribute extraction
  - Price range analysis
  - Competitive positioning

- **Data Validation**
  - Schema validation
  - Data consistency checks
  - Missing data detection
  - Format standardization
  - Error correction

### Export Functionality
- **Multiple Format Support**
  - Structured JSON output
  - CSV for data analysis
  - Batch-based file organization
  - Incremental updates
  
- **Data Organization**
  - Timestamp-based naming
  - Categorized storage
  - Backup management
  - Version tracking

## 📁 Project Structure

```
AI-webagent_extractor/
├── src/
│   ├── process_products.py           # Main orchestration script
│   ├── darwin_scraper_complete.py    # Core scraping engine
│   ├── darwin_sitemap_processor_v2.py# Sitemap handling
│   ├── darwin_product_analyzer.py    # Product analysis
│   └── utils/
│       ├── logger.py                 # Logging configuration
│       ├── validators.py             # Data validation
│       └── exporters.py             # Export utilities
├── data/
│   ├── raw/                         # Raw scraped data
│   │   └── products_batch_*.json    # JSON batches
│   ├── processed/                   # Processed data
│   │   └── products_batch_*.csv     # CSV exports
│   └── analytics/                   # Analysis results
├── logs/                           # Detailed log files
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   └── examples/                 # Usage examples
└── config/                      # Configuration files
```

## 🔧 Technical Requirements

### System Requirements
- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended)
- Stable internet connection
- Windows/Linux/macOS compatible

### Python Dependencies
```
beautifulsoup4>=4.9.3
requests>=2.26.0
pandas>=1.3.0
lxml>=4.6.3
aiohttp>=3.8.1
```

## 🚀 Installation

1. **Clone the Repository**
```bash
git clone https://github.com/Nasalciuc/AI-WebAgent-Extractor.git
cd AI-webagent_extractor
```

2. **Set Up Python Environment**
```bash
# Using Conda (recommended)
conda create -n py310 python=3.10
conda activate py310

# OR using venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure the Environment**
```bash
cp config/example.env .env
# Edit .env with your settings
```

## 💻 Usage

### Basic Usage
```bash
python src/process_products.py
```

### Advanced Configuration
```bash
python src/process_products.py --workers 8 --batch-size 200 --retry-count 3
```

### Parameters
- `--workers`: Number of parallel workers (default: 5)
- `--batch-size`: Products per batch (default: 100)
- `--retry-count`: Failed request retries (default: 3)
- `--output-dir`: Custom output directory
- `--log-level`: Logging detail level

## 📊 Data Output

### JSON Format
```json
{
  "url": "https://darwin.md/product/example",
  "title": "Product Name",
  "price": 999.99,
  "currency": "MDL",
  "brand": "Brand Name",
  "model": "Model X",
  "category": "Electronics",
  "subcategory": "Smartphones",
  "specs": {
    "color": "Black",
    "storage": "128GB",
    "ram": "8GB"
  },
  "images": ["url1", "url2"],
  "extracted_at": "2023-09-12T15:30:00"
}
```

### CSV Structure
- product_id
- title
- price
- currency
- brand
- model
- category
- subcategory
- specifications
- image_count
- extraction_date

## 🔍 Monitoring & Logging

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General operational events
- `WARNING`: Minor issues and recoverable errors
- `ERROR`: Serious issues requiring attention
- `CRITICAL`: System-critical issues

### Log File Structure
```
logs/
├── product_processing_YYYYMMDD_HHMMSS.log
├── error_YYYYMMDD_HHMMSS.log
└── performance_YYYYMMDD_HHMMSS.log
```

## 🛠 Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/
```

### Code Style
- Following PEP 8 guidelines
- Type hints for all functions
- Comprehensive docstrings
- Maximum line length: 100 characters

## 🔄 Development Roadmap

### Phase 1 (Current)
- [x] Basic scraping functionality
- [x] JSON/CSV export
- [x] Multi-threading support
- [x] Basic error handling

### Phase 2 (In Progress)
- [ ] Advanced URL pattern recognition
- [ ] Intelligent rate limiting
- [ ] Enhanced error handling
- [ ] Multiple sitemap support

### Phase 3 (Planned)
- [ ] AI-powered product categorization
- [ ] Real-time price monitoring
- [ ] API integration
- [ ] Dashboard for monitoring

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines
- Write tests for new features
- Follow existing code style
- Update documentation
- Add comments for complex logic
- Test thoroughly before PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

Project Maintainer - [@Nasalciuc](https://github.com/Nasalciuc)

Project Link: [https://github.com/Nasalciuc/AI-WebAgent-Extractor](https://github.com/Nasalciuc/AI-WebAgent-Extractor)

## 🙏 Acknowledgments

- BeautifulSoup4 team for the amazing parsing library
- Darwin.md for providing a well-structured website
- All contributors who have helped with the project