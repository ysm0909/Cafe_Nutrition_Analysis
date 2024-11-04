from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re

# Chrome 옵션 설정
options = Options()
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')

# Chrome Driver 경로 지정 및 서비스 객체 생성
s = Service(r"selenium/chromedriver.exe")
driver = webdriver.Chrome(service=s, options=options)
driver.get("https://www.baristapaulbassett.co.kr/menu/List.pb?cid1=A")

# 데이터 저장 구조 초기화
data = {
    "카테고리": [],
    "메뉴명": [],
    "정보": [],
    "용량": [],
    "1회제공량(kcal)": [],
    "나트륨 (mg)": [],
    "포화지방 (g)": [],
    "당류 (g)": [],
    "단백질 (g)": [],
    "카페인 (mg)": [],
    "알레르기성분": []
}

# 영어 제거 및 한글만 남기는 함수
def remove_english(text):
    return re.sub(r'[a-zA-Z]', '', text).strip()

# 명시적 대기를 위한 함수 정의
def get_text(xpath, default="정보 없음", remove_eng=False):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        text = element.text
        if remove_eng:
            text = remove_english(text)
        return text
    except (NoSuchElementException, TimeoutException):
        return default

# pSize_S 또는 pSize_O 중 하나에서 값을 추출하는 함수
def get_size_text(primary_xpath, secondary_xpath, third_xpath):
    if driver.find_elements(By.XPATH, primary_xpath):
        return driver.find_element(By.XPATH, primary_xpath).text
    elif driver.find_elements(By.XPATH, secondary_xpath):
        return driver.find_element(By.XPATH, secondary_xpath).text
    elif driver.find_elements(By.XPATH, third_xpath):
        return driver.find_element(By.XPATH, third_xpath).text
    else:
        return "정보 없음"

# 배열 길이 맞추기 함수
def fill_missing_data(data):
    max_len = max(len(lst) for lst in data.values())
    for key, lst in data.items():
        lst.extend(["정보 없음"] * (max_len - len(lst)))

# 카테고리별 크롤링 시작
try:
    for A in range(2, 5):  # 카테고리 A=2부터 4까지만 반복
        # 카테고리 설정
        category_xpath = f'//*[@id="container"]/div[2]/ul/li[{A}]'
        category_element = driver.find_element(By.XPATH, category_xpath)
        category_name = category_element.text
        category_element.click()
        time.sleep(1)

        # 페이지 스크롤 제일 아래로 이동 후 위로
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # 음료 리스트 크롤링
        items = driver.find_elements(By.XPATH, '//*[@id="container"]/div[4]/ul/li')
        for i in range(1, len(items) + 1):
            try:
                drink_xpath = f'//*[@id="container"]/div[4]/ul/li[{i}]/a/div[1]/img'
                element = driver.find_element(By.XPATH, drink_xpath)
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                element.click()
                time.sleep(1)
                
                # 메뉴 정보 크롤링
                data["카테고리"].append(category_name)
                data["메뉴명"].append(get_text('//*[@id="container"]/div[1]/div/div[1]/dl/dt', remove_eng=True))
                data["정보"].append(get_text('//*[@id="container"]/div[1]/div/div[1]/dl/dd'))
  
                # pSize_S 또는 pSize_O 중 하나에서 용량 추출
                data["용량"].append(get_size_text('//*[@id="pSize_S"]/span/span', '//*[@id="pSize_O"]/span/span','//*[@id="pSize_G"]/span/span'))
                data["1회제공량(kcal)"].append(get_size_text('//*[@id="pSize_S"]/ul/li[1]/span[2]', '//*[@id="pSize_O"]/ul/li[1]/span[2]', '//*[@id="pSize_G"]/ul/li[1]/span[2]'))
                data["나트륨 (mg)"].append(get_size_text('//*[@id="pSize_S"]/ul/li[3]/span[2]', '//*[@id="pSize_O"]/ul/li[3]/span[2]', '//*[@id="pSize_G"]/ul/li[3]/span[2]'))
                data["포화지방 (g)"].append(get_size_text('//*[@id="pSize_S"]/ul/li[5]/span[2]', '//*[@id="pSize_O"]/ul/li[5]/span[2]', '//*[@id="pSize_G"]/ul/li[5]/span[2]'))
                data["당류 (g)"].append(get_size_text('//*[@id="pSize_S"]/ul/li[2]/span[2]', '//*[@id="pSize_O"]/ul/li[2]/span[2]', '//*[@id="pSize_G"]/ul/li[2]/span[2]'))
                data["단백질 (g)"].append(get_size_text('//*[@id="pSize_S"]/ul/li[4]/span[2]', '//*[@id="pSize_O"]/ul/li[4]/span[2]', '//*[@id="pSize_G"]/ul/li[4]/span[2]'))
                data["카페인 (mg)"].append(get_size_text('//*[@id="pSize_S"]/ul/li[6]/span[2]', '//*[@id="pSize_O"]/ul/li[6]/span[2]', '//*[@id="pSize_G"]/ul/li[6]/span[2]'))

                time.sleep(1)
                 # 알레르기성분 추출
                try:
                    if len(driver.find_elements(By.XPATH, '//*[@id="container"]/div[1]/div/ul/li')) >= 4:
                        allergy_text = get_text('//*[@id="container"]/div[1]/div/ul/li[3]')
                    elif len(driver.find_elements(By.XPATH, '//*[@id="container"]/div[1]/div/ul/li')) == 3:
                        allergy_text = get_text('//*[@id="container"]/div[1]/div/ul/li[2]')
                except NoSuchElementException:
                    data["알레르기성분"].append("정보 없음")

                # 뒤로 가기 및 대기
                max_retries = 3
                retries = 0
                while retries < max_retries:
                    driver.back()
                    try:
                        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, drink_xpath)))
                        break  # 뒤로 가기 성공 시 루프 탈출
                    except TimeoutException:
                        retries += 1
                        print(f"Retry {retries}/{max_retries} - Retrying back navigation")
                        if retries == max_retries:
                            print("뒤로 가기 실패 - 다음 항목으로 이동")
                            break
                time.sleep(1)

            except NoSuchElementException:
                print(f"Drink {i} not found in category {category_name}.")
                # 기본값 추가로 모든 배열 길이 동일하게 유지
                data["카테고리"].append(category_name)
                data["메뉴명"].append("정보 없음")
                data["정보"].append("정보 없음")
                data["용량"].append("정보 없음")
                data["1회제공량(kcal)"].append("정보 없음")
                data["나트륨 (mg)"].append("정보 없음")
                data["포화지방 (g)"].append("정보 없음")
                data["당류 (g)"].append("정보 없음")
                data["단백질 (g)"].append("정보 없음")
                data["카페인 (mg)"].append("정보 없음")
                data["알레르기성분"].append("정보 없음")

        # 다음 카테고리로 이동하기 전 맨 위로 스크롤 및 예외 처리
        driver.execute_script("window.scrollTo(0, 0);")  # 페이지 맨 위로 스크롤
        time.sleep(1)

finally:
    # 배열 길이 맞추기
    fill_missing_data(data)
    
    # 수집된 데이터를 CSV 파일로 저장
    df = pd.DataFrame(data)
    df.to_csv("paulbassett_menu.csv", index=False, encoding="utf-8-sig")
    print("CSV 파일 저장 완료")

    driver.quit()


