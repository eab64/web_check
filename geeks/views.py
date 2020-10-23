from django.shortcuts import render
from django.http import HttpResponse
from .forms import GeeksForm
from .models import GeeksModel

from PIL import Image
from PIL import ImageFilter
import pytesseract as tess
import re
import requests
import cv2
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import exception_handler


# Create your views here.
def filter(image):
    blurred_jelly = image.filter(ImageFilter.SHARPEN)
    return blurred_jelly

def thrash(img):
    ret1,th1 = cv2.threshold(img,150,255,cv2.THRESH_BINARY)
    return th1

def date_finder(text):#Проделываем тоже самое
    for i in text:
        date_re = r'\d\d\.\d\d\.\d\d'
        date = re.findall(date_re, i)
        if len(date) != 0:
            print(date)
            return date

def summa_finder(text):
    total_re = r'\ИТОГ\W\W+\d+'#Ищем по слову ИТОГ
    total1_re = r'\итог\W\W+\d+'
    totals_list = []
    for i in reversed(text):
        total = re.findall(total_re, i)
        totals_list.append(total)
    for i in reversed(text):
        total1 = re.findall(total1_re, i)
        totals_list.append(total1)
    for i in totals_list:
        if len(i)!=0:
            print(i)
            return i

def bin_finder(text):#Проделываем тоже самое
    BINs_list = []
    for i in text:
        # print(i)
        Bin_re = r'\d{12}'
        Bin = re.findall(Bin_re, i)
        for i in Bin:
            BINs_list.append(i)
    print(list(set(BINs_list)))
    return list(set(BINs_list))#Убрал new_binslist == list(set(BINs_list))


custom_config = r'--psm 6 --oem 3'

@csrf_exempt
def index(request):
    context = {}
    data = {}
    texts_list = []
    if request.method == "POST":
        form = GeeksForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data.get("image")
            obj = GeeksModel.objects.create(
                img=img
            )
            obj.save()
            print(obj)
            # imgc = cv2.imdecode(obj.img, flag=1)

            imgf = Image.open(obj.img)
            texts_list.append(tess.image_to_string(filter(imgf), lang='rus+eng', config=custom_config))  # filt+psm
            texts_list.append(tess.image_to_string(imgf, lang='rus+eng'))  # default
            texts_list.append(tess.image_to_string(imgf, lang='rus+eng', config=custom_config))  # def+psm
            texts_list.append(tess.image_to_string(filter(imgf), lang='rus+eng'))  # filtered
            # texts_list.append(tess.image_to_string(thrash(imgc), lang='eng+rus', config=custom_config))  # threshold
            obj.data = date_finder(texts_list)
            for i in bin_finder(texts_list):
                #Цикл для проверки всех БИНов
                print("FIRSt")
                response = requests.get(
                    'https://api.smartplaza.kz/partners/api/brand/bin?bin=' + str(i))
                data1 = response.json()
                print("Data1 " + str(data1))
                for key in data1:
                    if key == 'city':
                        data = {'date': date_finder(texts_list), 'brandId': (data1['brand']['brandId']), 'sum': summa_finder(texts_list), 'Bin': i}
                        print("Data " + str(data))
                        print(type(obj.img))
                        return HttpResponse(json.dumps(data), content_type="application/json")
                    else:
                        print('BIN not found')

    else:
        return HttpResponse(json.dumps("Method not allowed."),
                            content_type="application/json")
    return HttpResponse(json.dumps(data),
                        content_type="application/json")


# class CheckView(APIView):#Это должно быть в конце и после того как задаются все данные атрибутам выводит все обьекты
#     def get(self, request):
#         Checks = Check.objects.all()
#         return Response({"Checks": Checks})


# def bin_finder(text):
#     Bin_re = r'\d{12}'
#     Bin = re.findall(Bin_re, text)
#     return Bin

# def total_finder(text):
#     some_list = []
#     total_re = r'\ИТОГ\s\W+\w+\.\w+'  # Ищем по слову ИТОГ
#     total1_re = r'\итог\s\W+\w+\.\w+'  # Ищем по слову итог
#     max_total = r'\d+\.'
#     total = re.findall(total_re, text)
#     total1 = re.findall(total1_re, text)
#     itog = re.findall(max_total, text)
#     if len(total) == 1:  # Условия для отбора
#         return total
#     elif len(total1) == 1:
#         return total1
#     if len(total) == 0 and len(total1) == 0 and len(itog) != 0:
#         for i in itog:
#             i = int(i[:-1])#Приводим в нужный тип, все цифры из списка
#             some_list.append(i)#Закидываем их в новый список
#         return max(some_list)

# def date_finder(text):
#     date_re = r'\d\d\.\d\d\.\d\d'
#     date = re.findall(date_re, text)
#     return date