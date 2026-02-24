from django.db.models.signals import post_save, post_delete
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
