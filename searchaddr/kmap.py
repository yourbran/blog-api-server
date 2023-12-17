from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from configparser import ConfigParser
from common import myLogger

### PROP 세팅 START
properties = ConfigParser()
properties.read('./appConfig.ini')
TOT_PAGE = properties.getint('KMAP', 'tot_page', fallback=2)
### PROP 세팅 END

### Logger 세팅 START
logger = myLogger.get_logger()
LOGGING_DATA = 25
### Logger 세팅 END

### 카카오맵 스크래핑
def scraping_kakao(pTarget):

    if not pTarget or len(pTarget) == 0:
        return pTarget
    
    logger.log(LOGGING_DATA, "[KAKAO] TARGET : %s", pTarget)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )

    logger.log(LOGGING_DATA, "[KAKAO] API START")
    baseUrl = "https://map.kakao.com/"
    try:
        driver.get(baseUrl)
        search = driver.find_element(By.CSS_SELECTOR, "div.box_searchbar > input.query") # 검색
        search.send_keys(pTarget)
        search.send_keys(Keys.ENTER)
        sleep(0.2)

        place_tab = driver.find_element(
            By.CSS_SELECTOR, "#info\.main\.options > li.option1 > a" # 장소TAB 이동
        )
        place_tab.send_keys(Keys.ENTER)
        sleep(0.2)

        storeList = {"items": []}
        page = 0
        totPage = 0
        error_cnt = 0

        while 1:
            try:
                page += 1
                totPage += 1

                placeList = driver.find_elements(
                    By.CSS_SELECTOR, ".placelist > .PlaceItem"
                )  # 해당 페이지 결과 리스트

                if totPage != 1 or len(placeList) >= 15 :
                    driver.find_element(
                        By.XPATH, f'//*[@id="info.search.page.no{page}"]'
                    ).send_keys(
                        Keys.ENTER
                    )  # 페이지번호 클릭
                    sleep(0.2)

                place_scraping(driver, storeList)  # 스크래핑

                if totPage >= TOT_PAGE: # 최대값 제한
                    break
                
                if len(placeList) < 15:  # 장소 개수가 15개 미만일 경우 마지막 페이지로 판단
                    break

                if not driver.find_element(
                    By.XPATH, '//*[@id="info.search.page.next"]'
                ).is_enabled():  # 다음 버튼이 없을 경우 마지막 페이지로 판단
                    break

                if page % 5 == 0:  # 다섯번 째 페이지 도달 시 0으로 초기화 (5개 순환 주기)
                    driver.find_element(
                        By.XPATH, '//*[@id="info.search.page.next"]'
                    ).send_keys(Keys.ENTER)
                    sleep(0.2)
                    page = 0
                    
            except Exception as e:
                error_cnt += 1
                logger.error("While Exception")
                logger.error(e)
                if error_cnt > 5:
                    break
    finally:
        driver.quit()

    # print(storeList)
    logger.log(LOGGING_DATA, "[KAKAO] API END")
    logger.log(LOGGING_DATA, "[KAKAO] DATA_CNT : %s", len(storeList['items']))
    return storeList


def place_scraping(driver, storeList):
    placeList = driver.find_elements(By.CSS_SELECTOR, ".placelist > .PlaceItem")

    for index in range(len(placeList)):
        storeNames = driver.find_elements(
            By.CSS_SELECTOR, ".head_item > .tit_name > .link_name"
        )
        category = driver.find_elements(
            By.CSS_SELECTOR, ".head_item > .subcategory"
        )
        address_list = driver.find_elements(By.CSS_SELECTOR, ".info_item > .addr")
        address = address_list.__getitem__(index).find_elements(By.CSS_SELECTOR, "p")
        ratings = driver.find_elements(
            By.CSS_SELECTOR,
            ".rating > .score > .num",
        )
        reviews = driver.find_elements(
            By.CSS_SELECTOR,
            ".rating > .review > em",
        )

        storeName = storeNames[index].text
        categoryName = category[index].text
        roadAddress = address.__getitem__(0).text
        address = address.__getitem__(1).text
        rating = ratings[index].text
        numOfRevivews = reviews[index].text

        tempDic = {
            "title": storeName,
            "category": categoryName,
            "roadAddress": roadAddress,
            "address": address,
            "rating": rating,
            "reviewsNum": numOfRevivews,
        }
        # print(tempDic)
        storeList["items"].append(tempDic)
