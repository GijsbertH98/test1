st.set_page_config(layout=”wide”)
st.sidebar.title(“Choose Parameters”)
config_select_ecommerce = st.sidebar.multiselect(“Select one or more ecommerce for price comparison:”, [“All”, “Shopee Mall”, “LazMall”])
if “All” in config_select_ecommerce:
 config_select_ecommerce = [“Shopee Mall”, “LazMall”]
config_search_method = st.sidebar.radio(“Select search method:”, [“By name of the item”,”By url”], 0)
if config_search_method == “By name of the item”:
 config_input_value = st.sidebar.text_input(“Please type in the item you want to do a price comparison”, “Tineco”)
else:
 for ecommerce in config_select_ecommerce:
 if “Shopee” in ecommerce:
 config_url_shopee = st.sidebar.text_input(“Please type in the url for Shopee Mall”)
 if “LazMall” in ecommerce:
 config_url_lazmall = st.sidebar.text_input(“Please type in the url for LazMall”)
