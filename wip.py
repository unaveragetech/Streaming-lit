from bs4 import BeautifulSoup
import requests
import webbrowser
import time
import os
import random
from datetime import datetime, timedelta

# Helper function to clear the CLI screen (optional)
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Fetch the page content
def fetch_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Search cameras by a term entered by the user
def search_cameras(base_url, search_term):
    search_url = base_url  # The search is performed on the same page
    payload = {
        'ctl02$tbSearchbox': search_term,
        'ctl02$btnCamSearch': 'Search'
    }
    response = requests.post(search_url, data=payload)  # Perform a POST request to search
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Let the user select a camera category
def select_category(soup):
    camera_categories = soup.find('ul', {'class': 'dropdown-menu-catagory'})
    if camera_categories:
        categories = camera_categories.find_all('li', {'class': 'catagorylist-item'})
        category_dict = {}
        for index, category in enumerate(categories):
            category_name = category.text.strip()
            category_link = category.find('a').get('href')
            category_dict[index] = (category_name, category_link)
            print(f"{index}: {category_name}")
        
        selected_index = int(input("Enter the number of the category you want to select: "))
        selected_category = category_dict[selected_index]
        print(f"Selected category: {selected_category[0]}")
        return selected_category[1]

# Navigate pages and get camera links
def get_cameras_on_page(soup):
    camera_list = []
    cameras = soup.find_all('li', {'class': 'camItem'})
    for camera in cameras:
        camera_title = camera.get('title')
        camera_link = camera.find('a').get('href')
        camera_list.append((camera_title, camera_link))
    return camera_list

# Open cameras in the browser
def view_cameras(cameras):
    for index, (title, link) in enumerate(cameras):
        print(f"\nViewing {title} - {link}")
        webbrowser.open(link)
        input(f"Press Enter to view the next camera (or type 'exit' to quit)...")
        if input() == 'exit':
            break
        clear_screen()

# Pagination handling
def select_page(soup):
    pagination = soup.find('select', {'class': 'droppage'})
    if pagination:
        pages = pagination.find_all('option')
        page_dict = {}
        for page in pages:
            page_number = page.get('value')
            page_dict[int(page_number)] = page_number
            print(f"Page {page_number}/{len(pages)}")

        selected_page = int(input("Enter the page number to navigate: "))
        return selected_page

# Generate camera URL with user input date and time
def generate_camera_url(camera, start_datetime):
    base_url = "https://www.cameraftp.com/camera/CameraPlayerMultiHours.htm"
    
    # Check the format of camera[1] before trying to split it
    try:
        # Adjust the extraction based on the expected URL structure
        parts = camera[1].split('/')
        if len(parts) < 6:  # Make sure there are enough parts
            raise ValueError(f"Camera URL format error: {camera[1]}")

        camera_id = parts[4].replace('parentID', '')  # Extract cameraID
        share_id = parts[5].replace('shareID', '')    # Extract shareID
        name = camera[0]
        
        url = f"{base_url}?cameraID={camera_id}&name={name}&shareID={share_id}&start={start_datetime}"
        return url

    except Exception as e:
        print(f"Error generating camera URL for {camera}: {e}")
        return None  # Return None or handle the error as needed

# Helper function to get a numbered list of dates for user selection
def get_date_selection():
    today = datetime.now()
    two_weeks_ago = today - timedelta(days=14)

    date_list = []
    for i in range(15):  # 0 to 14 for a total of 15 days
        date = two_weeks_ago + timedelta(days=i)
        date_list.append(date.strftime("%Y-%m-%d"))
        print(f"{i}: {date.strftime('%Y-%m-%d')}")

    selected_index = input("Select the number corresponding to the date you want to use (default is today): ")
    if selected_index.strip() == '':  # Default to today's date if no input is given
        selected_date = today.strftime("%Y-%m-%d")
    else:
        selected_index = int(selected_index)
        selected_date = date_list[selected_index]

    return selected_date

# Function to generate a random time in HH:MM:SS format
def generate_random_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02}:{minute:02}:{second:02}"

# Main program flow
def main():
    base_url = "https://www.cameraftp.com/cameraftp/publish/publishedcameras.aspx"  # Replace with the website's base URL
    soup = fetch_page(base_url)

    # Search for cameras
    search_term = input("Enter the camera name you want to search for: ")
    soup = search_cameras(base_url, search_term)  # Call the search function

    # Select a category
    category_link = select_category(soup)
    if category_link:
        full_category_url = f"{base_url}{category_link}"
        soup = fetch_page(full_category_url)

    # Navigate to a specific page
    selected_page = select_page(soup)
    if selected_page:
        page_url = f"{base_url}?page={selected_page}"
        soup = fetch_page(page_url)

    # Get cameras on the current page
    cameras = get_cameras_on_page(soup)

    # Print found cameras for debugging
    print("Cameras found:")
    for camera in cameras:
        print(camera)

    # Get user-selected date from the past two weeks
    selected_date = get_date_selection()

    # Prompt for time input
    start_time = input("Enter start time (HH:MM:SS) or press Enter for a random time: ")
    if not start_time.strip():  # If no time is provided, generate a random time
        start_time = generate_random_time()

    start_datetime = f"{selected_date} {start_time}"

    # Check if the date and time format is valid
    try:
        datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print("Invalid date or time format. Please use YYYY-MM-DD and HH:MM:SS format.")
        return
    
    # Generate and display camera URLs
    for camera in cameras:
        cam_url = generate_camera_url(camera, start_datetime)
        if cam_url:  # Only print if the URL was generated successfully
            print(f"Generated Camera URL: {cam_url}")
    
    # View cameras
    view_cameras(cameras)

if __name__ == "__main__":
    main()
