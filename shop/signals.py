from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from shop.models import ProductShop, ProductImage
from django.conf import settings
import json
import os
from datetime import datetime
from django.core.management import call_command

@receiver(post_save, sender=ProductShop)
def update_products_json_on_save(sender, instance, **kwargs):
    """
    Signal receiver to update products.json when a product is saved
    """
    try:
        call_command('generate_products_json')
    except Exception as e:
        print(f"Error updating products.json: {str(e)}")

@receiver(post_delete, sender=ProductShop)
def update_products_json_on_delete(sender, instance, **kwargs):
    """
    Signal receiver to update products.json when a product is deleted
    """
    try:
        call_command('generate_products_json')
    except Exception as e:
        print(f"Error updating products.json: {str(e)}")

@receiver(pre_delete, sender=ProductShop)
def delete_product_images_on_delete(sender, instance, **kwargs):
    """
    Signal receiver to delete product images from disk when a product is deleted
    """
    from django.core.files.storage import default_storage

    # Get all images related to the product (before they are deleted by CASCADE)
    images = instance.images.all()

    for image in images:
        try:
            # Delete the image file from storage
            if image.image:
                if default_storage.exists(image.image.path):
                    default_storage.delete(image.image.path)
                    print(f"Deleted image file: {image.image.path}")
                else:
                    print(f"Image file not found: {image.image.path}")
        except Exception as e:
            print(f"Error deleting image file {image.image.path}: {str(e)}")

@receiver(post_save, sender=ProductImage)
def update_products_json_on_image_save(sender, instance, **kwargs):
    """
    Signal receiver to update products.json when a product image is saved
    """
    try:
        call_command('generate_products_json')
    except Exception as e:
        print(f"Error updating products.json: {str(e)}")

@receiver(post_delete, sender=ProductImage)
def update_products_json_on_image_delete(sender, instance, **kwargs):
    """
    Signal receiver to update products.json when a product image is deleted
    """
    try:
        call_command('generate_products_json')
    except Exception as e:
        print(f"Error updating products.json: {str(e)}")
