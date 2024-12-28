import json
from typing import Any
import re
import time
import requests

from main import logger

ACCESS_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIzZjE2M2QxNmQ2MTM0M2I2OTY4MjIwNjFkY2NmNzc5ZiIsImN1c3RvbUpzb24iOiJ7XCJjbGllbnRJZFwiOlwiMjVkelgzdmJZcWt0Vnh5WFwiLFwiZG9tYWluSWRcIjpcImJqMjlcIixcInNjb3BlXCI6W1wiRFJJVkUuQUxMXCIsXCJTSEFSRS5BTExcIixcIkZJTEUuQUxMXCIsXCJVU0VSLkFMTFwiLFwiVklFVy5BTExcIixcIlNUT1JBR0UuQUxMXCIsXCJTVE9SQUdFRklMRS5MSVNUXCIsXCJCQVRDSFwiLFwiT0FVVEguQUxMXCIsXCJJTUFHRS5BTExcIixcIklOVklURS5BTExcIixcIkFDQ09VTlQuQUxMXCIsXCJTWU5DTUFQUElORy5MSVNUXCIsXCJTWU5DTUFQUElORy5ERUxFVEVcIl0sXCJyb2xlXCI6XCJ1c2VyXCIsXCJyZWZcIjpcImh0dHBzOi8vd3d3LmFsaXl1bmRyaXZlLmNvbS9cIixcImRldmljZV9pZFwiOlwiNThmNmQ4NDVhYTc1NDA0NDgxOWJlNzJmMzU3NDY5NzNcIn0iLCJleHAiOjE3MzUzMjE5ODYsImlhdCI6MTczNTMxNDcyNn0.pHQ-Kxpebq9asF8V5OxSSVE19f-UJOM9jE8zCeml2QzoA7iMVCqDDdU2RWand_1_SVGDTvSLzXc8S7G5KQXywEOrApyXTLUy3-rc1bJHBooy5Kloho-FxEQYtkmgTbnpq56RIaEO8cyT-uD2NMNr0CpI5Nooz5PqrWwZfVzb8gI'
# console.log(JSON.parse(localStorage.token).access_token)


