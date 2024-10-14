from bs4 import BeautifulSoup
import requests
import webbrowser
import time
import os
from datetime import datetime

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
    camera_id = camera[1].split('=')[1]  # Assuming link format contains cameraID
    share_id = camera[1].split('&')[1].split('=')[1]  # Assuming shareID follows the cameraID
    name = camera[0]
    url = f"{base_url}?cameraID={camera_id}&name={name}&shareID={share_id}&start={start_datetime}"
    return url

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
    
    # Prompt for date range
    start_date = input("Enter start date (YYYY-MM-DD): ")
    start_time = input("Enter start time (HH:MM:SS): ")
    start_datetime = f"{start_date} {start_time}"

    # Check if the date and time format is valid
    try:
        datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print("Invalid date or time format. Please use YYYY-MM-DD and HH:MM:SS format.")
        return
    
    # Generate and display camera URLs
    for camera in cameras:
        cam_url = generate_camera_url(camera, start_datetime)
        print(f"Generated Camera URL: {cam_url}")
    
    # View cameras
    view_cameras(cameras)

if __name__ == "__main__":
    main()
