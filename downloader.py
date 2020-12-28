import time
import passport
import requests
import json
import re
import os

mobile_header = {
    "Origin": "file://",
    "Content-Type": "application/json;charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "X-SESSION-ID": "null",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36"
}

identity_url = "https://identity.zju.edu.cn/auth/realms/zju/broker/cas-client/endpoint?state=xDW9NGsc1FhRC40asEfEzgBWkqTLKHQRYdAUCOfKQ_0.eQODgwMRKn4.TronClassApp&ticket=ST-7679681-FYOjmUt7LXBrhtfKbWmU-zju.edu.cn"

xzzd_base_url = "https://courses.zju.edu.cn"

xzzd_api_login_url = "/api/login?login=access_token&version=7"

xzzd_login_url = "http://course.zju.edu.cn/global/login?redirectpath=http://course.zju.edu.cn/"

course_list_url = "https://courses.zju.edu.cn/api/users/{}/courses?page=1&page_size=1000"

course_main_page_url = "https://courses.zju.edu.cn/user/courses"

courseware_list_url = "https://courses.zju.edu.cn/api/course/{}/coursewares?page=1&page_size=1000"

ref_url = "https://courses.zju.edu.cn/api/uploads/reference/{}/blob"

user_id_pattern = "span id=\"userId\" data-id=\"(.+)\" value"


def login_xzzd(s):
    s.get(xzzd_login_url)


def get_user_id(s: requests.Session):
    # r = s.get(identity_url)
    # print(r.text)
    # print(r.headers)
    # r = s.get(xzzd_base_url+xzzd_api_login_url)
    # return r.text

    r = s.get(course_main_page_url)
    if len(re.findall(user_id_pattern, r.text)) > 0:
        return re.findall(user_id_pattern, r.text)[0]
    else:
        return -1


def get_course_list(s, user_id):
    r = s.get(course_list_url.format(user_id))
    course_json = r.json()
    course_list = []
    for course in course_json['courses']:
        # print(course)
        course_list.append((course['name'], course['id']))
    return course_list


def get_download_list(s, course_id):
    download_list = []
    r = s.get(courseware_list_url.format(course_id))
    loads = r.json()
    for courseware in loads['activities']:
        if 'uploads' in courseware:
            if isinstance(courseware['uploads'], list):
                for upload in courseware['uploads']:
                    download_list.append(
                        (upload['name'], ref_url.format(upload['reference_id'])))
    return download_list


def download_file(s, url, file_name):
    r = s.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)
        f.close()


def parse_content_command(s: str, index_max: int) -> list:
    if s.isnumeric():
        if int(s) < index_max:
            return [int(s)]
        else:
            return []
    if isinstance(eval(s), list):
        return list(eval(s))
    if s == 'all':
        return list(range(index_max))


if __name__ == "__main__":
    s = requests.session()
    user_school_id = input("input your zju school id\n")
    passport.getPass(s, user_school_id)
    login_xzzd(s)
    user_id = get_user_id(s)
    course_list = get_course_list(s, user_id)
    for index, course in enumerate(course_list):
        print(index, course[0])
    course_index = int(input("select course with index\n"))
    download_list = get_download_list(s, course_list[course_index][1])
    for index, course_ware in enumerate(download_list):
        print(index, course_ware)
    course_ware_index = parse_content_command(
        input("select course ware with index list\n"), len(download_list))
    dir_appendix = input(
        "input download directory, default current directory\n")
    file_name = ""
    for index in course_ware_index:
        if not os.path.exists(dir_appendix):
            print("directory not found")
            print("download to ./{}".format(download_list[index][0]))
            file_name = "./"+download_list[index][0]
        else:
            file_name = dir_appendix+"/"+download_list[index][0]
        try:
            download_file(s, download_list[index][1],
                          file_name)
            print("download successful")
        except:
            print("download error")
