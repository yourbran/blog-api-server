from time import sleep
from configparser import ConfigParser
from common import myLogger
import urllib.request
import urllib.parse
import json
import gzip


### PROP 세팅 START
properties = ConfigParser()
properties.read('./appConfig.ini')

MAX_PAGE = properties.getint('NMAP', 'max_page', fallback=2)
DISPLAY_COUNT = properties.getint('NMAP', 'display_count', fallback=10)
### PROP 세팅 END

### Logger 세팅 START
logger = myLogger.get_logger()
LOGGING_DATA = 25
### Logger 세팅 END


### 네이버플레이스 API
def naver_v5_api(pTarget):

    if not pTarget or len(pTarget) == 0:
        return pTarget
    
    logger.log(LOGGING_DATA, "[NAVER] TARGET : %s", pTarget)

    encText = urllib.parse.quote(pTarget)
    baseurl = "https://map.naver.com/v5/api/search?caller=pcweb&query=" + encText  # JSON 결과

    storeList = {"items": []}
    page = 1
    logger.log(LOGGING_DATA, "[NAVER] API START")
    while page < MAX_PAGE: # 최대값 제한
        url = baseurl
        url += "&type=all&page=" + str(page)
        url += "&displayCount=" + str(DISPLAY_COUNT)
        url += "&isPlaceRecommendationReplace=true&lang=ko"
        newRequest = urllib.request.Request(url)
        
        # header 설정
        newRequest.add_header("authority"           , "map.naver.com")
        newRequest.add_header("method"              , "GET")
        newRequest.add_header("scheme"              , "https")
        # newRequest.add_header("accept"              , "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
        # newRequest.add_header("pragma"              , "no-cache")
        newRequest.add_header("accept-encoding"     , "gzip, deflate, br")
        # newRequest.add_header("accept-language"     , "ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4")
        # newRequest.add_header("cache-control"       , "no-cache")
        newRequest.add_header("content-type"        , "application/json")
        newRequest.add_header("referer"             , "https://map.naver.com/")
        newRequest.add_header("user-agent"          , "Mozilla/5.0")
        newRequest.add_header("cookie"              , "hide_intro_popup=true; NNB=YB4ZCP2KPBQF3; BMR=s=1682410501834&r=&r2=; nid_inf=-1200312348; NID_AUT=dDyW/jafIlmW8RZYFO/qx0sibaRZ; NID_JKL=bj17HrEtZWoAlqRks=; _ga_7VKFYR6RV1=GS1.1.1.0.1.60; _ga=GA1.2..; _gid=GA1.2..; NID_SES=AAABvjvT3; _naver_usersession_=zjDUtGtcOJ; page_uid=UE5yLlpy8ejBsd9oyAK-014447; csrf_token=dc6c34e04198ab0f1ae")
        # newRequest.add_header("sec-ch-ua-platform"  , "Windows")
        # newRequest.add_header("sec-fetch-dest"      , "document")
        response = urllib.request.urlopen(newRequest)
        rescode = response.getcode()
        if rescode == 200:
            response_body = gzip.decompress(response.read()).decode("utf-8")
            jsonObj = json.loads(response_body)
            # print(jsonObj)
            if not jsonObj or len(jsonObj) == 0 or len(jsonObj['result']['place']['list']) == 0: # 더이상 없으면 종료
                break
            else:
                 makeStoreList(jsonObj, storeList) # Json Ary 생성
        else:
            print("Error Code:" + rescode)
            return rescode
        page += 1

    logger.log(LOGGING_DATA, "[NAVER] API END")
    logger.log(LOGGING_DATA, "[NAVER] DATA_CNT : %s", len(storeList['items']))
    return storeList


## 응답값으로부터 장소리스트 Json Object 생성
def makeStoreList(pJson, storeList):
    
    jsonAry = pJson['result']['place']['list']
    for index in range(0, len(jsonAry)):
        storeName = jsonAry[index]['name']
        category = jsonAry[index]['category']
        roadAddress = jsonAry[index]['roadAddress']
        address = jsonAry[index]['address']
        numOfRevivews = jsonAry[index]['reviewCount']
        numOfPlaceRevivews = jsonAry[index]['placeReviewCount']

        tempDic = {
            "title": storeName,
            "category": category,
            "roadAddress": roadAddress.replace(storeName, ""), # 주소에 장소명이 들어가 있는 경우 제거
            "address": address.replace(storeName, ""), # 주소에 장소명이 들어가 있는 경우 제거
            "rating": numOfRevivews,
            "reviewsNum": numOfPlaceRevivews,
        }
        storeList["items"].append(tempDic)

    # print(storeList)
    return
