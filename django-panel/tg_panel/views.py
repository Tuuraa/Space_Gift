from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from .models import TgUser, ApiTokens
import telebot


bot = telebot.TeleBot(ApiTokens.objects.get(api='bot_api').title)
bot.token = ApiTokens.objects.get(api='bot_api').title


def index(request, *args, **kwargs):
    return redirect('admin-page')


@csrf_exempt
def deposit_transfer(request, *args, **kwargs):
    data = request.POST
    user_id = data.get('user_id')
    amount_rub = data.get('amount_rub')

    if user_id is None or not user_id.isnumeric():
        return JsonResponse({'error_status': 'incorrect_user_id'})

    users = TgUser.objects.filter(user_id=user_id)

    if not users:
        return JsonResponse({'error_status': 'user_not_exist'})

    if amount_rub is None or not amount_rub.replace('.', '', 1).isdecimal():
        return JsonResponse({'error_status': 'incorrect_amount_rub'})
    user = users[0]
    user.depozit += float(amount_rub)
    user.save()

    try:
        bot.send_message(
            chat_id=user_id,
            text=f'<b> ✅ Депозит в размере {amount_rub} рублей успешно перенесен </b>, он будет отображаться в разделе "Кошелек"',
            parse_mode="html",
        )
    except Exception:
        pass

    return JsonResponse({'dt_status': 'success'})
