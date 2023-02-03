## Importing Libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from bs4 import BeautifulSoup
import os
import requests
import pandas as pd
import urllib.request
import streamlit as st
from PIL import Image
import numpy as np

# create object for chrome options
chrome_options = Options()
chrome_options.add_argument("disable-notifications")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("start-maximized")
# To disable the message, “Chrome is being controlled by automated test software”
chrome_options.add_argument("disable-infobars")
# Pass the argument 1 to allow and 2 to block
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 2
})

#################### Streamlit ####################
st.set_page_config(layout="wide")
st.sidebar.title("Choose Parameters")
config_select_ecommerce = st.sidebar.multiselect(
    "Select one or more ecommerce for price comparison:", ["All", "Shopee Mall", "LazMall"])
if "All" in config_select_ecommerce:
    config_select_ecommerce = ["Shopee Mall", "LazMall"]
config_search_method = st.sidebar.radio(
    "Select search method:", ["By name of the item", "By url"], 0)
if config_search_method == "By name of the item":
    config_input_value = st.sidebar.text_input(
        "Please type in the item you want to do a price comparison", "Tineco")
else:
    for ecommerce in config_select_ecommerce:
        if "Shopee" in ecommerce:
            config_url_shopee = st.sidebar.text_input("Please type in the url for Shopee Mall")
        if "LazMall" in ecommerce:
            config_url_lazmall = st.sidebar.text_input("Please type in the url for LazMall")

#################### Actual code ####################
def load_image(img):
    im = Image.open(img)
    image = np.array(im)
    return image

st.image(load_image(os.getcwd() + "\Streamlit.jpg"))
