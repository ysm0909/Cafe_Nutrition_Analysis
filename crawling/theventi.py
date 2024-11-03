from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time

# Chrome 옵션 설정
options = Options()
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')

# Chrome Driver 경로 지정 및 서비스 객체 생성
s = Service(r"chromedriver_path")  # 여기에 ChromeDriver 경로 설정
driver = webdriver.Chrome(service=s, options=options)
driver.get("https://www.theventi.co.kr/new2022/menu/all.html")

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

# 카테고리별 크롤링 시작 (N=2부터 N=7까지)
for n in range(2, 8):
    try:
        # 카테고리 요소 찾기
        category_xpath = f'//*[@id="contents"]/div/div/div[1]/ul/li[{n}]/a'
        
        # 스크롤을 이용해서 요소를 화면에 표시
        category_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, category_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", category_element)
        time.sleep(0.5)  # 스크롤 후 대기
        
        # 카테고리 요소 클릭
        ActionChains(driver).move_to_element(category_element).click(category_element).perform()
        time.sleep(1)  # 페이지 로드 대기

        # 카테고리 내 음료 정보 크롤링
        items = driver.find_elements(By.XPATH, '//*[@id="contents"]/div/div/div[2]/ul/li')
        item_count = len(items)

        for a in range(1, item_count + 1):
            try:
                # 각 음료 클릭
                menu_xpath = f'//*[@id="contents"]/div/div/div[2]/ul/li[{a}]/a/div[1]'
                menu_item = driver.find_element(By.XPATH, menu_xpath)
                menu_item.click()
                time.sleep(1)  # 페이지 로드 시간 대기

                # 각 항목 크롤링
                def get_text(xpath, default="정보 없음", delimiter=None):
                    try:
                        text = driver.find_element(By.XPATH, xpath).text
                        if delimiter:
                            return text.split(delimiter)[0]  # 구분자로 텍스트 분할
                        return text
                    except NoSuchElementException:
                        return default

                data["카테고리"].append(get_text(category_xpath))
                data["메뉴명"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/p/span[3]'))
                data["정보"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[1]').split('\n')[0])
                data["용량"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[1]', delimiter=")"))
                data["1회제공량(kcal)"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[2]'))
                data["나트륨 (mg)"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[6]', delimiter="("))
                data["포화지방 (g)"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[5]', delimiter="("))
                data["당류 (g)"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[3]', delimiter="("))
                data["단백질 (g)"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[4]', delimiter="("))
                data["카페인 (mg)"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[7]', delimiter="("))
                data["알레르기성분"].append(get_text('/html/body/div[2]/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[8]'))

                # 상세 페이지 닫기
                close_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/a/i')
                close_button.click()
                time.sleep(0.5)  # 페이지 닫기 후 대기

            except NoSuchElementException:
                print(f"음료 정보 누락됨: {category_name} - {a}번째 음료")
                continue

    except NoSuchElementException:
        print(f"카테고리 누락됨: {n}")
        continue

# 수집된 데이터를 CSV 파일로 저장
df = pd.DataFrame(data)
df.to_csv("theventi_menu.csv", index=False, encoding="utf-8-sig")
print("CSV 파일 저장 완료")

driver.quit()
