import datetime
import os
import time
from urllib.parse import urlparse
from urllib3.exceptions import MaxRetryError

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from expressvpn.wrapper import random_connect
from expressvpn import wrapper
import logging
logging.basicConfig(filename='log.dat')

TERMCOLOR = True
if TERMCOLOR:
    from termcolor import colored


def printm(text, color='white', switch=False):
    # wrapper for standard print function
    if switch:
        print(colored(text, color))
    else:
        print(text)
    return


def change_ip():
    max_attempts = 10
    attempts = 0
    while True:
        attempts += 1
        try:
            logging.info('GETTING NEW IP')
            wrapper.random_connect()
            logging.info('SUCCESS')
            return
        except Exception as e:
            if attempts > max_attempts:
                logging.error('Max attempts reached for VPN. Check its configuration.')
                logging.error('Browse https://github.com/philipperemy/expressvpn-python.')
                logging.error('Program will exit.')
                exit(1)
            logging.error(e)
            logging.error('Skipping exception.')


def rotate_proxy():

    options = webdriver.ChromeOptions()
    # options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(chrome_options=options)
    driver.get("https://sslproxies.org/")

    driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH,
                                          "//table[@class='table table-striped table-bordered dataTable']//th[contains(., 'IP Address')]"))))
    ips = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.XPATH,
                                               "//table[@class='table table-striped table-bordered dataTable']//tbody//tr[@role='row']/td[position() = 1]")))]
    ports = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.XPATH,
                                               "//table[@class='table table-striped table-bordered dataTable']//tbody//tr[@role='row']/td[position() = 2]")))]
    driver.quit()
    proxies = []
    for i in range(0, len(ips)):
        proxies.append(ips[i] + ':' + ports[i])
    print(proxies)
    for i in range(0, len(proxies)):
        try:
            print("Proxy selected: {}".format(proxies[i]))
            options = webdriver.ChromeOptions()
            options.add_argument('--proxy-server={}'.format(proxies[i]))
            driver = webdriver.Chrome(options=options, executable_path=r'C:\WebDrivers\chromedriver.exe')
            driver.get("https://www.whatismyip.com/proxy-check/?iref=home")
            if "Proxy Type" in WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "p.card-text"))):
                break
        except Exception:
            driver.quit()
    print("Proxy Invoked")


def is_valid(url):
    """
    Checks whether `url` is a valid URL.

    :param url: <str> path to the location of images to download

    :return is_valid: <bool> whether or not the path is valid
    """

    parsed = urlparse(url)
    is_valid = bool(parsed.netloc) and bool(parsed.scheme)
    return is_valid


