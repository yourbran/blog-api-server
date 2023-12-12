from flask import Flask, render_template, jsonify, request
# from flask_cors import CORS
from configparser import ConfigParser
from kmap import scraping_kakao
from nmap import naver_v5_api
import urllib.request
import urllib.parse
import json
import myLogger

app = Flask(__name__)

# ### Logger 세팅 START
logger = myLogger.get_logger()
LOGGING_DATA = 25
# ### Logger 세팅 END

### PROP 세팅 START
properties = ConfigParser()
properties.read('./appConfig.ini')
JUSO_API_KEY = properties.get('COMMON', 'juso_api_confmKey')
ADDRESS_KEY = properties.get('COMMON', 'address_key')
### PROP 세팅 END


@app.route("/")
def hello_world():
    return "<p>Hello, WORld!</p>"


## 네이버 결과
### 네이버API V5 결과 수신 후 Juso API를 통한 우편번호 붙히기
@app.route("/searchaddr1", methods=["POST"])
def search_store_naver():
    reqJson = request.get_json()
    target = reqJson["name"]
    inputKey = reqJson["addressAuthKey"]

    authYn = validate_auth(inputKey)
    if not authYn:
        responseJson = make_fail_response(2)
        return responseJson, 200
    
    resultJson = naver_v5_api(target)
    if not resultJson or len(resultJson) == 0:
        responseJson = make_fail_response(1)
        return responseJson, 200
    else:
        responseJson = post_process(json.dumps(resultJson)) # 후속처리(우편번호 세팅)
        return responseJson, 200


## 카카오 결과
### 카카오맵 스크래핑 후 Juso API를 통한 우편번호 붙히기
@app.route("/searchaddr2", methods=["POST"])
def search_store_kakao():
    reqJson = request.get_json()
    target = reqJson["name"]
    inputKey = reqJson["addressAuthKey"]
    
    authYn = validate_auth(inputKey)
    if not authYn:
        responseJson = make_fail_response(2)
        return responseJson, 200
    
    resultJson = scraping_kakao(target) # 카카오맵 스크래핑
    if not resultJson or len(resultJson) == 0:
        responseJson = make_fail_response(1)
        return responseJson, 200
    else:
        responseJson = post_process(json.dumps(resultJson)) # 후속처리(우편번호 세팅)
        return responseJson, 200


## 후속처리
# 1 : 포털 주소검색 결과에 우편번호 붙히기
# 2 : 도로명주소가 없을 경우 지번주소로 대체
def post_process(pStr):
    jsonObj = json.loads(pStr)
    tempList = list()
    storeLists = jsonObj["items"]
    for store in storeLists:
        realRoadAddress = make_real_address(store["roadAddress"])
        # print("정제된 도로명주소 : " + realRoadAddress)
        zipcode = search_zipcode(realRoadAddress)  # 정제된 도로명주소로 1차 시도
        if zipcode == "(조회실패)":
            realAddress = make_real_address(store["address"])
            logger.log(LOGGING_DATA, "정제된 지번주소 : %s", realAddress)
            zipcode = search_zipcode(realAddress)  # 정제된 지번주소로 2차 시도
        newDic = store
        newDic["zipcode"] = zipcode
        if not store["roadAddress"] or len(store["roadAddress"]) == 0:
            newDic["roadAddress"] = "(지)" + store["address"]  # 도로명주소가 없을 경우 지번주소로 대체
        tempList.append(newDic)
    resultJson = dict()
    resultJson["items"] = tempList
    resultJson["errCd"] = '000'
    resultJson["errMsg"] = '정상'
    return resultJson


# 주소.go.kr
## 사용기간 : 2023-10-21 ~ 2024-01-20
## http://3.38.61.176/
def search_zipcode(address):
    if not address or len(address) == 0:
        return "(조회실패)"

    urls = "https://business.juso.go.kr/addrlink/addrLinkApi.do"
    confmKey = JUSO_API_KEY
    params = {
        "keyword": address,
        "countPerPage": "1",
        "currentPage": "1",
        "confmKey": confmKey,
        "resultType": "json",
    }

    params_str = urllib.parse.urlencode(params)
    url = "{}?{}".format(urls, params_str)
    # print(url)

    newRequest = urllib.request.Request(url)
    response = urllib.request.urlopen(newRequest)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        return extract_zipcode(response_body.decode("utf-8"))  # 결과로부터 우편번호 추출
    else:
        print("Error Code:" + rescode)
        return rescode


## 우편번호 추출
def extract_zipcode(pJsonStr):
    jsonObj = json.loads(pJsonStr)
    # print(jsonObj)
    if (
        not jsonObj.get("results")
        or not jsonObj.get("results").get("juso")
        or len(jsonObj.get("results").get("juso")) == 0
    ):
        return "(조회실패)"
    else:
        jusoLists = jsonObj["results"]["juso"]
        juso = jusoLists[0]
        zipcode = juso["zipNo"]
        # print(">>>>>>>>>>>>>>zipcode : " + zipcode)
        return zipcode


## 전체 주소에서 4번째 항목까지만 추출
def make_real_address(rawAddress):
    if not rawAddress:
        return ""
    else:
        tempAddress = rawAddress.split()
        returnAddress = ""

        for idx, addressToken in enumerate(tempAddress):
            if idx == 0:
                returnAddress = addressToken
            elif idx < 4:
                returnAddress = returnAddress + " " + addressToken
            else:
                break

    return returnAddress


## 실패 RESPONSE 생성
def make_fail_response(case):

    jsonObj = dict()

    if case == 1:
        jsonObj["errCd"] = "901"
        jsonObj["errMsg"] = "조회실패"
    elif case == 2:
        jsonObj["errCd"] = "902"
        jsonObj["errMsg"] = "인증실패"
    else:
        jsonObj["errCd"] = "900"
        jsonObj["errMsg"] = "통신실패"

    return jsonObj


## 인증값 검증
def validate_auth(param):
    inputParam = param
    authKey = ADDRESS_KEY

    if inputParam == authKey:
        return True
    else:
        return False
    