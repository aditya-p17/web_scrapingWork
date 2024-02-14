# Importing necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Setting up the Selenium web driver
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Opening the webpage
driver.get("https://hprera.nic.in/PublicDashboard")

# Waiting for the "View Application" links to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="View Application"]')))

# Fetching the first five links from the page
a_tags = driver.find_elements(By.CSS_SELECTOR, '[title="View Application"]')
texts_of_a_tags = [a_tag.text for a_tag in a_tags]

# Removing unwanted text from the list
texts_of_a_tags = [text for text in texts_of_a_tags if text != 'Previous Detail >>' and text != '']
a_five = texts_of_a_tags[:5]

def get_details(address):
    """
    Retrieves details from a webpage based on the given address.

    Args:
        address (str): The address to search for on the webpage.

    Returns:
        list: A list containing the retrieved details.
    """
    output_dict = []

    # Clicking on the link for the given address
    link_locator = (By.PARTIAL_LINK_TEXT, address)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(link_locator))
    link = driver.find_element(*link_locator)
    link.click()

    # Waiting for the details to load
    element_locator = (By.CSS_SELECTOR, "td.fw-600")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(element_locator))

    # Retrieving the details
    tr_elements = driver.find_element(*element_locator)
    output_dict.append(tr_elements.text)

    # Retrieving additional details
    element_locator2 = (By.CSS_SELECTOR, "span.fw-600")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(element_locator2))
    tr_elements2 = driver.find_elements(*element_locator2)
    tr_elements2 = tr_elements2[-7:]

    # Appending the additional details to the output dictionary
    for i in range(len(tr_elements2)):
        if tr_elements2[i].text == "":
            output_dict.append("N/A")
        else:
            output_dict.append(tr_elements2[i].text)

    # Closing the details popup
    button = driver.find_element(By.CLASS_NAME, "close")
    button.click()
    time.sleep(5)

    return output_dict

# Retrieving details for all five addresses
all_files = [get_details(i) for i in a_five]

# Removing "Yes" from the retrieved details
for i in all_files:
    if "Yes" in i:
        i.remove("Yes")

# Quitting the web driver
driver.quit()

# Creating a list of dictionaries with the required details
#Here we can verify the pan number and GSTIN number for its validity but for now I am just checking if it is present or not (using regex)
result_list = [
    {
        "Name": entry[0],
        "Permanent Address": entry[-1],
        "PAN No": next((item for item in entry if item.isalnum() and len(item) == 10), 'N/A'),
        "GSTIN No": next((item for item in entry if item.isalnum() and len(item) == 15), 'N/A')
    }
    for entry in all_files
]

# Creating a dataframe from the list of dictionaries
df = pd.DataFrame(result_list)

# Printing the dataframe
print(df)
