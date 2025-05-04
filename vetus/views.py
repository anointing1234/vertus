from django.shortcuts import render
import requests
import logging
import json
import os
import time
from urllib.parse import urljoin
from requests.exceptions import RequestException
from django.contrib.auth import logout
from bs4 import BeautifulSoup
import random
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404,redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django_countries.fields import Country
from django_countries import countries
from datetime import date
from accounts.models import Room
from PIL import Image
from io import BytesIO
import base64
from django.core.files.uploadedfile import InMemoryUploadedFile


def home_view(request):
    return render(request,'home/index.html')

def about_view(request):
    return render(request,'home/about.html')


def faq_view(request):
    return render(request,'home/faq.html')


def pricing_view(request):
    return render(request,'home/pricing.html')


def room_detail_view(request, id):
    # Your main room
    room = get_object_or_404(Room, id=id)
    room_facilities = room.facilities.all()

    # Process the main room’s image to Base64 as before
    image_data = None
    if room.image:
        room.image.open()
        img = Image.open(room.image).convert('RGB')
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS
        img = img.resize((570, 320), resample=resample)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=95)
        buf.seek(0)
        image_data = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

    # Fetch three other rooms (random order; exclude the current one)
    other_rooms = Room.objects.exclude(id=room.id).order_by('?')[:3]

    return render(request, 'home/room_details.html', {
        'room': room,
        'image_data': image_data,
        'room_facilities': room_facilities,
        'other_rooms': other_rooms,
    })

def rooms_view(request):
    return render(request,'home/rooms.html')


def services_view(request):
    rooms = Room.objects.all()
    return render(request,'home/services.html',{'rooms': rooms})


def contact_view(request):
    return render(request,'home/contact.html')

def page_pricing(request):
    return render(request,'home/page-pricing.html')


   
