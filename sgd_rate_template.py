from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


def check_internet_connection():
    """检测网络连接是否正常"""
    try:
        response = requests.get("http://www.baidu.com", timeout=5)
        return response.status_code == 200
    except requests.RequestException as e:
        log(f"出现错误: {e}")


def send_email(rate):
    sender_email = "your_mail@gmail.com"
    receiver_email = "your_mail@gmail.com"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "SGD_reminder"

    message.attach(MIMEText("The current rate of SGD has dropped to " + str(rate), "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, "xxxx")
        server.sendmail(sender_email, receiver_email, message.as_string())
        log("邮件发送成功！")


def log(*args):
    with open("log.txt", "a") as f:
        for msg in args:
            f.write(msg + " ")
        f.write("\n")


def main():

    url = "https://www.icbc.com.cn/column/1438058341489590354.html"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    try:
        while True:

            if not check_internet_connection():
                log("网络不可用,等待x分钟后再重试...")
                time.sleep(60*60)
                continue

            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(5)  # 等待5秒，确保动态内容加载完成
            xpath = '//*[@id="app"]/div[2]/div[3]/table/tbody/tr[5]/td[3]/div'

            try:
                sgd_rate = driver.find_element(By.XPATH, xpath).text
                sgd_rate = float(sgd_rate)
            except Exception as e:
                log(f"未能获取新加坡元汇率：{e}")
                time.sleep(60*60)
                continue

            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # 判断汇率是否低于5.4
            if sgd_rate < 540:
                log("新加坡元汇率低于5.4,发送邮件提醒！")
                send_email(sgd_rate)
            
            log(f"当前新加坡元汇率: {sgd_rate}. " + "时间:" + current_time)
            time.sleep(30*60)  # 每30分钟获取一次

    except Exception as e:
        log(f"出现错误: {e}")


if __name__ == "__main__":
    main()

