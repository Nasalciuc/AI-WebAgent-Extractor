import json
import csv
import glob
import os
from datetime import datetime

def convert_json_to_csv():
    # Get all JSON files from data directory that match the batch pattern
    json_files = glob.glob("data/products_batch_*_*.json")
    
    # List to store all products
    all_products = []
    
    # Read all JSON files
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
            all_products.extend(products)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/all_products_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        'id', 'name', 'description', 'price', 
        'category', 'url', 'image_url', 'brand',
        'in_stock', 'extraction_method', 'last_updated'
    ]
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for product in all_products:
            # Ensure all required fields exist
            row = {
                'id': product.get('id', ''),
                'name': product.get('name', ''),
                'description': product.get('description', ''),
                'price': product.get('price', ''),
                'category': product.get('category', ''),
                'url': product.get('url', ''),
                'image_url': product.get('image_url', ''),
                'brand': product.get('brand', ''),
                'in_stock': product.get('in_stock', ''),
                'extraction_method': product.get('extraction_method', ''),
                'last_updated': product.get('last_updated', '')
            }
            writer.writerow(row)
    
    print(f"Converted {len(all_products)} products to CSV: {output_file}")
    return output_file

if __name__ == "__main__":
    convert_json_to_csv()