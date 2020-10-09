from django.shortcuts import render
from .forms import GeeksForm
from .models import GeeksModel
from PIL import Image
from PIL import ImageFilter
import pytesseract as tess
import re
import requests

# Create your views here.
def filter(image):
    blurred_jelly = image.filter(ImageFilter.SHARPEN)
    return blurred_jelly

def date_finder(text):
    date_re = r'\d\d\.\d\d\.\d\d'
    date = re.findall(date_re, text)
    return date

def total_finder(text):
    some_list = []
    total_re = r'\ИТОГ\s\W+\w+\.\w+'  # Ищем по слову ИТОГ
    total1_re = r'\итог\s\W+\w+\.\w+'  # Ищем по слову итог
    max_total = r'\d+\.'
    total = re.findall(total_re, text)
    total1 = re.findall(total1_re, text)
    itog = re.findall(max_total, text)
    if len(total) == 1:  # Условия для отбора
        return total
    elif len(total1) == 1:
        return total1
    if len(total) == 0 and len(total1) == 0 and len(itog) != 0:
        for i in itog:
            i = int(i[:-1])#Приводим в нужный тип, все цифры из списка
            some_list.append(i)#Закидываем их в новый список
        return max(some_list)

def bin_finder(text):
    Bin_re = r'\d{12}'
    Bin = re.findall(Bin_re, text)
    return Bin[0]
custom_config = r'--psm 6 --oem 3'


def index(request):
    context = {}
    if request.method == "POST":
        form = GeeksForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data.get("geeks_field")
            obj = GeeksModel.objects.create(
                img=img
            )
            obj.save()
            print(obj)
            fotka = obj.img
            img = Image.open(fotka)
            text = tess.image_to_string(filter(img), lang='rus+eng')
            response = requests.get(
                'https://api.smartplaza.kz/partners/api/brand/bin?bin=' + str(bin_finder(text)))
            data1 = response.json()
            for key in data1:
                if key == 'city':
                    data = {'text': date_finder(text), 'brand': (data1['brand']['brandId']), 'total': total_finder(text), 'Bin': bin_finder(text)}
                    return render(request, "result.html", context=data)
                else:
                    print('BIN not found')

    else:
        form = GeeksForm()
    context['form'] = form
    return render(request, "home.html", context)