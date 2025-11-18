from robocorp.tasks import task
from RPA.Excel.Files import Files
from RPA.Browser.Selenium import Selenium
import sqlite3
import re
from time import sleep
import os

# Database folder configuration
DB_FOLDER = "movie_databases"

@task
def task():
    input_data = asking_user()
    print(input_data)
    
    if input_data[0] == "1":
        # Single movie search
        process_single_movie(input_data[1])
    elif input_data[0] == "2":
        # Excel file processing
        process_excel_file(input_data[1])
    elif input_data[0] == "0":
        print("Exiting...")
        return

def asking_user():
    print("Welcome to Movie Finder")
    num = input(" Enter 1: for input movie name and find \n Enter 2: for excel file list to find movie \n Enter 0: for exit \n")
    try:
        int(num)
    except ValueError:
        print("Invalid input. Please enter a number (0, 1, or 2).\n")
        return asking_user()
    
    if num == "1":
        movie = str(input("Enter movie name: "))
        return (num, movie)
    elif num == "2":
        file = str(input("Enter file name (with path): "))
        return (num, file)
    elif num == "0":
        print("=======System Close========")
        return (num, "")
    else:
        print("Enter right number")
        return asking_user()

def get_database_name(movie_name):
    """Create database filename from movie name"""
    # Remove special characters and replace spaces with underscores
    clean_name = re.sub(r'[^\w\s-]', '', movie_name)
    clean_name = clean_name.strip().replace(' ', '_').lower()
    
    # Create database folder if not exists
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"Created database folder: {DB_FOLDER}")
    
    db_path = os.path.join(DB_FOLDER, f"{clean_name}.db")
    return db_path

