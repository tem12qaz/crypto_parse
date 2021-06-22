import asyncio
from fake_useragent import UserAgent

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium_stealth import stealth


user_agent = UserAgent()


def get_selen(proxy=False):
    # display = Display(visible=0, size=(640, 480))
    # display.start()

    ua = UserAgent()
    options = webdriver.ChromeOptions()

    if proxy:
        # new_connection()
        options.add_argument('--proxy-server=socks5://localhost:9050')

    options.add_argument("--disable-blink-features")
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("start-maximized")

    driver = webdriver.Chrome(
        # executable_path="/home/ubuntu/code/parse/project_parse/chromedriver",
        executable_path=r"C:\Users\Matvey\Desktop\crypto_parse\chromedriver.exe",
        options=options
    )

    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #     "source": """
    #     Object.defineProperty(navigator, 'webdriver', {
    #       get: () => undefined
    #     })
    #   """
    # })

    # driver.execute_cdp_cmd(
    #    'Network.setUserAgentOverride',
    #    {"userAgent": user_agent.random}
    # )

    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


async def parse(id_, proxy=False):
    driver = get_selen(proxy)
    driver.get(f'https://raydium.io/swap/?ammId={id_}')
    await asyncio.sleep(2)
    driver.find_element_by_class_name('coin-input').find_element_by_tag_name('input').send_keys(1)
    err = 0
    await asyncio.sleep(8)
    while True:
        try:
            price = float(driver.find_element_by_class_name('price-base').text.split('≈ ')[1].split(' ')[0])
        except NoSuchElementException:
            print('x')
            if err == 5:
                price = None
                break
            err += 1
            await asyncio.sleep(2)
        else:
            break
    return price








