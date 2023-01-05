from django.db import models
from django.db.models import signals
from django.dispatch import receiver

import tg_panel.utils


class Clones(models.Model):
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clones'


STATUS_CHOICES = (
    ('WAIT_PAYMENT_TYPE', '⏳ В ожидании способа оплаты'),
    ('CANCELED', '⛔️ Отменен'),
    ('WAIT_PAYMENT', '⏳ В ожидании оплаты'),
    ('SUCCESSFULLY_PAYED', '⏳ Успешно оплачено, ожидайте выплату'),
    ('OPERATION_COMPLETED', '✅ Операция проведена'),
    ('OPERATION_ERROR', '⚠️ Ошибка при выполнении операции')
)

BOOLCHOISES = (
    (False, 'Не актив'),
    (True, 'Актив'),
)

class CryptPay(models.Model):
    amount = models.DecimalField(verbose_name='Сумма', max_digits=10, decimal_places=2, blank=True, null=True)
    user_id = models.IntegerField(verbose_name='ID пользователя', blank=True, null=True)
    date = models.DateField(verbose_name='Дата', blank=True, null=True)
    pay_type = models.TextField(verbose_name='Тип криптовалюты', blank=True, null=True)  
    cancel_id = models.TextField(verbose_name='ID отмены', blank=True, null=True)
    status = models.TextField(verbose_name='Статус', choices=STATUS_CHOICES, default='FALSE')
    amount_rub = models.DecimalField(verbose_name='Сумма в рублях', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Крипто-пополнение'
        verbose_name_plural = 'Крипто-пополнения'
        managed = False
        db_table = 'crypt_pay'


class Helper(models.Model):
    from_id = models.IntegerField()
    to_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'helper'


class Pay(models.Model):
    pay_id = models.IntegerField(verbose_name='ID')
    pay_amount = models.IntegerField(verbose_name='Сумма')
    date = models.DateField(verbose_name='Дата')
    pay_type = models.TextField(verbose_name='Тип')
    user_id = models.IntegerField(verbose_name='ID пользователя')
    cancel_id = models.IntegerField(verbose_name='ID отмены')
    status = models.TextField(verbose_name='Статус', choices=STATUS_CHOICES, default='FALSE')

    class Meta:
        verbose_name = 'Пополнение'
        verbose_name_plural = 'Пополнения'
        managed = False
        db_table = 'pay'


class Transaction(models.Model):
    amount = models.DecimalField(verbose_name='Сумма', max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.TextField(verbose_name='Валюта', blank=True, null=True)
    date = models.DateField(verbose_name='Дата', blank=True, null=True)
    wallet = models.TextField(verbose_name='Кошелек', blank=True, null=True)
    status = models.TextField(verbose_name='Статус', blank=True, null=True)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        managed = False
        db_table = 'transactions'


class TgUser(models.Model):
    user_id = models.IntegerField(verbose_name='ID пользователя', unique=True)
    referrer_id = models.TextField(verbose_name='ID реферала', blank=True, null=True)
    name = models.TextField(verbose_name='Имя пользователя')
    date = models.DateField(verbose_name='Дата', blank=True, null=True)
    money = models.IntegerField(verbose_name='Кошелек', blank=True, null=True)
    date_now = models.DateTimeField(verbose_name='Дата последнего начисления', blank=True, null=True)
    link_name = models.TextField(verbose_name='Ссылка на пользователя', blank=True, null=True)
    depozit = models.IntegerField(verbose_name='Депозит', blank=True, null=True)
    gift_value = models.IntegerField(blank=True, null=True)
    now_depozit = models.IntegerField(verbose_name='Текущий депозит', blank=True, null=True)
    planet = models.TextField(verbose_name='Планета', blank=True, null=True)
    step = models.TextField(verbose_name='Уровень', blank=True, null=True)
    first_dep = models.BooleanField(verbose_name='Первое пополнение')
    status = models.BooleanField(verbose_name='Статус', blank=True, null=True, choices=BOOLCHOISES, default=False)
    count_ref = models.IntegerField(verbose_name='Кол-во рефералов', blank=True, null=True)
    active = models.BooleanField(verbose_name='Актив', blank=True, null=True, choices=BOOLCHOISES, default=False)
    gift_money = models.IntegerField(verbose_name='Деньги для вывода', blank=True, null=True)
    amount_gift_money = models.IntegerField(verbose_name='Деньги с системы дарения', blank=True, null=True)
    ref_money = models.IntegerField(verbose_name='Деньги с рефералов', blank=True, null=True)
    jump = models.BooleanField(blank=True, null=True)
    last_withd = models.DateTimeField(blank=True, null=True, auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        managed = False
        db_table = 'users'


WIDTHDRAW_CHOISES = (
    ('CANCEL', 'Отмена'),
    ('WAIT', 'В обработке'),
    ('GOOD', 'Принято'),
)


class Withdraw(models.Model):
    card = models.TextField(verbose_name='Карта', )
    type = models.TextField(verbose_name='Тип', )
    amount = models.IntegerField(verbose_name='Сумма', )
    data = models.TextField(verbose_name='Доп. данные', )
    user_id = models.IntegerField(verbose_name='ID пользователя', )
    date = models.DateTimeField(verbose_name='Дата', )
    status = models.CharField(verbose_name='Статус', max_length=45, choices=WIDTHDRAW_CHOISES, default='WAIT')
    amount_commission = models.DecimalField(verbose_name='Сумма с комиссией', max_digits=10, decimal_places=2, blank=True, null=True)
    amount_crypt = models.FloatField(verbose_name='Сумма в криптовалюте', blank=True, null=True)
    type_crypt = models.CharField(verbose_name='Тип криптовалюты', max_length=10, blank=True, null=True)

    class Meta:
        verbose_name = 'Вывод'
        verbose_name_plural = 'Выводы'
        managed = False
        db_table = 'withdraw'


@receiver(signals.post_save, sender=Withdraw)
def send_withdraw_status_to_user(sender, instance, created, *args,  **kwargs):
    if instance.status != 'WAIT':
        bot_token = ApiTokens.objects.get(title='api_bot')
        tg_panel.utils.tg_send_message(instance.user_id, bot_token.token, instance.status)



class ApiTokens(models.Model):
    title = models.CharField(verbose_name='Название', max_length=100, unique=True)
    api = models.CharField(verbose_name='Токен', max_length=300)

    class Meta:
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'


class Statistic(TgUser):
    class Meta:
        proxy = True
        managed = False
        db_table = 'users'
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'


class AllStats(TgUser):
    class Meta:
        proxy = True
        verbose_name = 'Общая статистика'
        verbose_name_plural = 'Общая статистика'


class RefMoney(models.Model):
    user_id = models.IntegerField(verbose_name='ID пользователя', )
    ref_id = models.IntegerField(verbose_name='ID реферала', )
    money = models.DecimalField(verbose_name='Сумма', max_digits=10, decimal_places=2)
    date = models.DateTimeField(verbose_name='Дата', )
    class Meta:
        managed = False
        db_table = 'ref_money'