def create_database_if_not_exists(db_path):
    """Create SQLite database table if it doesn't exist"""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT NOT NULL,
            tomatometer_score TEXT,
            audience_score TEXT,
            storyline TEXT,
            rating TEXT,
            genres TEXT,
            review_1 TEXT,
            review_2 TEXT,
            review_3 TEXT,
            review_4 TEXT,
            review_5 TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print(f"Database created/verified: {db_path}")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def insert_movie_data(db_path, movie_data):
    """Insert movie data into SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        insert_query = """
        INSERT INTO movies (
            movie_name, tomatometer_score, audience_score, storyline, 
            rating, genres, review_1, review_2, review_3, review_4, review_5, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cur.execute(insert_query, (
            movie_data.get('movie_name', ''),
            movie_data.get('tomatometer_score', ''),
            movie_data.get('audience_score', ''),
            movie_data.get('storyline', ''),
            movie_data.get('rating', ''),
            movie_data.get('genres', ''),
            movie_data.get('review_1', ''),
            movie_data.get('review_2', ''),
            movie_data.get('review_3', ''),
            movie_data.get('review_4', ''),
            movie_data.get('review_5', ''),
            movie_data.get('status', '')
        ))
        
        conn.commit()
        print(f"Data inserted successfully for {movie_data.get('movie_name')}")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting data: {e}")
        return False

def process_single_movie(movie_name):
    """Process a single movie search"""
    print(f"\n========== Searching for movie: {movie_name} ==========")
    
    # Get database path for this movie
    db_path = get_database_name(movie_name)
    
    # Create database if not exists
    create_database_if_not_exists(db_path)
    
    browser = Selenium()
    try:
        # Search and extract movie data
        movie_data = search_and_extract_movie(browser, movie_name)
        
        # Insert into database
        insert_movie_data(db_path, movie_data)
        
        print(f"========== Completed processing: {movie_name} ==========")
        print(f"Data saved to: {db_path}\n")
        
    except Exception as e:
        print(f"Error processing movie: {e}")
    finally:
        browser.close_browser()

def process_excel_file(file_name):
    """Process movies from Excel file"""
    print(f"\n========== Processing Excel file: {file_name} ==========")
    
    excel = Files()
    browser = Selenium()
    
    try:
        # Open Excel file
        excel.open_workbook(file_name)
        
        # Read movie names from worksheet
        rows = excel.read_worksheet_as_table(header=True)
        
        print(f"Found {len(rows)} movies to process\n")
        
        for idx, row in enumerate(rows, 1):
            # Get movie name from 'Movie' column or first column
            movie_name = row.get('Movie') or row.get('movie') or row.get('Movie Name') or list(row.values())[0]
            
            if movie_name and str(movie_name).strip():
                print(f"\n[{idx}/{len(rows)}] Processing: {movie_name}")
                
                # Get database path for this movie
                db_path = get_database_name(str(movie_name).strip())
                
                # Create database if not exists
                create_database_if_not_exists(db_path)
                
                try:
                    movie_data = search_and_extract_movie(browser, str(movie_name).strip())
                    insert_movie_data(db_path, movie_data)
                    print(f"Data saved to: {db_path}")
                except Exception as e:
                    print(f"Error processing {movie_name}: {e}")
                    # Insert error record
                    error_data = {
                        'movie_name': movie_name,
                        'status': f'Error: {str(e)}'
                    }
                    insert_movie_data(db_path, error_data)
        
        excel.close_workbook()
        print(f"\n========== Completed processing Excel file ==========\n")
        
    except Exception as e:
        print(f"Error processing Excel file: {e}")
    finally:
        browser.close_browser()

def search_and_extract_movie(browser, movie_name):
    """Search for movie on Rotten Tomatoes and extract data"""
    
    # Open Rotten Tomatoes
    browser.open_available_browser("https://www.rottentomatoes.com/")
    browser.maximize_browser_window()
    sleep(2)
    
    try:
        # Click search icon
        browser.wait_until_element_is_visible("css:search-algolia", timeout=10)
        browser.click_element("css:search-algolia button")
        sleep(1)
        
        # Input search query
        browser.wait_until_element_is_visible("css:search-algolia input[data-qa='search-input']", timeout=5)
        browser.input_text("css:search-algolia input[data-qa='search-input']", movie_name)
        sleep(2)
        browser.press_keys("css:search-algolia input[data-qa='search-input']", "ENTER")
        sleep(3)
        
    except Exception as e:
        print(f"Search input error: {e}")
    
    # Find exact match
    movie_url = find_exact_match(browser, movie_name)
    
    if not movie_url:
        print(f"No exact match found for {movie_name}")
        return {
            'movie_name': movie_name,
            'status': 'No exact match found'
        }
    
    # Navigate to movie page
    browser.go_to(movie_url)
    sleep(3)
    
    # Extract data
    movie_data = extract_movie_details(browser, movie_name)
    movie_data['status'] = 'Success'
    
    return movie_data

def find_exact_match(browser, movie_name):
    """Find exact match for movie name (case insensitive)"""
    try:
        sleep(2)
        # Get all search results
        results = browser.find_elements("css:search-page-media-row")
        
        if not results:
            print("No search results found")
            return None
        
        matches = []
        
        for result in results:
            try:
                # Get the HTML to check media type
                html_content = result.get_attribute('innerHTML')
                
                # Skip if it's not a movie (TV shows, etc.)
                if 'tv' in html_content.lower() and 'movie' not in html_content.lower():
                    continue
                
                # Get movie title
                title_element = browser.find_element("css:a[data-qa='info-name']", parent=result)
                title = title_element.text.strip()
                
                # Remove extra whitespaces and compare (case insensitive)
                clean_title = ' '.join(title.split())
                clean_search = ' '.join(movie_name.split())
                
                if clean_title.lower() == clean_search.lower():
                    # Get year
                    year = 0
                    try:
                        year_element = browser.find_element("css:span[data-qa='info-year']", parent=result)
                        year_text = year_element.text
                        year_match = re.search(r'\d{4}', year_text)
                        if year_match:
                            year = int(year_match.group())
                    except:
                        pass
                    
                    url = title_element.get_attribute("href")
                    matches.append({
                        'title': title,
                        'year': year,
                        'url': url
                    })
                    print(f"Found exact match: {title} ({year})")
            except Exception as e:
                continue
        
        if not matches:
            print("No exact matches found in results")
            return None
        
        # Sort by year (most recent first) and return URL
        matches.sort(key=lambda x: x['year'], reverse=True)
        print(f"Selected movie: {matches[0]['title']} ({matches[0]['year']})")
        return matches[0]['url']
        
    except Exception as e:
        print(f"Error finding exact match: {e}")
        return None

def extract_movie_details(browser, movie_name):
    """Extract movie details from Rotten Tomatoes movie page"""
    movie_data = {'movie_name': movie_name}
    
    try:
        # Wait for page to load
        browser.wait_until_element_is_visible("css:score-board", timeout=10)
        
        # Extract Tomatometer Score
        try:
            tomatometer = browser.find_element("css:rt-button[slot='criticsScore'] rt-text").text
            movie_data['tomatometer_score'] = tomatometer.strip().replace('%', '') + '%'
        except:
            try:
                tomatometer = browser.find_element("css:score-board").get_attribute('tomatometerscore')
                movie_data['tomatometer_score'] = tomatometer + '%' if tomatometer else 'N/A'
            except:
                movie_data['tomatometer_score'] = 'N/A'
        
        # Extract Audience Score
        try:
            audience = browser.find_element("css:rt-button[slot='audienceScore'] rt-text").text
            movie_data['audience_score'] = audience.strip().replace('%', '') + '%'
        except:
            try:
                audience = browser.find_element("css:score-board").get_attribute('audiencescore')
                movie_data['audience_score'] = audience + '%' if audience else 'N/A'
            except:
                movie_data['audience_score'] = 'N/A'
        
        # Extract Storyline/Synopsis
        try:
            storyline_elem = browser.find_element("css:drawer-more[data-qa='movie-info-synopsis'] rt-text")
            storyline = storyline_elem.text
            movie_data['storyline'] = storyline.strip() if storyline else 'N/A'
        except:
            try:
                storyline_elem = browser.find_element("css:p[data-qa='movie-info-synopsis']")
                movie_data['storyline'] = storyline_elem.text.strip()
            except:
                movie_data['storyline'] = 'N/A'
        
        # Extract Rating
        try:
            rating_elem = browser.find_element("css:rt-text[slot='rating']")
            movie_data['rating'] = rating_elem.text.strip()
        except:
            try:
                rating_elem = browser.find_element("css:div[data-qa='rating']")
                movie_data['rating'] = rating_elem.text.strip()
            except:
                movie_data['rating'] = 'N/A'
        
        # Extract Genres
        try:
            genre_elements = browser.find_elements("css:rt-text[slot='genre']")
            if genre_elements:
                genres = ', '.join([g.text.strip() for g in genre_elements if g.text.strip()])
                movie_data['genres'] = genres if genres else 'N/A'
            else:
                genre_elements = browser.find_elements("css:span[data-qa='genre']")
                genres = ', '.join([g.text.strip() for g in genre_elements if g.text.strip()])
                movie_data['genres'] = genres if genres else 'N/A'
        except:
            movie_data['genres'] = 'N/A'
        
        # Scroll to reviews section
        try:
            browser.execute_javascript("window.scrollTo(0, document.body.scrollHeight/2);")
            sleep(2)
        except:
            pass
        
        # Extract Top 5 Critic Reviews
        try:
            # Try different selectors for reviews
            review_elements = browser.find_elements("css:p.review-text")
            
            if not review_elements:
                review_elements = browser.find_elements("css:drawer-more[data-qa='review-text'] rt-text")
            
            if not review_elements:
                review_elements = browser.find_elements("css:critic-review p")
            
            review_count = min(5, len(review_elements))
            
            for i in range(review_count):
                review_text = review_elements[i].text.strip()
                movie_data[f'review_{i+1}'] = review_text if review_text else ''
            
            # Fill remaining reviews with empty string
            for i in range(review_count, 5):
                movie_data[f'review_{i+1}'] = ''
                
        except Exception as e:
            print(f"Error extracting reviews: {e}")
            for i in range(1, 6):
                movie_data[f'review_{i}'] = ''
        
        print(f"Extracted data - Tomatometer: {movie_data['tomatometer_score']}, Audience: {movie_data['audience_score']}")
        
    except Exception as e:
        print(f"Error extracting movie details: {e}")
    
    return movie_data

def view_all_databases():
    """View all movie databases created"""
    if not os.path.exists(DB_FOLDER):
        print("No databases found")
        return
    
    db_files = [f for f in os.listdir(DB_FOLDER) if f.endswith('.db')]
    
    if not db_files:
        print("No databases found")
        return
    
    print(f"\n========== Total {len(db_files)} Movie Databases ==========")
    for idx, db_file in enumerate(db_files, 1):
        print(f"{idx}. {db_file}")
    print("=" * 50)

def view_movie_database_data(movie_name):
    """View data from specific movie database"""
    db_path = get_database_name(movie_name)
    
    if not os.path.exists(db_path):
        print(f"Database not found for: {movie_name}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM movies ORDER BY created_at DESC")
        rows = cur.fetchall()
        
        if not rows:
            print("No data found in database")
            return
        
        print(f"\n========== Data for: {movie_name} ==========")
        for row in rows:
            print(f"\nID: {row['id']}")
            print(f"Movie Name: {row['movie_name']}")
            print(f"Tomatometer Score: {row['tomatometer_score']}")
            print(f"Audience Score: {row['audience_score']}")
            print(f"Storyline: {row['storyline'][:100]}..." if row['storyline'] and len(row['storyline']) > 100 else f"Storyline: {row['storyline']}")
            print(f"Rating: {row['rating']}")
            print(f"Genres: {row['genres']}")
            print(f"Review 1: {row['review_1'][:80]}..." if row['review_1'] and len(row['review_1']) > 80 else f"Review 1: {row['review_1']}")
            print(f"Status: {row['status']}")
            print(f"Created At: {row['created_at']}")
            print("-" * 50)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error reading database: {e}")