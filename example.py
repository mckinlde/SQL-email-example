from time import sleep
import mysql.connector
import smtplib
from email.mime.text import MIMEText

def send_mail(to, from_addr, subject, text):
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to
    s = smtplib.SMTP_SSL("smtp.gmail.com")
    s.login('johnnygooddeals@gmail.com', 'H@sht4bles')
    # for Python 3
    s.send_message(msg)
    # OR
    # for Python 2 (or 3, will still work)
    # s.sendmail(from_addr, [to], msg.as_string())
    s.quit()

### Connect to / Create Craigslist DB
connection = mysql.connector.connect(host="localhost", port=3306, user="semdemo", passwd="demo", db="semdemo")
db = connection.cursor(prepared=True)

db.execute("""
        CREATE TABLE IF NOT EXISTS PDX_LISTINGS (
            Title VARCHAR(512) NOT NULL,
            Price VARCHAR(512) NOT NULL,
            Make VARCHAR(512) NOT NULL,
            Model VARCHAR(512) NOT NULL,
            Year VARCHAR(512) NOT NULL,
            Odo VARCHAR(512) NOT NULL,
            Added VARCHAR(512) NOT NULL,
            URL VARCHAR(512) NOT NULL PRIMARY KEY
        )""")
connection.commit()

while True:
    # Get current online listings
    seedURL = 'https://kpr.craigslist.org/search/cto?min_price=1000&max_price=2900&auto_drivetrain=3'
    testSoup = retrieve(seedURL)
    ## get_listings returns a list of links to listings : ['url', 'url']
    current_online_listings = get_listings(testSoup)

    # Which ones are already in our DB?
    query = ('select * from PDX_LISTINGS;')
    db.execute(query)
    current_saved_listings = []
    for (Data) in db:
        current_saved_listings.append(str(Data[7], 'utf-8'))

    # add only the new listings
    unsaved = []
    for element in current_online_listings:
        if element not in current_saved_listings:
            unsaved.append(element)
            ### get_info isn't defined because this is just a SQL & email example
            ### suffice to say it scrapes all the info we need for a listing from it's URL
            info = get_info(element) # element is a URL
            # Get details about listing
            info = get_info(element) # info is the listing that we scrape, as a dict {} of strings ''
            # add listing to DB
            db.execute(
                "insert into PDX_LISTINGS(Title, Price, Make, Model, Year, Odo, Added, URL) values(?, ?, ?, ?, ?, ?, ?, ?)",
                [info['title'], info['price'], info['make'], info['model'], info['year'], info['odo'], info['added'],
                 element])
            connection.commit()

            # Send Email with listing details
            to = 'timmycustomer@gmail.com'
            from_addr = 'johnnygooddeals@gmail.com'
            subject = 'New instrument for ' + info['price']
            text = 'Hi Timmy!\n\nThere\'s a new listing for you!\n\n' + element + '\n\nSincerely,\nJohnny'
            sleep(5)  # give some time to avoid double-sends
            send_mail(to, from_addr, subject, text)
            print('Sent with no ODO to Timmy!')