def get_header(access_token) -> Any:
    # headers = {
    #     'User-Agent': "AliApp(AYSD/6.7.5) com.alicloud.databox/42464890 Channel/36176727979800@rimet_android_6.7.5 language/zh-CN /Android Mobile/Xiaomi 2109119BC",
    #     'Accept': "application/json",
    #     'Accept-Encoding': "gzip",
    #     'Content-Type': "application/json",
    #     'x-request-id': "41d1a2d9-8c42-4b33-b358-2391acfaa8a7",
    #     'x-device-id': "bf45d088ce3a23c13a8cb14666f848c9d346b0af6010ff2b5714be47d039b75c",
    #     'referer': "https://alipan.com/",
    #     'x-canary': "client=Android,app=adrive,version=v6.7.5",
    #     # 'x-timestamp': '1735315543',
    #     'x-timestamp': str(int(time.time())),
    #     'x-nonce': "40f126d5-ba52-4dc5-a5c4-a63b0812a83d",
    #     'x-signature-v2': "946d5117ace64b3808f8a42f5f98d3af9fb5f276",
    #     'authorization': "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIzZjE2M2QxNmQ2MTM0M2I2OTY4MjIwNjFkY2NmNzc5ZiIsImN1c3RvbUpzb24iOiJ7XCJjbGllbnRJZFwiOlwicEpaSW5OSE4yZFpXazhxZ1wiLFwiZG9tYWluSWRcIjpcImJqMjlcIixcInNjb3BlXCI6W1wiRFJJVkUuQUxMXCIsXCJGSUxFLkFMTFwiLFwiVklFVy5BTExcIixcIlNIQVJFLkFMTFwiLFwiU1RPUkFHRS5BTExcIixcIlNUT1JBR0VGSUxFLkxJU1RcIixcIlVTRVIuQUxMXCIsXCJCQVRDSFwiLFwiQUNDT1VOVC5BTExcIixcIklNQUdFLkFMTFwiLFwiSU5WSVRFLkFMTFwiLFwiU1lOQ01BUFBJTkcuTElTVFwiXSxcInJvbGVcIjpcInVzZXJcIixcInJlZlwiOlwiXCIsXCJkZXZpY2VfaWRcIjpcIjc4MWRkMzFlMmE2NDQxODVhZjJiMTNjNTJhYTA0ZjBkXCJ9IiwiZXhwIjoxNzM1MzE2NDY2LCJpYXQiOjE3MzUzMDkyMDZ9.UDg-5otAb0ndYcRg3QtgS2lK1LBRLMMm8NStfBH9nUc8g1eLqz48eHXjNTGGCDSj8od76H_4DIWcrRr-gwrbjOAf_I1CgHw57Fqi1Tgk30049JntvppEP9Yi1ShMZrv1B8ltN9TtCxMNoxSipiLCDHJfaaRIudToYPXZiza_ot4",
    #     'x-sign': "azRr1P002xAAIZUhIvfgTIix1r3GsZUhlSGVIZdzdtGVyaU2TDUm5OsyJQjVqeGhaHs4rN3pjzlWU1FdxRjRRkcWQzGVMZUhlTGVIZ",
    #     'x-mini-wua': "a7wQvQtlHqpBvh47d21rDza4Sqdas5nQkDMQ0ftLuNtEOzECRIqZcm2duOUWWPbW7Q9sSC0KEkT6FWoJQpiRc9z3k8hpcJMGxmu8Tz811Ro5MS3jywThsWzjdOWHC%2F52rZo4SVL%2Fv0KWsTw7J9dpEGNNyFVnLpKC6ZAcqsAKz6%2Bvr6w%3D%3D",
    #     'x-umt': "DoMBfZFLPFfhOwKUCIdID9Wq2NSMgaGM",
    #     'x-sgext': "JBL3OWvC5ekfk4Y%2FCu8LODnGCcUBwRrGDcABwxrCDtQaxg7EDMQIwgvGCdQJxFqWCccJxwiVAZRckl%2FAGsYawRrPDdQJxwnCGsQaxhrGGsYaxhrGGsYaxxrDGsUaxxrHGscaxxrHGscaxxrUXNQJ1AnUDsBYzwnHGscJxwnHGscaxV2WGsca1ArUAdQK1ArUQ7RQnBrHGtcZ1wnXGdcJ",
    #     'x-bx-version': "6.6.240404",
    #     'x-host': "198.18.0.67",
    #     'Cookie': "munb=2211197091650; _nk_=t-2211197091650-52; cookie2=14fed731d00892b840b086409123352b; csg=bd15dfd5; t=97756c615ff797cf2e00123c48ddd31b; _tb_token_=51b6933ff31ed"
    # }


    headers = {
        'User-Agent': "AliApp(AYSD/6.7.5) com.alicloud.databox/37029260 Channel/36176727979800@rimet_android_6.7.5 language/zh-CN /Android Mobile/Xiaomi 2109119BC",
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'x-canary': "client=Android,app=adrive,version=v6.7.5",
        # 'x-request-id': "d245b858-9636-4a58-a7e8-53d993d2fa94",
        # 'x-device-id': "bf45d088ce3a23c13a8cb14666f848c9d346b0af6010ff2b5714be47d039b75c",
        # 'x-signature': "160028d1fd87f70524b84b3b2a54b523dd51ebf7511f1495540c1c79e54fbfc7037096be2874171ce2ee0da7badad38210a2f6cea5175f6ae0aab74f5e94aa9401",
        'referer': "https://alipan.com/",
        # 'x-timestamp': "1735309748",
        # 'x-nonce': "739b25b9-7ec7-4e55-8b08-5abfc52b95c4",
        # 'x-signature-v2': "efcea0fa6dc83da61418f66b78066f13154fa061",
        'authorization': "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIzZjE2M2QxNmQ2MTM0M2I2OTY4MjIwNjFkY2NmNzc5ZiIsImN1c3RvbUpzb24iOiJ7XCJjbGllbnRJZFwiOlwicEpaSW5OSE4yZFpXazhxZ1wiLFwiZG9tYWluSWRcIjpcImJqMjlcIixcInNjb3BlXCI6W1wiRFJJVkUuQUxMXCIsXCJGSUxFLkFMTFwiLFwiVklFVy5BTExcIixcIlNIQVJFLkFMTFwiLFwiU1RPUkFHRS5BTExcIixcIlNUT1JBR0VGSUxFLkxJU1RcIixcIlVTRVIuQUxMXCIsXCJCQVRDSFwiLFwiQUNDT1VOVC5BTExcIixcIklNQUdFLkFMTFwiLFwiSU5WSVRFLkFMTFwiLFwiU1lOQ01BUFBJTkcuTElTVFwiXSxcInJvbGVcIjpcInVzZXJcIixcInJlZlwiOlwiXCIsXCJkZXZpY2VfaWRcIjpcIjc4MWRkMzFlMmE2NDQxODVhZjJiMTNjNTJhYTA0ZjBkXCJ9IiwiZXhwIjoxNzM1MzE2NDY2LCJpYXQiOjE3MzUzMDkyMDZ9.UDg-5otAb0ndYcRg3QtgS2lK1LBRLMMm8NStfBH9nUc8g1eLqz48eHXjNTGGCDSj8od76H_4DIWcrRr-gwrbjOAf_I1CgHw57Fqi1Tgk30049JntvppEP9Yi1ShMZrv1B8ltN9TtCxMNoxSipiLCDHJfaaRIudToYPXZiza_ot4",
        # 'authorization': access_token,
        # E3NTZjNDNkMTAyZjQ1ZDQ5MDViZTljZGE4MDhlYjI2XCJ9IiwiZXhwIjoxNzM1MjQyMDQwLCJpYXQiOjE3MzUyMzQ3ODB9.mI199bTKskc1dLgTTwGwKY4XtFRRtKx9m_msugEidFLk0bI6cK92HSEONVOl9Ls0xpcWkvAkDxQF-x-qk1UjckuhmHDnvEqczqDUYBeYlT7ZgvKE7T560OIE45gHCi26iMRY4XoCVvpUEvetnP4gKdhnJdnjikRYWv6V2f_v-4Y",
        # 'x-sign': "azRr1P002xAAIiJv99WollUt%2BDZxwiJiImIiYiAwwZIvX1JxG0aRp45eEktiKxC53OIChfXfEPPhaOYGclNmJfBV9HIiciJiInIiYi",
        # 'x-mini-wua': "ayQTS59B5vYCVblym4J8Fr%2FNH0nIKJmVIFf1%2FFPpYxfeEStvgfGZLbcnO5wnP%2F7D5%2F54Np65zfkx9qRH%2F4nD0g07VE6Q9p9Bqnj8%2BZJDI9Rddf%2Fn80JyTlb1ZmI7mcvQNy9reWS9Jb5Ac8xJWaZA1U8WP3e1P%2Ft6dU%2FVtwvRJEx5YNMKkX5voqiP4I9eXFyjcIg0%3D",
        # 'x-umt': "09cBM5JLPFrDwwKUBJMtv%2BgCDn170ykc",
        # 'x-sgext': "JBIHXgwyghl4Y%2BHPbR9syF42bjVmMX02aDBqMX0yZiR9Nmk0azRuPmg0ZiRuND1mbjduN2ZmPGI%2FND01fTZ9MX0%2FaiRuN24yfTR9Nn02fTZ9Nn02fTZ9N300fTV9N303fTd9N303fTd9N30kOyRuJG4kaTA%2FP242fTduN243fTd9NTpmfTd9JG0kZiRtJG0kJEQ3bH03fSd%2BJ24nfidu",
        'x-bx-version': "6.6.240404",
        # 'x-host': "198.18.0.44",
        # 'Cookie': "munb=2211197091650; _nk_=t-2211197091650-52; cookie2=14fed731d00892b840b086409123352b; csg=bd15dfd5; t=97756c615ff797cf2e00123c48ddd31b; _tb_token_=51b6933ff31ed"
    }
    return headers


