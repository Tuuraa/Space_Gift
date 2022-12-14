import requests
from datetime import datetime, timezone

from django.db.models import Sum

import tg_panel.models as tg_models


def tg_send_message(chat_id, token, status):
    requests.post(
        url='https://api.telegram.org/bot{0}/sendMessage'.format(token),
        data={'chat_id': chat_id, 'text': f'Статус вашей транзакции: {status}'}
    )


def get_statistic(user_pk, start_time, end_time):
    if start_time is None:
        start_time = datetime(1900, 1, 1)
    
    if end_time is None:
        end_time = datetime.now(timezone.utc)
    
    user = tg_models.TgUser.objects.get(pk=user_pk)
    total_pay = tg_models.Pay.objects.filter(user_id=user.user_id, date__gte=start_time, date__lte=end_time).aggregate(total=Sum('pay_amount'))['total'] or 0
    total_pay += tg_models.CryptPay.objects.filter(user_id=user.user_id, date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_rub'))['total'] or 0


    total_withdraw = tg_models.Withdraw.objects.filter(user_id=user.user_id, date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount'))['total'] or 0
    total_withdraw += tg_models.Withdraw.objects.filter(user_id=user.user_id, date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_commission'))['total'] or 0


    data = {
        'total_pay': total_pay,
        'total_withdraw': total_withdraw,
        'total_ref': tg_models.RefMoney.objects.filter(user_id=user.user_id, date__gte=start_time, date__lte=end_time).aggregate(total_ref=Sum('money'))['total_ref'] or 0,
        'total_procent': user.gift_money or 0,
        'total_pay_btc': tg_models.CryptPay.objects.filter(user_id=user.user_id, pay_type='BTC', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount'))['total'] or 0,
        'total_withdraw_btc': tg_models.Withdraw.objects.filter(user_id=user.user_id, type_crypt='BTC', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_commission'))['total'] or 0,
        'total_pay_ltc': tg_models.CryptPay.objects.filter(user_id=user.user_id, pay_type='LTC', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount'))['total'] or 0,
        'total_withdraw_ltc': tg_models.Withdraw.objects.filter(user_id=user.user_id, type_crypt='LTC', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_commission'))['total'] or 0,
        'total_pay_eth': tg_models.CryptPay.objects.filter(user_id=user.user_id, pay_type='ETH', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount'))['total'] or 0,
        'total_withdraw_eth': tg_models.Withdraw.objects.filter(user_id=user.user_id, type_crypt='ETH', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_commission'))['total'] or 0,
        'user': user,
    }
    return data


def get_all_stats(start_time, end_time):
    if start_time is None:
        start_time = datetime(1900, 1, 1)
    
    if end_time is None:
        end_time = datetime.now(timezone.utc)

    total_pay = tg_models.Pay.objects.filter(date__gte=start_time, date__lte=end_time).aggregate(total=Sum('pay_amount'))['total'] or 0
    total_pay += tg_models.CryptPay.objects.filter(date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_rub'))['total'] or 0

    total_withdraw = tg_models.Withdraw.objects.filter(date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount'))['total'] or 0
    total_withdraw += tg_models.Withdraw.objects.filter(date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_commission'))['total'] or 0


    data = {
        'total_pay': total_pay,
        'total_withdraw': total_withdraw,
        'total_ref': tg_models.RefMoney.objects.all().aggregate(total_ref=Sum('money'))['total_ref'] or 0,
        'total_procent': tg_models.TgUser.objects.all().aggregate(total_procent=Sum('gift_money'))['total_procent'] or 0,
        'total_pay_btc': tg_models.CryptPay.objects.filter(pay_type='BTC', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount'))['total'] or 0,
        'total_withdraw_btc': tg_models.Withdraw.objects.filter(type_crypt='BTC', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_commission'))['total'] or 0,
        'total_pay_ltc': tg_models.CryptPay.objects.filter(pay_type='LTC', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount'))['total'] or 0,
        'total_withdraw_ltc': tg_models.Withdraw.objects.filter(type_crypt='LTC', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_commission'))['total'] or 0,
        'total_pay_eth': tg_models.CryptPay.objects.filter(pay_type='ETH', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount'))['total'] or 0,
        'total_withdraw_eth': tg_models.Withdraw.objects.filter(type_crypt='ETH', date__gte=start_time, date__lte=end_time).aggregate(total=Sum('amount_commission'))['total'] or 0,
    }
    return data
