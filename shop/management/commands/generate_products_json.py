from django.core.management.base import BaseCommand
from shop.models import ProductShop, CategoryShop
from django.conf import settings
import json
import os
from datetime import datetime
import uuid

class Command(BaseCommand):
    help = 'Generates products.json file from database products'

    def handle(self, *args, **options):
        # Get all products from database
        products = ProductShop.objects.all().prefetch_related('images')

        # Get all categories
        categories = CategoryShop.objects.all()

        # Prepare data structure
        products_data = []
        categories_data = []

        # Convert categories to JSON format
        for category in categories:
            categories_data.append({
                "id": str(category.id),
                "title": category.title,
                "categoryId": None,
                "created": int(datetime.now().timestamp() * 1000),
                "updated": int(datetime.now().timestamp() * 1000),
                "translations": {
                    "en": {
                        "title": category.title
                    }
                }
            })

        # Convert products to JSON format
        for product in products:
            # Get product images
            images = []
            if product.images.exists():
                for img in product.images.all():
                    images.append({
                        "url": img.image.url
                    })
            else:
                # Add default image if none exists
                images.append({
                    "url": "/images/person-using-smartphone-his-auto.jpg"
                })

            # Create product data
            product_data = {
                "id": str(product.id),
                "name": product.title.lower().replace(' ', '-'),
                "title": product.title,
                "description": product.description or "Sample text. Lorem ipsum dolor sit amet, consectetur adipiscing elit nullam nunc justo sagittis suscipit.",
                "fullDescription": product.description or "Пример текста. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut Labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrum exercitation ullamco Laboris ni si ut aliquip ex ea commodo consequat.",
                "price": str(product.sell_price()),
                "oldPrice": str(product.price) if product.discount > 0 else str(product.sell_price()),
                "quantity": product.quantity,
                "currency": "USD",
                "sku": "",
                "outOfStock": product.quantity <= 0,
                "isFeatured": product.is_bestseller,
                "saleEnabled": product.discount > 0,
                "saleStart": "",
                "saleEnd": "",
                "categories": [str(product.category.id)],
                "variations": [],
                "variationValues": {},
                "images": images,
                "created": int(datetime.now().timestamp() * 1000),
                "updated": int(datetime.now().timestamp() * 1000),
                "isDefault": True,
                "translations": {
                    "ru": {
                        "name": product.title.lower().replace(' ', '-'),
                        "title": product.title,
                        "description": product.description or "Sample text. Lorem ipsum dolor sit amet, consectetur adipiscing elit nullam nunc justo sagittis suscipit.",
                        "fullDescription": product.description or "Пример текста. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut Labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrum exercitation ullamco Laboris ni si ut aliquip ex ea commodo consequat."
                    }
                }
            }
            products_data.append(product_data)

        # Add variations (color and size)
        variations = [
            {
                "id": "1",
                "title": "Color",
                "items": [
                    {"title": "Red", "value": "#ff0000"},
                    {"title": "Green", "value": "#00ff00"},
                    {"title": "Blue", "value": "#0000ff"}
                ],
                "created": int(datetime.now().timestamp() * 1000),
                "updated": int(datetime.now().timestamp() * 1000),
                "translations": {
                    "en": {
                        "title": "Color"
                    }
                }
            },
            {
                "id": "2",
                "title": "Size",
                "items": [
                    {"title": "Small", "value": "S"},
                    {"title": "Medium", "value": "M"},
                    {"title": "Large", "value": "L"}
                ],
                "created": int(datetime.now().timestamp() * 1000),
                "updated": int(datetime.now().timestamp() * 1000),
                "translations": {
                    "en": {
                        "title": "Size"
                    }
                }
            }
        ]

        # Create final JSON structure
        json_data = {
            "products": products_data,
            "categories": categories_data,
            "variations": variations
        }

        # Write to file
        json_file_path = os.path.join(settings.BASE_DIR, 'static', 'products.json')

        try:
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            self.stdout.write(self.style.SUCCESS(f'Successfully generated products.json with {len(products_data)} products'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating products.json: {str(e)}'))
