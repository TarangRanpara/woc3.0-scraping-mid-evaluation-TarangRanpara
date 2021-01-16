from selenium import webdriver
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import csv

class GsocScrapper:

    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None
        self.url = None
        self.org_skills = dict()
        self.org_links = dict()
        self.org_skills_to_be_sent = dict()
        
    def init_chrome_window(self):
        self.driver = webdriver.Chrome(self.driver_path)
        
    def set_url(self, url):
        self.url = url
        self.driver.get(self.url)

    def close(self):
        self.driver.close()
        
    def scrap(self):
        print('Scraping data:')
        for i in range(1, 200):
            orgs = self.driver.find_elements_by_xpath(f"/html/body/main/section/div/ul/li[{i}]")
            for org in orgs:
                org_name = org.get_attribute("aria-label")
                print('company name:', org_name)
                self.org_skills[org_name] = []
                org.click()
                ul = self.driver.find_elements_by_xpath("/html/body/main/section[1]/div/div/div[2]/md-card/div/div[3]/ul")
                lst = ul[0].find_elements_by_css_selector("li")
                print('url:', self.driver.current_url)
                self.org_links[org_name] = self.driver.current_url
                print('skills:')
                for skill in lst:
                    print(skill.text)
                    self.org_skills[org_name].append(skill.text)
                self.driver.execute_script("window.history.go(-1)")
                print('.........')

    def write_csv(self, choices):
        for choice in choices:
            for key, value in self.org_skills.items():
                if choice in value:
                    self.org_skills_to_be_sent[key] = value

        with open("org_skills.csv", "w") as file:
            writer = csv.writer(file)
            for key, value in self.org_skills_to_be_sent.items():
                writer.writerow([key, self.org_links[key], str(value)])

    def send_mails(self, to_email, to_pwd):
        msg = MIMEMultipart()
        msg['From'] = to_email
        msg['To'] = to_email
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "GSOC 2020"

        msg.attach(MIMEText("Please find attached. "))
        path = './org_skills.csv'
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(Path(path).name))
        msg.attach(part)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(to_email, to_pwd)
        smtp.sendmail(to_email, to_email, msg.as_string())
        smtp.quit()

print('It will run only on WINDOWS.')

email = input('enter email:')
pwd = input('enter password:')
choice = input('enter skill: (type exit to end.):')
choices = []
while choice != 'exit':
    choices.append(choice)
    choice = input('enter skill (type exit to end.):')

print(choices)

scrapper = GsocScrapper(".//w_driver//chromedriver") #to run on linux, supply your own driver here. 
scrapper.init_chrome_window()
scrapper.set_url("https://summerofcode.withgoogle.com/archive/2020/organizations/")
scrapper.scrap()
scrapper.write_csv(choices)
scrapper.send_mails(email, pwd)
scrapper.close()
