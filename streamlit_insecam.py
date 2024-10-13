import streamlit as st
import requests
import re
from requests.structures import CaseInsensitiveDict
import webbrowser

# IP location service URL
ip_location_url = "http://ip-api.com/json/"

# Set up Streamlit UI
st.title("Insecam Country Viewer")
st.write("Infinidev Team's Cam-Hackers - Interactive IP Address Finder")

# Headers for HTTP requests
headers = CaseInsensitiveDict({
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "www.insecam.org",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
})

url = "http://www.insecam.org/en/jsoncountries/"

# Fetch country data and show in the UI
st.write("Fetching available countries...")

try:
    # Request to get the countries list
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()  # Check for successful response
    data = resp.json()
    countries = data['countries']
    
    country_codes = {value['country']: key for key, value in countries.items()}
    
    # Select box for user to pick a country
    selected_country = st.selectbox("Select a country", list(country_codes.keys()))

    if st.button("Fetch IPs"):
        country_code = country_codes[selected_country]
        res = requests.get(f"http://www.insecam.org/en/bycountry/{country_code}", headers=headers)
        res.raise_for_status()
        
        # Finding the last page
        last_page = re.findall(r'pagenavigator\("\?page=", (\d+)', res.text)
        if last_page:
            last_page = int(last_page[0])
        else:
            st.error("No IPs found for the selected country.")
            st.stop()
        
        # Container to display the IP addresses and validation
        ip_container = st.container()
        ip_list = []
        
        for page in range(last_page):
            res = requests.get(f"http://www.insecam.org/en/bycountry/{country_code}/?page={page}", headers=headers)
            res.raise_for_status()
            find_ip = re.findall(r"http://\d+\.\d+\.\d+\.\d+:\d+", res.text)
            ip_list.extend(find_ip)
            
            # Displaying IPs with validation and location info
            for ip in find_ip:
                st.write(f"IP: {ip}")
                
                # Button to open IP link in a new browser tab
                if st.button(f"Open {ip}", key=ip):
                    webbrowser.open(ip)  # Opens in a new tab
                    
                # Validate if the IP link is active
                try:
                    link_response = requests.get(ip, timeout=5)
                    if link_response.status_code == 200:
                        st.success(f"Link is valid: {ip}")
                    else:
                        st.warning(f"Link returned status code: {link_response.status_code}")
                except requests.RequestException:
                    st.error(f"Failed to connect to: {ip}")
                
                # Fetching location data
                loc_resp = requests.get(ip_location_url + ip.split("//")[1].split(":")[0])
                if loc_resp.status_code == 200:
                    location_data = loc_resp.json()
                    st.write(f"Location: {location_data['city']}, {location_data['country']} ({location_data['lat']}, {location_data['lon']})")
                else:
                    st.warning(f"Location data not found for {ip}")
        
        # Save the found IPs to a file
        file_name = f"{selected_country}_ips.txt"
        with open(file_name, 'w') as f:
            for ip in ip_list:
                f.write(f'{ip}\n')
        
        st.success(f"IP addresses saved to {file_name}")

except requests.exceptions.RequestException as e:
    st.error(f"Error: {e}")
except IndexError:
    st.error("Error: No pages found for the specified country.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
