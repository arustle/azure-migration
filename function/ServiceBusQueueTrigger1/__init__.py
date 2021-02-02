import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    # logging.info('Python ServiceBus queue trigger processed message: %s',
    #              msg.get_body().decode('utf-8'))
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    conn = psycopg2.connect(
        host=',
        dbname='techconfdb', 
        user='',
        password=''
    )

    cursor = conn.cursor()
    try:
        # TODO: Get notification message and subject from database using the notification_id
        query = "SELECT message, subject FROM notification WHERE id = {0}".format(notification_id)
        cursor.execute(query)
        notification = cursor.fetchone()

        # TODO: Get attendees email and name
        query = "SELECT email, CONCAT(first_name, ' ', last_name) FROM attendee"
        cursor.execute(query)
        attendees = cursor.fetchall()

        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            # logging.info('attendee[0]: %s',attendee[0])
            # logging.info('notification[0]: %s',notification[0])
            # logging.info('notification[1]: %s',notification[1])
            Mail(
                "info@techconf.com",
                attendee[0],
                notification[1],
                notification[0]
            )

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        status = "Notified {0} attendees".format(len(attendees))
        query = "UPDATE notification SET status = '{0}', completed_date='{1}' WHERE id = {2}".format(status, datetime.utcnow(), notification_id)
        cursor.execute(query)

        conn.commit()


    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conn.close()