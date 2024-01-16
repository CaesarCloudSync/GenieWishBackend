import unittest
import requests
CONTRIBUTOR_ID = "d85a0ef68da0a2afa659725d0bece0645598576ac33c4a2cacf2437f2b91e031"
PASSWORD = "kya63amari"
MAGENT_URI = r"magnet:?xt=urn:btih:2457c0c838d036ffd17b6bbb827c71d7c0b79d83&dn=Tubi(1)(4).csv&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=udp%3A%2F%2Fexplodie.org%3A6969&tr=udp%3A%2F%2Ftracker.empire-js.us%3A1337&tr=wss%3A%2F%2Ftracker.btorrent.xyz&tr=wss%3A%2F%2Ftracker.openwebtorrent.com"
class StoreTest(unittest.TestCase):
    def store_test(self):
        response = requests.post("http://127.0.0.1:5000/contributorsignin",json={"contributorid": CONTRIBUTOR_ID,"password": PASSWORD})
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        json = {"quotaurl":"CaesarAI/CaesarAI/AIAssistant","quotamagneturi":MAGENT_URI,"torrentfilename":"Tubi(1)(4).csv","filesize":4024}
        response = requests.post("http://127.0.0.1:5000/storemagneturi",json=json,headers=headers)
        print(response.json())

    def get_test(self):
        response = requests.post("http://127.0.0.1:5000/quotapostersignin",json={"company": "CaesarAI","email":"amari.lawal@gmail.com","password": PASSWORD})
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        json = {"quotaurl":"CaesarAI/CaesarAI/AIAssistant","contributor":"palondomus","torrentfilename":"Tubi(1)(4).csv"}
        response = requests.post("http://127.0.0.1:5000/getmagneturi",json=json,headers=headers)
        print(response.json())

if __name__ == "__main__":
    unittest.main()