import os
import sys
import shutil
import pathlib

import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

if(len(sys.argv)==1):
    sys.exit("No queries provided.")


download_path = pathlib.Path.cwd()/'urls'

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")
profile.set_preference("browser.download.dir", str(download_path))

queries = sys.argv[1:]

wd = webdriver.Firefox(profile)
wd.get("http://images.google.com")

for query in queries:

    print(f"Downloading {query}.csv ...")

    search_box = wd.find_element_by_name('q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    while True:
        try:
            show_more = wd.find_element_by_xpath("""
                //input[@value='Show more results']
            """)
            show_more.click()
        except:
            wd.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(1)
            try:
                if wd.find_element_by_css_selector(".OuJzKb").is_displayed():
                    break
            except:
                continue

    curr_size = len(list(download_path.glob('**/*')))

    wd.execute_script("""
                urls=Array.from(document.querySelectorAll('.rg_i')).map(el=> el.hasAttribute('data-src')?el.getAttribute('data-src'):el.getAttribute('data-iurl'));
                window.open('data:text/csv;charset=utf-8,'+escape(urls.join('\\n')));
            """)

    while len(list(download_path.glob('**/*'))) == curr_size:
        continue

    wd.back()

    paths = sorted(pathlib.Path(download_path).iterdir(), key=os.path.getmtime)

    latest = paths[-1]
    latest = latest.rename(f'{query}.csv')
    shutil.move(str(latest),str(download_path))


wd.quit()



