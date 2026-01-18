import os
import uuid
from dotenv import load_dotenv
from redis_client import redis_client
from database import SessionLocal
from models.chat_model import roomSchema, messageSchema
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

import asyncio

async def message_worker():
    print("message worker started")

    GROUP = os.getenv("GROUP_NAME")
    CONSUMER = os.getenv("CONSUMER_NAME")
    STREAM = os.getenv("STREAM_NAME")

    while True:
        # 1️⃣ Redis read in thread
        messages = await asyncio.to_thread(
            redis_client.xreadgroup,
            groupname=GROUP,
            consumername=CONSUMER,
            streams={STREAM: '>'},
            count=1,
            block=5000
        )

        if not messages:
            await asyncio.sleep(0.1)  # yield control
            continue

        for _, message_list in messages:
            for message_id, message_data in message_list:
                # 2️⃣ DB work in thread
                await asyncio.to_thread(
                    process_message,
                    STREAM,
                    GROUP,
                    message_id,
                    message_data
                )
                await asyncio.to_thread(
                    send_mail_worker ,
    
                )
                redis_client.xack(STREAM, GROUP, message_id)

def send_mail_worker():
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python

    message = Mail(
        from_email='shreya.xyz.wtf@gmail.com',
        to_emails='personal.vaibhavtripathi@gmail.com',
        subject='Sending with Twilio SendGrid is Fun',
        html_content=f"<strong>Vaibhav is a phony . hes a gay phonyy</strong>")
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        # sg.set_sendgrid_data_residency("eu")
        # uncomment the above line if you are sending mail using a regional EU subuser
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


def process_message(STREAM, GROUP, message_id, message_data):
    db = SessionLocal()
    try:
        sender_id = message_data.get('sender_id')
        msg = message_data.get('message')
        room_name = message_data.get('room_name')

        if not sender_id or not msg or not room_name:
            redis_client.xack(STREAM, GROUP, message_id)
            return

        room = db.query(roomSchema).filter(
            roomSchema.room_name == room_name
        ).first()

        if not room:
            redis_client.xack(STREAM, GROUP, message_id)
            return

        new_record = messageSchema(
            id=str(uuid.uuid4()),
            room_id=room.id,
            message=msg,
            sender_id=sender_id
        )

        db.add(new_record)
        db.commit()
       

    finally:
        db.close()


