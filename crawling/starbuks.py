from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Chrome 옵션 설정
options = Options()
options.add_argument('--disable-infobars')  # 정보바 비활성화
options.add_argument('--disable-extensions')  # 확장 기능 비활성화

# Chrome Driver 경로 지정 및 서비스 객체 생성
s = Service(r"selenium/chromedriver.exe")

# 드라이버 초기화
driver = webdriver.Chrome(service=s, options=options)
driver.get("https://www.starbucks.co.kr/menu/drink_list.do")
wait = WebDriverWait(driver, 10)

# 데이터 저장 구조 초기화
data = {
    "카테고리": [],
    "메뉴명": [],
    "정보": [],
    "용량": [],
    "1회제공량(kcal)": [],
    "나트륨(mg)": [],
    "포화지방(g)": [],
    "당류(g)": [],
    "단백질(g)": [],
    "카페인(mg)": [],
    "알레르기성분": []
}

# 모든 카테고리 요소 찾기
categories = driver.find_elements(By.XPATH, '//*[@id="container"]/div[2]/div[2]/div/dl/dd[1]/div[1]/dl/dt/a')

# 각 카테고리별로 순회
for category_index in range(len(categories)):
    categories = driver.find_elements(By.XPATH, '//*[@id="container"]/div[2]/div[2]/div/dl/dd[1]/div[1]/dl/dt/a')
    category_element = categories[category_index]
    category_name = category_element.text  # 카테고리명 저장
    category_element.click()  # 카테고리 클릭
    time.sleep(1)  # 로딩 대기

    # 현재 카테고리에서 모든 음료 순회
    drink_index = 1
    while True:
        try:
            # dd[N] 부분 동적 설정을 위해 카테고리 인덱스를 `N`으로 매핑
            drink_xpath = f'//*[@id="container"]/div[2]/div[2]/div/dl/dd[1]/div[1]/dl/dd[{category_index + 1}]/ul/li[{drink_index}]/dl/dt/a/img'
            drink_element = driver.find_element(By.XPATH, drink_xpath)
            ActionChains(driver).move_to_element(drink_element).click().perform()
            time.sleep(1)

            # 각 정보 크롤링
            data["카테고리"].append(category_name)
            data["메뉴명"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/div[1]/h4').text)
            data["정보"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/div[1]/p').text)
            data["용량"].append(driver.find_element(By.XPATH, '//*[@id="product_info01"]/p/b').text)
            data["1회제공량(kcal)"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/form/fieldset/div/div[2]/ul[1]/li[1]/dl/dd').text)
            data["나트륨(mg)"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/form/fieldset/div/div[2]/ul[2]/li[1]/dl/dd').text)
            data["포화지방(g)"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/form/fieldset/div/div[2]/ul[1]/li[2]/dl/dd').text)
            data["당류(g)"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/form/fieldset/div/div[2]/ul[2]/li[2]/dl/dd').text)
            data["단백질(g)"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/form/fieldset/div/div[2]/ul[1]/li[3]/dl/dd').text)
            data["카페인(mg)"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/form/fieldset/div/div[2]/ul[2]/li[3]/dl/dd').text)
            data["알레르기성분"].append(driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[1]/div[2]/form/fieldset/div/div[3]/p').text)

            # 뒤로 가기 후 다음 음료로 이동
            driver.back()
            time.sleep(1)
            drink_index += 1

        except NoSuchElementException:
            # 현재 카테고리의 모든 음료 탐색 완료
            break

# 수집된 데이터를 CSV 파일로 저장
df = pd.DataFrame(data)
df.to_csv("csv_cafe/starbucks_menu.csv", index=False, encoding="utf-8-sig")
print("CSV 파일 저장 완료")

driver.quit()
