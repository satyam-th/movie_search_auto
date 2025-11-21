from RPA.Browser.Selenium import Selenium
from time import sleep

browser = Selenium()

def search_and_extract_movie(movie_name):
    browser.open_available_browser("https://www.rottentomatoes.com/")
    browser.maximize_browser_window()
    # sleep(2)

    try:
        try:
            
             browser.click_element("xpath:/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/button")
             
        except Exception as e:
            print(e)
        browser.click_element("xpath:/html/body/div[3]/rt-header/search-results-nav/search-results-controls/input")
        # sleep(1)

        browser.input_text("xpath:/html/body/div[3]/rt-header/search-results-nav/search-results-controls/input", movie_name)
        browser.press_keys("xpath:/html/body/div[3]/rt-header/search-results-nav/search-results-controls/input", "ENTER")
        # sleep(2)

    except Exception as e:
        print("Search error:", e)

    movie_url = find_exact_match(movie_name)

    if not movie_url:
        return {"movie_name": movie_name, "status": "No match"}

    browser.go_to(movie_url)
    # sleep(3)

    data = extract_movie_details()
    data["movie_name"] = movie_name
    data["status"] = "Success"

    return data


def find_exact_match(movie_name):
    # sleep(2)
    browser.click_element_if_visible("xpath://div[@id='search-results']/nav[@class='search__nav']/ul[@class='searchNav__filters']/li[@class='js-search-filter searchNav__filter'][1]")
    results = browser.find_elements("xpath://search-page-media-row")
   
    print(f'Number of movie rows found: {len(results)}')
    matches = []
    num = 1
    for result in results:
            
        try:
            title_elem = browser.find_element(f'xpath://*[@id="search-results"]/search-page-result/ul/search-page-media-row[{num}]/a[2]')
            title = title_elem.text.strip()
            print(f'title{title}')
            num = 1+num
            if title.lower() == movie_name.lower():
                matches.append(title_elem.get_attribute("href"))
                print(matches)
        except:
            continue
            
    return matches[0] if matches else None


def extract_movie_details():
    movie_data = {}

    browser.wait_until_element_is_visible("xpath:/html/body")
    test = 1

    while True:
        try:
            browser.find_element( f'xpath://*[@id="modules-wrap"]/div[{test}]/section/div[2]/dl/div')
            print("data found")
            break
        except:
            print(f"testing {test}")
            test = 1 + test
            # print(f"testing {test}")
            continue
    data = browser.find_elements(f'xpath://*[@id="modules-wrap"]/div[{test}]/section/div[2]/dl/div')
    print(f"number of data are {len(data)} and num {test}")
    i = 1
    for a in data:
        try:
            name_xpath = f'xpath://*[@id="modules-wrap"]//section/div[2]/dl/div[{i}]/dt/rt-text'
            detail_xpath = f'xpath://*[@id="modules-wrap"]/div[{test}]/section/div[2]/dl/div[{i}]/dd'

            data_name = browser.find_element(name_xpath).text
            data_detail = browser.find_element(detail_xpath).text

            movie_data[data_name] = data_detail
        except Exception as e:
            print(f"Skipping block {i}: {e}")
            continue
        i = 1 + i
    clean_data = {key: clean_text(value) for key, value in movie_data.items()}
    print(f'this is movie type{clean_data}')

    return clean_data
def clean_text(text):
    # Remove repeated newlines/spaces and normalize commas
    text = text.replace("\n", " ").replace("  ", " ")      # collapse newlines + double spaces
    text = text.replace(" ,", ",")                         # remove space before comma
    text = " ".join(text.split())                          # normalize all whitespace
    return text
