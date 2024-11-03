from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Chrome 옵션 설정
options = Options()
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')

# Chrome Driver 경로 지정 및 서비스 객체 생성
s = Service(r"selenium/chromedriver.exe")
driver = webdriver.Chrome(service=s, options=options)
driver.get("https://www.coffeebeankorea.com/menu/list.asp?category=32")

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
    "탄수화물 (g)": []
}

# 카테고리별 크롤링 시작
for n in range(1, 10):  # N=1부터 N=9까지 반복
    try:
        # 카테고리 요소 클릭
        category_xpath = f'//*[@id="contents"]/div/ul/li[1]/ul/li[{n}]/a'
        category_element = driver.find_element(By.XPATH, category_xpath)
        category_name = category_element.text
        category_element.click()
        time.sleep(1)  # 페이지 로드 시간 대기

        # 페이지별 음료 정보 크롤링
        page = 1
        while True:
            items = driver.find_elements(By.XPATH, '//*[@id="contents"]/div/div/ul/li')
            item_count = len(items)

            for a in range(1, item_count + 1):
                # 메뉴 정보를 각각 크롤링 (존재하지 않으면 기본값 설정)
                def get_text(xpath, default="정보 없음"):
                    try:
                        return driver.find_element(By.XPATH, xpath).text
                    except NoSuchElementException:
                        return default

                data["카테고리"].append(category_name)
                data["메뉴명"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/dl/dt/span[2]'))
                data["정보"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/dl/dd'))
                data["용량"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/div[1]/dl[1]/dt'))
                kcal_text = get_text(f'//*[@id="content-wrap"]/div[2]/div/div[2]/ul/li[{a}]/div[2]/div[2]/ul/li[2]/div[2]')
                data["1회제공량(kcal)"].append(kcal_text.split(": ")[-1] if ": " in kcal_text else kcal_text)
                data["나트륨 (mg)"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/div[1]/dl[2]/dt'))
                data["포화지방 (g)"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/div[1]/dl[7]/dt'))
                data["당류 (g)"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/div[1]/dl[4]/dt'))
                data["단백질 (g)"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/div[1]/dl[5]/dt'))
                data["카페인 (mg)"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/div[1]/dl[6]/dt'))
                data["탄수화물 (g)"].append(get_text(f'//*[@id="contents"]/div/div/ul/li[{a}]/div[1]/dl[3]/dt'))

            # 다음 페이지로 이동
            try:
                next_page_elements = driver.find_elements(By.XPATH, '//*[@id="contents"]/div/div/div/a')
                if len(next_page_elements) <= 2 or page > len(next_page_elements) - 2:
                    break  # 다음 페이지가 없는 경우 종료
                next_page_elements[-2].click()  # 다음 페이지 버튼 클릭
                page += 1
                WebDriverWait(driver, 10).until(EC.staleness_of(items[0]))  # 페이지 로드 대기

            except NoSuchElementException:
                break  # 다음 페이지가 없으면 루프 종료

    except NoSuchElementException:
        continue  # 카테고리가 없는 경우 건너뜀

# 수집된 데이터를 CSV 파일로 저장
df = pd.DataFrame(data)
df.to_csv("coffeebean_menu.csv", index=False, encoding="utf-8-sig")
print("CSV 파일 저장 완료")

driver.quit()
