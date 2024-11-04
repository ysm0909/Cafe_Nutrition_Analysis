from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Chrome 옵션 설정
options = Options()
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')

# Chrome Driver 경로 지정 및 서비스 객체 생성
s = Service(r"selenium/chromedriver.exe")
driver = webdriver.Chrome(service=s, options=options)
driver.get("https://www.caffe-pascucci.co.kr/product/productList.asp?typeCode=00010020")

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

# 카테고리별 크롤링 시작
try:

    # 하위 카테고리 반복
    for n in range(1, 4):  # N=1부터 N=3까지 반복

        # 메인 카테고리 클릭
        category_xpath = '//*[@id="container"]/div[2]/ul/li[3]'
        driver.find_element(By.XPATH, category_xpath).click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/ul/li[3]/ul/li[1]')))
        time.sleep(1)

        try:
            sub_category_xpath = f'//*[@id="container"]/div[2]/ul/li[3]/ul/li[{n}]'
            sub_category_element = driver.find_element(By.XPATH, sub_category_xpath)
            category_name = sub_category_element.text
            sub_category_element.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/ul/li[4]/ul/li[1]')))
            time.sleep(1)
            
            # 중분류 리스트 반복
            for a in range(1, 6):  # 최대 5개 중분류 (추정)
                try:

                    click_mid_xpath = f'//*[@id="container"]/div[2]/ul/li[4]'
                    click_mid_element = driver.find_element(By.XPATH, click_mid_xpath)
                    click_mid_element.click()
                    time.sleep(1)

                    middle_category_xpath = f'//*[@id="container"]/div[2]/ul/li[4]/ul/li[{a}]'
                    middle_category_element = driver.find_element(By.XPATH, middle_category_xpath)
                    middle_category_element.click()
                    time.sleep(1)
                    
                    # 음료 리스트 크롤링
                    rows = driver.find_elements(By.XPATH, '//*[@id="container"]/div[3]/ul/li')
                    for c in range(1, len(rows) + 1):  # 각 줄의 음료 리스트 순회
                        for Q in [1, 2]:  # div[1]과 div[2] 순회
                            for b in range(1, 3):  # 각 div에서 a[1]과 a[2] 탐색
                                try:
                                    drink_xpath = f'//*[@id="container"]/div[3]/ul/li[{c}]/div[{Q}]/a[{b}]'
                                    element = driver.find_element(By.XPATH, drink_xpath)
                                    driver.execute_script("arguments[0].scrollIntoView(true);", element)  # 요소가 보이도록 스크롤
                                    time.sleep(0.5)
                                    
                                    # 클릭 시도
                                    clicked = False
                                    retries = 0
                                    while not clicked and retries < 3:
                                        try:
                                            element.click()
                                            clicked = True
                                        except ElementClickInterceptedException:
                                            time.sleep(1)
                                            retries += 1
                                            driver.execute_script("arguments[0].click();", element)  # JavaScript로 클릭

                                    # section 번호 설정
                                    section_num = 1 if Q == 1 else 2

                                    # 메뉴 정보 크롤링 (기본값 설정)
                                    def get_text(xpath, default="정보 없음"):
                                        try:
                                            return driver.find_element(By.XPATH, xpath).text
                                        except NoSuchElementException:
                                            return default

                                    time.sleep(1)

                                    # 메뉴명 및 세부 정보 추출
                                    data["카테고리"].append(category_name)
                                    data["메뉴명"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[1]/div/h1/strong'))
                                    info_text = get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[1]/div/p[1]')
                                    data["정보"].append(info_text.split("※")[0] if "※" in info_text else info_text)
                                    data["용량"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[2]/div/ul/li[1]/ul/li[1]/p'))
                                    data["1회제공량(kcal)"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[2]/div/ul/li[1]/ul/li[2]/p'))
                                    data["나트륨 (mg)"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[2]/div/ul/li[1]/ul/li[6]/p'))
                                    data["포화지방 (g)"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[2]/div/ul/li[1]/ul/li[5]/p'))
                                    data["당류 (g)"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[2]/div/ul/li[1]/ul/li[3]/p'))
                                    data["단백질 (g)"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[2]/div/ul/li[1]/ul/li[4]/p'))
                                    data["카페인 (mg)"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[2]/div/ul/li[1]/ul/li[7]/p'))
                                    data["알레르기성분"].append(get_text(f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[2]/div/ul/li[1]/ul/li[8]/p'))

                                    # 닫기 버튼
                                    try:
                                        close_button = driver.find_element(By.XPATH, f'//*[@id="container"]/div[3]/ul/li[{c}]/section[{section_num}]/div/div[1]/div/div[1]/button/img')
                                        close_button.click()
                                    except NoSuchElementException:
                                        pass

                                    time.sleep(1)

                                except NoSuchElementException:
                                    break  # 더 이상 열의 항목이 없으면 다음 div로 이동

                except NoSuchElementException:
                    print(f"Middle category {a} not found.")
                    break  # 더 이상 중분류가 없으면 반복 종료

            # 하위 카테고리로 돌아가기
            driver.back()

        except NoSuchElementException:
            print(f"Sub-category {n} not found.")
            continue  # 하위 카테고리가 없는 경우 건너뜀

finally:
    # 수집된 데이터를 CSV 파일로 저장
    df = pd.DataFrame(data)
    df.to_csv("pascucci_menu.csv", index=False, encoding="utf-8-sig")
    print("CSV 파일 저장 완료")

    driver.quit()



