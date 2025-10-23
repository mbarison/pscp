import requests, re
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from html import unescape
from datetime import datetime
from time import sleep

def unpack_struct(x):
    # first three rows contain URL, value, date
    header = x.find_all("div", attrs={"class": "row"})

    ptn_ctr_dat = re.compile(r"Contract Date:(.+)$")
    ptn_tot_val = re.compile(r"Total Value:\s+\$(.+)$")
    ptn_ori_val = re.compile(r"Original Value:\s+\$(.+)$")
    
    _dct = {
            #"h0": header[0].text,
            #"h1": header[1].text,
            #"h2": header[2].text
            }

    _dct["url"] = urljoin("https://search.open.canada.ca", header[0].find("a")["href"])
    _dct["vendor"] = header[0].find("a").text.strip()
    _dct["contract_date"] = datetime.strptime(ptn_ctr_dat.findall(header[1].text.replace("\n", ""))[0].strip(), "%b %d, %Y")
    _dct["total_value"] = ptn_tot_val.findall(header[0].text)[0].strip()
    _dct["original_value"] = ptn_ori_val.findall(header[2].text)[0].strip()

    # now unpack the rest
    _dct["description"] = x.find("div", attrs={"aria-labelledby": "org_value_lbl"}).text.strip()
    _dct["instrument_type"] = x.find("div", attrs={"aria-labelledby": "instrument_lbl"}).text.strip()
    _dct["commodity_type"] = x.find("div", attrs={"aria-labelledby": "commodity_lbl"}).text.strip()

    comm_block = x.find("div", attrs={"aria-labelledby": "comments_lbl"})
    if comm_block:
        _dct["comments"] = comm_block.text.strip()

    add_comm_block = x.find("div", attrs={"aria-labelledby": "acomments_lbl"})
    if add_comm_block:
        _dct["comments"] = add_comm_block.text.strip()  

    _dct["organization"] = x.find("div", attrs={"aria-labelledby": "org_lbl"}).text.strip()

    return _dct

def process_url(url):

    print(f"Parsing {url}")

    r = requests.get(url)

    raw_data = []
    next_url = None

    if r.ok:
        #print(r.text)

        bs = BeautifulSoup(r.text, features="html.parser")

        contract_structs = bs.find_all("div", attrs={"class": "row mrgn-bttm-xl mrgn-lft-md"})

        print(f"Found {len(contract_structs)} contracts.")

        for i in contract_structs:
            d = unpack_struct(i)
            print(d)
            raw_data.append(d)

        # check if there is a next url
        n_u = bs.find("li", attrs={"class": "next"})
        if n_u:
            next_url = unescape(n_u.find("a")["href"])

            # last page points to itself, discard
            if "http" not  in next_url:
                next_url = None

    else:
        print(r.status_code)

    return (raw_data, next_url)

def main(first_url):
    print("Hello from pscp!")

    next_url = first_url

    raw_data = []

    while next_url is not None:
        r_d, next_url = process_url(next_url)
        raw_data.extend(r_d)
        sleep(1)

    df = pd.DataFrame(raw_data)

    df.to_parquet("ms_test.parquet", index=False)

if __name__ == "__main__":
    main("https://search.open.canada.ca/contracts/?owner_org=statcan&page=1&sort=contract_date+desc&search_text=microsoft")
