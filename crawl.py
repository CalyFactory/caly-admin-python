
from bs4 import BeautifulSoup
# requests는 페이지를 요청한 응답을 받을때 사용합니다.
import requests
import urllib

from urllib.request import FancyURLopener

import requests


BASE_URL = "https://www.mangoplate.com"
# SEARCH_URL = "/search/" + region

headers = {
 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)     Chrome/37.0.2049.0 Safari/537.36'
}

def getDetailInfo(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')


    # mapUrl = soup.find("img",attrs={"class":"naver_static_map"}).get('src')

    detail_info = soup.find("section",attrs={"class":"restaurant-detail"})
    dic_result = {}

    dic_result['name'] = detail_info.find("h1",attrs={"class":"restaurant_name"}).text
    
    
    address = detail_info.find("span",attrs={"itemprop":"addressLocality"}).text
    #codeReview
    #trim을 써라 앞뒤 공백을 제거해준다.
    address = address[address.index('서'):]
    dic_result['address'] = address[:address.index('\n')]    
    dic_result['priceRange'] = detail_info.find("td",attrs={"itemprop":"priceRange"}).text
    # dic_result['mapUrl'] = mapUrl
    
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