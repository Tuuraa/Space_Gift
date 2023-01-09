import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adminpanel.settings')
django.setup()

from time import sleep
from datetime import datetime, timezone

import telebot

from django.conf import settings

from adminpanel import models

bot = telebot.TeleBot(settings.TOKEN)

DELAY = 1


def process_statuses():
    now = datetime.now(timezone.utc)

    expired_posts = models.Post.objects.filter(
        status='postponed', postpone_time__lte=now
    )

    for post in expired_posts:
        print(f'queue {post.created}')
        try:
            post.status = 'queue'
            post.save()
        except BaseException as error:
            print(f'{type(error)}: {error}')


def send_post_to_user(post, user):
    message = post.message

    if post.button_text and post.button_url:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(telebot.types.InlineKeyboardButton(
            text=post.button_text,
            url=post.button_url
        ))
    else:
        keyboard = None

    if post.photo:
        photo_url = f'{settings.BASE_URL}/media/{post.photo}'
        print(photo_url)

        bot.send_photo(user.tel_id,
            photo=photo_url,
            caption=message,
            parse_mode='html',
            reply_markup=keyboard
        )
    else:
        bot.send_message(user.tel_id,
            text=message,
            parse_mode='html',
            reply_markup=keyboard
        )


def process_post(post):
    print(f'post {post.created}')
    post.status = 'process'
    post.save()

    users = list(models.Users.objects.all())

    receivers = []

    for user in users:
        receivers.append(user)

    amount_of_receivers = 0

    for user in receivers:
        try:
            send_post_to_user(post, user)
        except BaseException as error:
            print(f'{type(error)}: {error}')
        else:
            amount_of_receivers += 1
        sleep(0.01)
    print(f'total {amount_of_receivers}')

    post.status = 'done'
    post.amount_of_receivers = amount_of_receivers
    post.save()


def main():
    while True:
        try:
            process_statuses()
        except BaseException as error:
            print(f'{type(error)}: {error}')

        try:
            post = models.Post.objects.filter(status='queue').order_by('created').first()
            if post:
                process_post(post)
        except BaseException as error:
            print(f'{type(error)}: {error}')

        sleep(DELAY)


if __name__ == '__main__':
    main()
