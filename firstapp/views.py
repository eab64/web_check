from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound
from .models import Person, Check
import json
from django.http import HttpResponse
import requests
import re
from PIL import Image
from PIL import ImageFilter
import pytesseract as tess



# Принимает БИН и дает бренд_айди
def index(bin):
    # request = request
    bin2 = bin.GET['bin']
    print("BIIIN " + bin2)
    response = requests.get(
        'https://api.smartplaza.kz/partners/api/brand/bin?bin=' + bin2)
    data = response.json()
    brandId = data['brand']['brandId']
    print("BrandId " + str(brandId))
    print("Response zhe "  + str(response))
    return HttpResponse(json.dumps(brandId),
                        content_type="application/json")



def recognize(request):#Должен принимать фотку и возвращать BIN
    pass