def get_signin_count(access_token) -> list[Any]:
    logger.info("get_signin_count")
    url = "https://member.aliyundrive.com/v2/activity/sign_in_list?_rx-s=mobile"
    #
    headers = get_header(access_token)
    response = requests.post(url, headers=headers, data=json.dumps({}))
    logger.info(response.text)

    count_data = re.search(r'"signInCount":(\d+)', response.text)
    month_data = re.search(r'"month":"(.*?)"', response.text)

    print(time.time())
    count = int(count_data.group(1))
    if response.status_code == 200:
        success = True
        text = f"{month_data.group(1)}已经领取天数{count}"
    else:
        text = "获取信息失败"
        success = False

    return [success, count, text]

def start_signin(access_token, count) -> list[Any]:
    logger.info("start_signin")
    url = "https://member.aliyundrive.com/v1/activity/sign_in_reward?_rx-s=mobile"
    headers = get_header(access_token)

    response = requests.post(url, headers=headers, data=json.dumps({"signInDay": str(count)}))
    logger.info(response.text)

    notice_data = re.search(r'"notice":"(.*?)"', response.text)
    if response.status_code == 200:
        success = True
        # text = f"签到成功, 结果: {notice_data.group(1)}"
    else:
        # text = f"签到失败, 结果: {notice_data.group(1)}"
        success = False


    return [success, response.text]


def test_aliyun():
    logger.info("开始请求aliyun")

    try:
        [success, count, text] = get_signin_count(ACCESS_TOKEN)
        if success and count > 0:
            [success, text] = start_signin(ACCESS_TOKEN, count)
    except Exception as e:
        success = False
        text = str(e)

    logger.info(text)

