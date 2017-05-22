
from bs4 import BeautifulSoup
# requests는 페이지를 요청한 응답을 받을때 사용합니다.
import requests
import urllib

from urllib.request import FancyURLopener

import requests
import re

OPMAPER_SIZE = 10
COMMA_SIZE = 3


BASE_URL = "https://www.mangoplate.com"
# SEARCH_URL = "/search/" + region

headers = {
 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)     Chrome/37.0.2049.0 Safari/537.36'
}


def getLatLanFromMapUrl(map_url):
    r = requests.get(map_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')


    if map_url.find("openapi.naver.com") == -1 :
        try:
            ogImage = soup.find("meta",  property="og:image")
            # url = soup.find("meta",  property="og:url")

            print(ogImage["content"] if ogImage else "No meta title given")

            op_maperPos = ogImage["content"].find("og_map¢er")+ OPMAPER_SIZE
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
    # dic_result['priceRange'] = detail_info.find("td",attrs={"itemprop":"priceRange"}).text
    dic_result['priceRange'] = price_range
    # dic_result['mapUrl'] = mapUrl
    # http://map.naver.com/?isDetailAddress=true&isNewAddress=false&query="+Base64.encode(obj.address)+"&rcode=09410112&tab=1&type=ADDRESS&dlevel=12&enc=b64
    
    print(dic_result)    
    return dic_result

# getDetailInfo('dd')



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