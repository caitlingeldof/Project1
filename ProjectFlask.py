from flask import Flask
from flask import render_template, request
import os
from DbClass import DbClass
from readSensor import readSensor
import RPi.GPIO as GPIO
import time
import schedule
from threading import Thread

app = Flask(__name__)

connection = DbClass()
sensor = readSensor()

knopBinnen = 26
knopBuiten = 19

loggedIn = False

condition = "closed"


def writeToDb():
    temp = sensor.print_temp()
    humidity = float(sensor.getAdc(0))
    connection.setDataToDatabaseMetingen(temp, 'temperature')
    connection.setDataToDatabaseMetingen(humidity, 'humidity')
    # connection.setDataToDatabaseMetingen(22, 'temperatuur')
    # connection.setDataToDatabaseMetingen(0, 'vochtigheid')


def emptyDb():
    connection.truncateTable("Metingen")


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led = 16
GPIO.setup(led, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(knopBinnen, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(knopBuiten, GPIO.IN, pull_up_down=GPIO.PUD_UP)
servoDeur = GPIO.PWM(21, 50)
servoDeur.start(0)

servoRaam = GPIO.PWM(20, 50)
servoRaam.start(0)

servoRaam2 = GPIO.PWM(12, 50)
servoRaam2.start(0)

isKnopGedruktVorig = 1
stand = 0

isKnopBuitenGedruktVorig = 1
standBuiten = 0


def getValue():
    global condition
    temperature = sensor.print_temp()
    set_temp = 26

    humidity = sensor.getAdc(0)
    set_hum = 50
    try:

        if temperature <= set_temp - 5:
            servoDeur.ChangeDutyCycle(7.5)  # turn towards 90 degree
            servoRaam.ChangeDutyCycle(7.5)  # turn towards 90 degree
            servoRaam2.ChangeDutyCycle(7.5)  # turn towards 90 degree
            condition = "closed"
            connection.setDataToDatabaseMetingenMetVerandering(temperature, "temperature", "automatic: closed")
        if temperature >= set_temp + 5:
            servoDeur.ChangeDutyCycle(12.5)  # turn towards 180 degree
            servoRaam.ChangeDutyCycle(12.5)  # turn towards 180 degree
            servoRaam2.ChangeDutyCycle(12.5)  # turn towards 180 degree
            condition = "open"
            connection.setDataToDatabaseMetingenMetVerandering(temperature, "temperature", "automatic: opened ")

        if humidity < set_hum:
            GPIO.output(led, GPIO.HIGH)
            connection.setDataToDatabaseMetingenMetVerandering(humidity, "humidity", "automatic: watering ")
        else:
            GPIO.output(led, GPIO.LOW)
    except KeyboardInterrupt:
        GPIO.cleanup()


# def openClose(number):
#     global isKnopGedruktVorig, stand, isKnopBuitenGedruktVorig, standBuiten, condition
#     isKnopGedrukt = GPIO.input(knopBinnen)
#
#     if GPIO.event_detected(knopBinnen):
#         if (isKnopGedrukt != isKnopGedruktVorig):
#             if (isKnopGedrukt == 0):
#                 if (stand == 0):
#                     print("Gedrukt Binnen")
#                     condition = "closed"
#                     connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door closed manually")
#                     stand = 1
#                     servoDeur.ChangeDutyCycle(7.5)  # turn towards 90 degree
#                 else:
#                     print("Gedrukt Binnen 2")
#                     condition = "open"
#                     connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door opened manually")
#                     stand = 0
#                     servoDeur.ChangeDutyCycle(12.5)  # turn towards 180 degree
#
#         isKnopGedruktVorig = isKnopGedrukt
#         time.sleep(0.0025)
#
#     isKnopBuitenGedrukt = GPIO.input(knopBuiten)
#
#     if GPIO.event_detected(knopBuiten):
#         if (isKnopBuitenGedrukt != isKnopBuitenGedruktVorig):
#             if (isKnopBuitenGedrukt == 0):
#                 if (standBuiten == 0):
#                     print("Gedrukt Buiten ")
#                     condition = "closed"
#                     connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door closed manually")
#                     standBuiten = 1
#                     servoDeur.ChangeDutyCycle(7.5)  # turn towards 90 degree
#
#                 else:
#                     print("Gedrukt Buiten 2")
#                     condition = "open"
#                     connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door opened manually")
#                     standBuiten = 0
#                     servoDeur.ChangeDutyCycle(12.5)  # turn towards 180 degree
#
#         isKnopBuitenGedruktVorig = isKnopBuitenGedrukt
#         time.sleep(0.0025)

def openClose(number):
    global isKnopGedruktVorig, stand, isKnopBuitenGedruktVorig, standBuiten, condition, servoDeur
    # isKnopGedrukt = GPIO.input(knopBinnen)
    servoDeur.start(0)

    if GPIO.event_detected(knopBinnen):
        # if (isKnopGedrukt != isKnopGedruktVorig):
        #     if (isKnopGedrukt == 0):
        if (stand == 0):
            print("Gedrukt Binnen")
            condition = "closed"
            connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door closed manually")
            stand = 1
            servoDeur.ChangeDutyCycle(6)  # turn towards 90 degree
        else:
            print("Gedrukt Binnen 2")
            condition = "open"
            connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door opened manually")
            stand = 0
            servoDeur.ChangeDutyCycle(2.5)  # turn towards 180 degree

        # isKnopGedruktVorig = isKnopGedrukt
    time.sleep(0.0025)  # isKnopBuitenGedrukt = GPIO.input(knopBuiten)

    if GPIO.event_detected(knopBuiten):

        # if (isKnopBuitenGedrukt != isKnopBuitenGedruktVorig):
        #     if (isKnopBuitenGedrukt == 0):
        if (standBuiten == 0):
            print("Gedrukt Buiten ")
            condition = "closed"
            connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door closed manually")
            standBuiten = 1
            servoDeur.ChangeDutyCycle(6)  # turn towards 90 degree

        else:
            print("Gedrukt Buiten 2")
            condition = "open"
            connection.setDataToDatabaseMetingenMetVerandering(sensor.print_temp(), "temperature", "Door opened manually")
            standBuiten = 0
            servoDeur.ChangeDutyCycle(2.5)  # turn towards 180 degree

            # isKnopBuitenGedruktVorig = isKnopBuitenGedrukt

        time.sleep(3)
        # servoDeur.ChangeDutyCycle(0)
        servoDeur.stop()
@app.route('/')
def onboarding():
    return render_template('onboarding.html')


@app.route('/onboarding1', methods=['post'])
def onboarding1():
    global loggedIn
    name = request.form['inputName']
    email = request.form['inputEmail']
    password = request.form['inputPass']
    passwordRepeat = request.form['inputRepeatPass']
    loggedIn = False
    unique = connection.getDataFromDatabaseEmail(email)

    if unique == []:
        if password == passwordRepeat:
            connection.setDataToDatabaseGebruikers(name, email, password)
            return render_template('onboarding1.html'), True
        else:
            error = "Passwords do not match."
    else:
        error = "Account with e-mailaddress " + email + " already exists."
    return render_template('onboarding.html', error=error)


@app.route('/index', methods=['post'])
def index():
    global loggedIn, condition
    error = None
    if request.method == 'POST':
        email = request.form['emailLogin']
        password = request.form['passwordLogin']
        data = connection.getDataFromDatabaseMetVoorwaarde(email, password)

        if data == []:
            loggedIn = False
            error = "Invalid Credentials. Please try again."
        else:
            # temp = sensor.print_temp()
            # humi = float(sensor.getAdc(0))
            loggedIn = True
            temp = 22
            humi = 56
            return render_template('index.html', temperature=temp, humidity=humi, condition=condition)
    return render_template('onboarding.html', error=error)


@app.route('/onboarding2', methods=['post'])
def onboarding2():
    if request.method == 'POST':
        reports = request.form['reports']
        unit = request.form['unit']
        connection.updateTable(unit, reports)
        return render_template('onboarding2.html')


@app.route('/index', methods=['post'])
def index_afterO():
    global loggedIn
    temp = request.form['temp']
    hum = request.form['hum']
    # if request.method == 'POST':
    # temp = 15
    # hum = 55
    connection.insertConfig(hum, temp)
    temp_ = sensor.print_temp()
    humi = float(sensor.getAdc(0))
    loggedIn = True
    # temp_ = 22
    # humi = 56
    return render_template('index.html', temperature=temp_, humidity=humi, condition=condition)


@app.route('/index')
def index_loggedIn():
    global loggedIn, condition
    if loggedIn == True:
        temp = sensor.print_temp()
        humi = float(sensor.getAdc(0))
        # temp = 22
        # humi = 56
        return render_template('index.html', temperature=temp, humidity=humi, condition=condition)
    else:
        error = "Please sign in."
    return render_template('onboarding.html', error=error)


@app.route('/logout')
def logout():
    global loggedIn
    loggedIn = False
    return render_template('onboarding.html')


@app.route('/report')
def report():
    global loggedIn
    if loggedIn == True:
        results = connection.getDataFromDatabase()
        return render_template('report.html', results=results)
    else:
        error = "Please sign in."
    return render_template('onboarding.html', error=error)


@app.route('/settings')
def settings():
    global loggedIn
    if loggedIn == True:
        return render_template('settings.html')
    else:
        error = "Please sign in."
    return render_template('onboarding.html', error=error)


schedule.run_pending()

if __name__ == '__main__':
    schedule.every(15).minutes.do(writeToDb)
    schedule.every(15).minutes.do(getValue)
    schedule.every(24).hours.do(emptyDb)
    t = Thread(target=run_schedule)
    t.start()
    GPIO.add_event_detect(knopBinnen, GPIO.FALLING, callback=openClose,bouncetime=50)
    GPIO.add_event_detect(knopBuiten, GPIO.FALLING, callback=openClose,bouncetime=50)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=False)
