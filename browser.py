from RPA.Browser.Selenium import Selenium
from time import sleep

browser = Selenium()

def search_and_extract_movie(movie_name):
    browser.open_available_browser("https://www.rottentomatoes.com/")
    browser.maximize_browser_window()
    sleep(2)

    try:
        try:
            
             browser.click_element("xpath:/html/body/div[5]/div[2]/div/div[1]/div/div[2]/div/button")
             
        except Exception as e:
            print(e)
        browser.click_element("xpath:/html/body/div[3]/rt-header/search-results-nav/search-results-controls/input")
        sleep(1)

        browser.input_text("xpath:/html/body/div[3]/rt-header/search-results-nav/search-results-controls/input", movie_name)
        browser.press_keys("xpath:/html/body/div[3]/rt-header/search-results-nav/search-results-controls/input", "ENTER")
        sleep(2)

    except Exception as e:
        print("Search error:", e)

    movie_url = find_exact_match(movie_name)

    if not movie_url:
        return {"movie_name": movie_name, "status": "No match"}

    browser.go_to(movie_url)
    sleep(3)

    data = extract_movie_details()
    data["movie_name"] = movie_name
    data["status"] = "Success"

    return data


def find_exact_match(movie_name):
    sleep(2)
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

    try:
        t = browser.find_element('xpath://*[@id="modules-wrap"]/div[1]/media-scorecard/rt-text[1]').text
        movie_data["tomatometer_score"] = t
    except:
        movie_data["tomatometer_score"] = "N/A"

    try:
        a = browser.find_element('xpath://*[@id="modules-wrap"]/div[1]/media-scorecard/rt-text[3]').text
        movie_data["audience_score"] = a
    except:
        movie_data["audience_score"] = "N/A"
    browser.scroll_element_into_view('xpath://*[@id="modules-wrap"]/div[10]/section')
    try:
        storyline = browser.find_element('xpath://*[@id="modules-wrap"]/div[10]/section/div[2]/div/rt-text[2]').text
        movie_data["storyline"] = storyline
    except:
        movie_data["storyline"] = "N/A"

    try:
        genres = browser.find_elements('xpath://*[@id="modules-wrap"]/div[10]/section/div[2]/dl/div[7]/dd')
        movie_data["genres"] = ", ".join([g.text for g in genres])
    except:
        movie_data["genres"] = "N/A"

    try:
        Release_Date = browser.find_element('xpath://*[@id="modules-wrap"]/div[10]/section/div[2]/dl/div[9]/dd/rt-text//span').text
        movie_data["Release Date"] = Release_Date
    except:
        movie_data["Release Date"] = "N/A"
    
    print(f'this is movie type{movie_data}')

    return movie_data