def get_links(url, show, number, root_data):
    """
    A function to get links to all the thumbnails in a url-specified runway show

    :param url: <str> url the page that has all of the thumbnails

    :return imgs: <list<str>> list of full url paths to the thumbails. also outputs a csv file containing the links
    :return show_name: <str> name of the show corresponding to the images
    """

    # Define Chrome options to open the window in maximized mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # Initialize the Chrome webdriver and open the URL
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # find show name
    soup_show = bs(requests.get(url).content, "html.parser")
    titles = soup_show.find_all("span")
    for item in titles:
        str_item = str(item)
        if 'pageTitle' in str_item:
            show_name = str_item.split("""pageTitle">""")[-1].split("""</span""")[0]

    # Define a pause time in between scrolls
    pause_time = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Record the starting time
    start = datetime.datetime.now()

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # wait to load page
        time.sleep(pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # which means end of page
            break
        # update the last height
        last_height = new_height

    # Record the end time, then calculate and print the total time
    end = datetime.datetime.now()
    delta = end - start
    print("\t[INFO] Total time taken to scroll till the end {}".format(delta))

    # Extract all anchor tags
    link_tags = driver.find_elements_by_tag_name('img')

    # print(link_tags)
    # Create an emply list to hold all the urls for the images
    imgs = []

    # Extract the urls of only the images from each of the tag WebElements
    for tag in link_tags:
        imgs.append(tag.get_attribute('src'))
        if "sm-tile-content" not in tag.get_attribute('class'):
            continue

    # create the root data directory
    if not os.path.exists(root_data):
        try:
            os.mkdir(root_data)
        except OSError:
            print("\t[INFO] Creation of the directory {} failed".format(os.path.abspath(root_data)))
        else:
            print("\t[INFO] Successfully created the directory {} ".format(os.path.abspath(root_data)))

    # Create the directory after checking if it already exists or not
    dir_name = root_data + show.replace('/', '+')
    if not os.path.exists(dir_name):
        try:
            os.mkdir(dir_name)
        except OSError:
            print("\t[INFO] Creation of the directory {} failed".format(os.path.abspath(dir_name)))
        else:
            print("\t[INFO] Successfully created the directory {} ".format(os.path.abspath(dir_name)))

    # put images from who in its own directory
    for img in tqdm(imgs):
        download(img, dir_name)

    # Write the links to the image pages to a file
    f = open("{}/{}.csv".format(dir_name, show_name + '_' + str(number + 1)), 'w')
    f.write(",\n".join(imgs))
    printm("\t[INFO] Successfully created the file {}.csv with {} links".format(show_name, len(imgs)),color='blue',switch=True)

    return imgs


def download(url, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`

    :param url: <str> path to the location of images to download

    :return pathname: <str> directory in which to put the downloaded image
    """

    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)

    # download the body of response by chunk, not immediately
    try:
        response = requests.get(url, stream=True)

        # get the total file size
        file_size = int(response.headers.get("Content-Length", 0))

        # get the file name
        filename = os.path.join(pathname, url.split("/")[-1])

        # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
        # progress = tqdm(response.iter_content(64), f"\tDownloading {filename}", total=file_size, unit="B",
        #                 unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:

            for data in response.iter_content(64):
                # write data read to the file
                f.write(data)
                # update the progress bar manually
                # progress.update(len(data))

    except requests.exceptions.InvalidSchema as ae:
        # logging.info('No connection adapters were found.')
        # logging.error(ae)
        pass

    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError, MaxRetryError) as be:
        logging.info('BANNED EXCEPTION in __MAIN__')
        logging.info(be)
        logging.info('Lets change our PUBLIC IP GUYS!')
        change_ip()
        print('\t\tSleeping after ip change for 1 hour.')
        time.sleep(3600)

    except Exception as ce:
        logging.error('Exception raised.')
        logging.error(ce)


def get_all_show_images(url, gender):
    """
    A function to crawl FirstView runway fashion show archive and save all thumbnails to disk
    for use in ML applications

    :param url: <str> homepage of FirstView
    :param gender: <str> "Mens" or "Womens" are the only valid inputs

    :return None: however, saves all images to disk
    """

    # print validity of url provided
    out = 'URL validity [bool] : '+str(is_valid(url))+str('\n')
    printm(out, color='green', switch=False)

    # Define Chrome options to open the window in maximized mode
    options = webdriver.ChromeOptions()

    # options.add_argument("--start-maximized")
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    link = driver.find_element_by_link_text('Browse ' + gender + ' Collections by Date')
    link.click()

    # convert page root to soup
    soup_show = bs(requests.get(driver.current_url).content, "html.parser")

    # find max number of pages in the men's collection
    pages = int(soup_show.find("div", {"id": "cd_results"}).getText().split(' - ')[1].split(' page')[0])

    N_mens_total = 0
    for page in range(pages + 1):

        #maybe avoid max HTTP requests
        # print(page%20)
        # if page > 10 and page % 40 == 0:
        #     print('\t\tSleeping after a page multiple of 40 for an hour.')
        #     time.sleep(3600)

        out = '\nGetting runway shows from Page '+str(page + 1)
        printm(out, color='green', switch=True)
        if page > 0:
            try:
                link = driver.find_element_by_link_text(str(page + 1))
                link.click()
                # find designer/show name
                soup_show = bs(requests.get(driver.current_url).content, "html.parser")
            except NoSuchElementException:
                link = driver.find_element_by_link_text('more pages...')
                link.click()

        shows = soup_show.find_all('h3')
        shows = [item.getText() for item in shows if ' - ' in item.getText()]

        root_data = 'data/'
        for i, show in enumerate(shows):
            if os.path.isdir(root_data+show.replace('/','+')):
                # this block is here because, unfortunately, runway shows that contain a lot of images
                # are carried onto new pages under the same name. logic could be added to take this into
                # account, but there are already a sufficient number of images to start
                continue
            try:
                print('\n\tGetting links for ', show)
                link = driver.find_element_by_link_text(show)
                link.click()
                imgs = get_links(driver.current_url, show, i, root_data)
                n_imgs = len(imgs)
                N_mens_total += n_imgs
                driver.back()
            except NoSuchElementException:
                pass

    print('Downloaded ', N_mens_total, """ images from men's runway shows.""")

    return


if __name__ == '__main__':

    get_all_show_images(home_page, 'Mens')
    # get_all_show_images(home_page, 'Womens')

    # rotate_proxy()
