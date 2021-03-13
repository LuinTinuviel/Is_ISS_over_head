import requests
from datetime import datetime
from time import sleep
import json
import smtplib

# --------- Params Load -------------- #
with open("parameters.json") as json_file:
    api_params = json.load(json_file)

with open("connection.json") as json_file:
    connection_params = json.load(json_file)


def send_notification_email():
    my_mail = connection_params["from_email"]
    password = connection_params["password"]
    smtp_server = connection_params["smtp_server"]
    port = connection_params["smtp_port"]
    to_mail = connection_params["to_email"]
    message = "In Your location ISS station might be currently visible!\n\nTry to find It ;)"
    subject = "ISS Station Visibility Report"

    try:
        with smtplib.SMTP(smtp_server, port, timeout=120) as connection:
            connection.starttls()
            connection.login(user=my_mail, password=password)
            connection.sendmail(
                from_addr=my_mail,
                to_addrs=to_mail,
                msg=f"Subject:{subject}"
                    f"\n\n{message}")
    except smtplib.SMTPServerDisconnected:
        print("Email not sent, smtp problem")


def get_iss_location():
    try:
        response = requests.get(url="http://api.open-notify.org/iss-now.json")
        response.raise_for_status()
    except Exception as e:
        print(e)
        return -666, -666
    else:
        data = response.json()

        iss_latitude = float(data["iss_position"]["latitude"])
        iss_longitude = float(data["iss_position"]["longitude"])

        return iss_longitude, iss_latitude


def get_sunrise_sunset_data():
    response = requests.get("https://api.sunrise-sunset.org/json", params=api_params["sunrise_api_parameters"])
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    return sunrise, sunset


def is_iss_visible(day_hours=None):
    iss_location = get_iss_location()
    my_location = (api_params["sunrise_api_parameters"]["lng"], api_params["sunrise_api_parameters"]["lat"])
    if day_hours is None:
        day_hours = get_sunrise_sunset_data()
    current_time = datetime.now()

    print("############## Location Data ##############")
    print(f'ISS Location: {iss_location}')
    print(f'My location: {my_location}')
    print(f'Day hours: {day_hours}')
    print(f'Current hour: {current_time.hour}')

    print(f'long difference: {abs(my_location[0] - iss_location[0])}')
    print(f'lat difference: {abs(my_location[1] - iss_location[1])}')
    print("############################################\n\n")

    if abs(my_location[0] - iss_location[0]) < 5 and abs(my_location[1] - iss_location[1]) < 5:
        print("Location Okay, checking time")
        if current_time.hour <= day_hours[0] or current_time.hour >= day_hours[1]:
            print("Time okay!")
            return True
    return False


# Your position is within +5 or -5 degrees of the ISS position.
while True:
    if is_iss_visible():
        send_notification_email()
    sleep(60)
