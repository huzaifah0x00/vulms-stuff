import argparse
import json
import re

from datetime import datetime
from ics import Calendar, Event

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement


def login(username: str, password: str):
    usernamefield: WebElement = driver.find_element_by_css_selector("input#txtStudentID")
    passwordfield: WebElement = driver.find_element_by_css_selector("input#txtPassword")
    login_btn: WebElement = driver.find_element_by_css_selector("input#ibtnLogin")
    usernamefield.send_keys(username)
    passwordfield.send_keys(password)
    login_btn.click()


def goto_homepage():
    driver.get("https://vulms.vu.edu.pk/home.aspx")


def goto_todo_calendar_page():
    driver.get("https://vulms.vu.edu.pk/ActivityCalendar/ActivityCalendar.aspx")


def export_todo_calender_to_ics():
    if "ActivityCalendar.aspx" not in driver.current_url:
        raise Exception("invalid usage. first you need to go to calendar page (goto_todo_calendar_page)")

    c = Calendar()

    # extract calendar jsondata from page source code, see example_calendar_jsondata.json for structure
    calender_jsondata = json.loads(re.search("var JsonData = (\[.+\]);", driver.page_source).group(1))

    for event in calender_jsondata:
        start_date = parse_date(event["start"])
        end_date = parse_date(event["end"])
        url = "https://vulms.vu.edu.pk" + event["url"]

        e = Event(name=event["title"], begin=start_date, end=end_date, url=url)
        e.make_all_day()

        c.events.add(e)

    with open("my.ics", "w") as my_file:
        my_file.writelines(c)


def parse_date(date_str: str):
    year, month, day = date_str.split(",")
    year, month, day = int(year), int(month), int(day)
    return datetime(year=year, month=month, day=day)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VULMS stuff")
    parser.add_argument("-u", "--username", type=str, help="VULMS username", required=True)
    parser.add_argument("-p", "--password", type=str, help="VULMS password", required=True)

    args = parser.parse_args()

    try:
        driver = webdriver.Chrome()
        driver.get("https://vulms.vu.edu.pk")
        login(args.username, args.password)
        goto_todo_calendar_page()
        export_todo_calender_to_ics()
    finally:
        driver.close()
