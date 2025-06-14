from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re

CHROMEDRIVER_PATH = './chromedriver.exe'

def extract_ids(url):
    match = re.search(r'titleId=(\d+)&no=(\d+)', url)
    return match.group(1), match.group(2) if match else (None, None)

def get_all_webtoon_comments(webtoon_url, max_pages):
    appId, episodeId = extract_ids(webtoon_url)

    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("headless")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(webtoon_url)
    time.sleep(3)

    # 클린봇 해제
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div/div[5]/a').click()
    # /html/body/div[1]/div[5]/div/div/div[4]/div[1]/div[3]/div/div/div[5]/a
    
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="cleanbot_dialog_checkbox_cbox_module"]').click()
    # /html/body/div[6]/div/div[2]/div[3]/div[2]/input

    #time.sleep(1)
    #driver.find_element(By.XPATH, '/html/body/div[6]/div/div[2]/div[4]/button').click()
    # /html/body/div[6]/div/div[2]/div[4]/button

    time.sleep(1)
    try:
        driver.find_element(By.XPATH, '/html/body/div[6]/div/div[2]/div[4]/button').click()
    except Exception as e:
        driver.find_element(By.XPATH, '/html/body/div[7]/div/div[2]/div[4]/button').click()


    

    time.sleep(2)

    # 전체댓글 버튼 클릭 (XPath 기반)
    driver.find_element(By.XPATH, '//*[@id="cbox_module_wai_u_cbox_sort_option_tab2"]/span[2]').click()
    # /html/body/div[1]/div[5]/div/div/div[5]/div[1]/div[3]/div/div/div[4]/div[1]/div/ul/li[2]/a/span[2]
    time.sleep(2)

    # 페이지 클릭 먼저 다 수행
    page = 1
    while page < max_pages:
        try:
            next_button = driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div/div[7]/a/span/span/span[1]')
            # /html/body/div[1]/div[5]/div/div/div[4]/div[1]/div[3]/div/div/div[7]/a/span/span/span[1]
            next_button.click()
            page += 1
            time.sleep(2)
        except:
            print("👉 다음 페이지 없음 또는 클릭 실패")
            break

    time.sleep(2)

    # 댓글 수집
    contents = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_contents')
    users = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_nick')
    dates = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_date')
    likes = driver.find_elements(By.CSS_SELECTOR, 'em.u_cbox_cnt_recomm')
    dislikes = driver.find_elements(By.CSS_SELECTOR, 'em.u_cbox_cnt_unrecomm')

    data = []

    for i in range(len(contents)):
        content = contents[i].text.strip()
        user = users[i].text.strip()
        date = dates[i].text.strip()
        like = int(likes[i].text.strip().replace(',', '') or 0)
        dislike = int(dislikes[i].text.strip().replace(',', '') or 0)
        score = like - dislike

        data.append({
            'no': i + 1,
            'appId': appId,
            'episodeId': episodeId,
            'userName': user,
            'content': content,
            'score': score,
            'at': date
        })

    driver.quit()

    data = pd.DataFrame(data)


    #os.makedirs('static', exist_ok=True)
    #raw_filename = f"{appId}_{episodeId}.csv"
    #raw_path = os.path.join('static', raw_filename)
    #data.to_csv(raw_path, index=False, encoding='utf-8-sig')

    return data




