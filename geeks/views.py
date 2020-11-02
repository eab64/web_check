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
import numpy
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import exception_handler


# Create your views here.
def filter(image):
    blurred_jelly = image.filter(ImageFilter.SHARPEN)
    return blurred_jelly

def thresholder(img):
    ret1,th1 = cv2.threshold(img,150,255,cv2.THRESH_BINARY)
    return th1

def date_finder(text):#Проделываем тоже самое
    for i in text:
        date_re = r'[0-3]\d[.|:|-|/][0-1]\d[.|:|-|/]20'
        date = re.findall(date_re, i)
        if len(date) != 0:
            print(date)
            return date[0]
            # break

def summa_finder(text):
    total_re = r"(итог|ИТОГ|Итог|Итого|Итого:|ИТОГО|итого|.ТОГ|.Тог|ОГ|ог)(\W+\d{3,})"#Ищем по слову ИТОГ
    for i in reversed(text):
        total = re.findall(total_re, i)
        if len(total)!=0:
            XX = ([re.sub('\D+', '', total[0][1])])
            return int(XX[0])
            break

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

def adress_finder(text):
    for i in text:
        date_re = r'DOSTYK|dostyk|Dostyk|ДОСТЫК|достык|PLAZA|plaza|Жолдасбекова|САМАЛ|самал|Самал|Медеус|МЕДЕУС|Фараб|ФАРАБ|фараб|Аль|аль|АЛЬ'
        # date_re = r'MEGA'
        date = re.findall(date_re, i)
        if len(date) != 0:
            return True
            break
        else:
            return False

custom_config = r'--psm 6 --oem 3'

@csrf_exempt
def index(request):
    data = {}
    texts_list = []
    if request.method == "POST":#Если запрос POST
        form = GeeksForm(request.POST, request.FILES)
        if form.is_valid():
            print('ПРИНЯЛ ФОТКУ')
            img = form.cleaned_data.get("image")
            img_pillow = Image.open(img)
            img_opencv = cv2.cvtColor(numpy.asarray(img_pillow), cv2.COLOR_RGB2GRAY)
            texts_list.append(tess.image_to_string(filter(img_pillow), lang='rus+eng', config=custom_config))  # filt+psm
            texts_list.append(tess.image_to_string(img_pillow, lang='rus+eng'))  # default
            texts_list.append(tess.image_to_string(img_pillow, lang='rus+eng', config=custom_config))  # def+psm
            texts_list.append(tess.image_to_string(filter(img_pillow), lang='rus+eng'))  # filtered
            texts_list.append(tess.image_to_string(thresholder(img_opencv), lang='rus+eng', config=custom_config))  # threshold
            if adress_finder(texts_list) is True:#Если ТРЦ подходит по названию
                print('НАЗВАНИЕ ТРЦ ВИДИТ')
                if len(bin_finder(texts_list))!=0:#Если список БИНОВ не пустой
                    print('Список бинов не пустой')
                    for i in bin_finder(texts_list):
                        response = requests.get(
                            'https://api.smartplaza.kz/partners/api/brand/bin?bin=' + str(i))
                        data1 = response.json()#Либо есть данные либо нет(БИНа не существует)
                        for key in data1:
                            if key == 'city':#Бренд найден
                                print('БРЕНД НАЙДЕН')
                                data = {'date': date_finder(texts_list), 'brandId': int((data1['brand']['brandId'])),
                                        'sum': summa_finder(texts_list), 'Bin': int(i)}
                                return HttpResponse(json.dumps(data), content_type="application/json")
                    data = {'date': date_finder(texts_list), 'brandId': 'не найден',
                            'sum': summa_finder(texts_list), 'Bin': 'не найден'}
                    return HttpResponse(json.dumps(data), content_type="application/json")#Бренд не найден
                else:
                    print('СПИСОК БИНОВ ПУСТОЙ')
                    data = {'date': date_finder(texts_list), 'brandId': 'не найден',
                            'sum': summa_finder(texts_list), 'Bin': 'не найден'}
                    return HttpResponse(json.dumps(data), content_type="application/json")
            else:
                print('НАЗВАНИЕ ТРЦ НЕ ВИДИТ')
    else:
        return HttpResponse(json.dumps("Method not allowed."),
                            content_type="application/json")
    print('Вернул пустой список')
    return HttpResponse(json.dumps(data),
                        content_type="application/json")



# elif form.is_valid() and adress_finder(texts_list) is False:
#     return HttpResponse(json.dumps("Method not allowed."),
#                         content_type="application/json")
# else:
#     data = {'date': date_finder(texts_list), 'brandId': 'не найден', 'sum': summa_finder(texts_list), 'Bin': 'не найден'}
#     return HttpResponse(json.dumps(data), content_type="application/json")
# class CheckView(APIView):#Это должно быть в конце и после того как задаются все данные атрибутам выводит все обьекты
#     def get(self, request):
#         Checks = Check.objects.all()
#         return Response({"Checks": Checks})