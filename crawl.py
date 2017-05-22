
from bs4 import BeautifulSoup
# requests는 페이지를 요청한 응답을 받을때 사용합니다.
import requests
import urllib
from bs4 import BeautifulSoup

from urllib.request import FancyURLopener
import math
import requests
import re
import db_manager
import util

import db_manager
import base64
from selenium import webdriver
from math import sin, cos, sqrt, atan2, radians 
import json


OPMAPER_SIZE = 10
COMMA_SIZE = 3


BASE_URL = "https://www.mangoplate.com"
# SEARCH_URL = "/search/" + region

headers = {
 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)     Chrome/37.0.2049.0 Safari/537.36'
}


def getLatLanFromMapUrl(map_url):
    
    

    # # browser = webdriver.PhantomJS()    
    # browser = webdriver.PhantomJS()

    # browser.get(map_url)
    # html = browser.page_source
    
    
    try:
        result_dic = {}
        r = requests.get(map_url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')        

        if "https://www.google.co.kr/maps" in map_url:

            
            
            
            op_image = soup.find("meta",  property="og:image")
            print(op_image)

            op_maperPos = op_image["content"].find("center=")+ 7
            commaPos = op_image["content"].find("%2C")
            levelPos = op_image["content"].find("&zoom=")
            
            if commaPos != -1 :                     
                lat = op_image["content"][op_maperPos:commaPos]
                lng = op_image["content"][commaPos+COMMA_SIZE:levelPos]
                print('long=>' + lng[:11] + 'lat =>' + lat[:10]) 
                result_dic['lat'] = lat[:10]
                result_dic['lng'] = lng[:11]
                return result_dic
            else:
                print('none default type')
                return result_dic   

        if "naver" in map_url:
            print(soup)                    
            strSoup = str(soup)
            print(strSoup[:31])

            if strSoup[:31] == "<script>window.location.replace":
                print("run")
                startIndex = strSoup.find("replace(") + 9                                
                endIndex = strSoup.find(");</script>") - 1
                redirectUrl = strSoup[startIndex:endIndex]

                r = requests.get(redirectUrl, headers=headers)
                soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')      


            ogImage = soup.find("meta",  property="og:image")

            # print(ogImage["content"] if ogImage else "No meta title given")

            op_maperPos = ogImage["content"].find("og_map¢er=") + 10
            commaPos = ogImage["content"].find("%2C")
            levelPos = ogImage["content"].find("&level")

            result_dic = {}

            #url에서 올바르게 파싱을 하였다면?
            if commaPos != -1 :                     
                lng = ogImage["content"][op_maperPos:commaPos]
                lat = ogImage["content"][commaPos+COMMA_SIZE:levelPos]
                print('long=>' + lng+ 'lat =>' + lat) 
                result_dic['lng'] = lng
                result_dic['lat'] = lat
                return result_dic

            else :
                print('none default type')
                return result_dic

    except Exception as e:
        return result_dic
        print(str(e))


def getInstaId(source_url):

    

    if not re.match(r'^[a-zA-Z]+://', source_url):
        print("not url")            

    r = requests.get(source_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
    
    try:
        meta_des = soup.findAll("meta", {"name":"description"})
        #링크가 존재하는한 메타데이터가 있어야하는데. 없을경우는 완전히 페이지가 삭제된경우이다.
        if(len(meta_des)==0):
            return "removed"
               

        text_description = meta_des[0].get('content')        
        start_id_pos = text_description.find("@")
        end_id_pos = text_description.find("on Instagram:")

        print("text middle = >"+text_description[start_id_pos:end_id_pos])
        #) 괄호 닫히는게없다면
        if(text_description[start_id_pos:end_id_pos].find(")")==-1):
            end_id_pos = end_id_pos + 1        

        source_user_id = text_description[start_id_pos+1:end_id_pos-2]

        return source_user_id

        
    except Exception as e:
        return 'err'
        
def getDetailInfo(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')


    # mapUrl = soup.find("img",attrs={"class":"naver_static_map"}).get('src')

    detail_info = soup.find("section",attrs={"class":"restaurant-detail"})
    dic_result = {}

    dic_result['name'] = detail_info.find("h1",attrs={"class":"restaurant_name"}).text
    # print(detail_info)
    # print(detail_info.find("span",attrs={"class":"orange-underline"}).text)
    # print(detail_info.find("table",attrs={"class":"info no_menu "}))
    
    table_body = detail_info.find("table",attrs={"class":"info no_menu "})
    if table_body == None:
        table_body = detail_info.find("table",attrs={"class":"info "})
    
    # 
    


    rows = table_body.find_all('tr')
    for row in rows:
        # print('row+>'+str(row))
        print(row.find('th').text)
        if row.find('th').text == "가격대:":
            price_range = row.find('td').text

    # <table class="info no_menu ">
    # address = detail_info.find("span",attrs={"itemprop":"addressLocality"}).text
    address = detail_info.find("span",attrs={"class":"orange-underline"}).text
    #codeReview
    #trim을 써라 앞뒤 공백을 제거해준다.
    address = address[address.index('서'):]
    dic_result['address'] = address[:address.index('\n')]    
    
    dic_result['priceRange'] = price_range
    print(dic_result['address'])
    # b64_address = base64.b64encode(bytes(dic_result['address'],'utf-8'))
    # mapurl로 부터 lat/lng을 가져오고. 몇분 걸리는지도 가져온다.
    # dic_pos  = getLatLanFromMapUrl("http://map.naver.com/?isDetailAddress=true&isNewAddress=false&query="+b64_address.decode("utf-8") +"&rcode=09410112&tab=1&type=ADDRESS&dlevel=12&enc=b64")
    dic_pos  = getLatLanFromMapUrl("https://www.google.co.kr/maps/place/"+str(dic_result['address']))
    print(dic_pos)
    try:
        dic_result['predictionWalkingTime'] = getWalkTime(dic_pos)
    except Exception as e:
        dic_result['predictionWalkingTime'] = '미안 찾을수 없었따.'
        print(str(e))

    print(dic_result)    
    return dic_result

def getWalkTime(dic_pos):
    
    subways = util.fetch_all_json(
        db_manager.query(
          "SELECT *FROM SUBWAY_INFO WHERE address LIKE '서울특별%'"
          )
    ) 

    stand_x = float(dic_pos['lat'])
    stand_y = float(dic_pos['lng'])


    minimum_dis = 100000000;
    minimum_subway_index = 0;

    for idx, subway in enumerate(subways):
        subway_x = float(subway["x_point_wgs"])
        subway_y = float(subway["y_point_wgs"])

        dx = subway_x - stand_x
        dy = subway_y - stand_y        
        distance = math.sqrt(float(dx*dx)+float(dy*dy))
        
        if minimum_dis > distance:
            minimum_dis = distance
            minimum_subway_index = idx  

    
        if minimum_dis > distance:
            minimum_dis = distance
            minimum_subway_index = idx   

    
    subway_x = subways[minimum_subway_index]["x_point_wgs"]
    subway_y = subways[minimum_subway_index]["y_point_wgs"]

    print("place:")
    print(dic_pos['lng'])
    print(dic_pos['lat'])
    print("subway:")
    print(subways[minimum_subway_index])    

    headers = {
     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
    }

    r = requests.get("http://map.naver.com/findroute2/findWalkRoute.nhn?call=route2&output=json&coord_type=naver&search=0&start="+dic_pos['lng']+"%2C"+dic_pos['lat']+"&destination="+subway_y+"%2C"+subway_x, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
    station_title = subways[minimum_subway_index]["station_name"]
    walking_time = json.loads(str(soup))["result"]["summary"]["totalTime"]

    return station_title + "역에서 걸어서 "+ str(walking_time) +"분"






def getBestPointList(region):
    r = requests.get(BASE_URL +"/search/" +region, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
    # print(soup)

    
    # result = soup.find("p",attrs={"class":"mango_text search_result_empty_message_content_sub_title"}).text    
    arr_result = []
    try:
        lists = soup.find_all('li')
        print("원본")
        print("============================")
        # print(str(lists[0]))
        
        
        for index,restaurant in enumerate(lists):

            #10개만 보여주면됨 ㅎ
            if index < 10:

                dic_result = {}
                img_url = restaurant.find("img",attrs={"class":"center-croping"}).get('src')
                title = restaurant.find("h2",attrs={"class":"title"}).text
                etc = restaurant.find("p",attrs={"class":"etc"}).text
                point = restaurant.find("strong",attrs={"class":"point search_point"}).text
                view_count = restaurant.find("span",attrs={"class":"view_count"}).text
                review_count = restaurant.find("span",attrs={"class":"review_count"}).text
                link = lists[index].find("div",attrs={"class":"info"}).find("a").get('href')

                dic_result['img_url'] = img_url
                dic_result['title'] = title
                dic_result['etc'] = etc
                dic_result['point'] = point
                dic_result['view_count'] = view_count
                dic_result['review_count'] = review_count
                dic_result['link'] = link
                arr_result.append(dic_result)
                print(img_url)
                print(title)
                print(etc)
                print(point)
                print(view_count)
                print(review_count)
                print(link)
                print("============================")
        return arr_result
    except Exception as e:
        return arr_result