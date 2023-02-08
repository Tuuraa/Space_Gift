import random
from datetime import datetime
from string import ascii_lowercase
from django.core.exceptions import ValidationError

from django.db import models
from django.db.models import signals
from django.dispatch import receiver


class Clones(models.Model):
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clones'


STATUS_CHOICES = (
    ('CANCELED', '⛔️ Отменен'),
    ('WAIT_PAYMENT', '⏳ В ожидании оплаты'),
    ('OPERATION_COMPLETED', '✅ Операция проведена'),
)

WITHDRAWAL_TYPES = (
    ('bank', '💳 Рубли на карту'),
    ('crypt', '🪙 Криптовалюта'),
)

BOOLCHOISES = (
    (False, 'Не актив'),
    (True, 'Актив'),
)


class CryptPay(models.Model):
    amount = models.DecimalField(verbose_name='Сумма', max_digits=10, decimal_places=2, blank=True, null=True)
    user_id = models.TextField(verbose_name='ID пользователя', blank=True, null=True)
    date = models.DateField(verbose_name='Дата', blank=True, null=True)
    pay_type = models.TextField(verbose_name='Тип криптовалюты', blank=True, null=True)
    cancel_id = models.TextField(verbose_name='ID отмены', blank=True, null=True)
    status = models.TextField(verbose_name='Статус', choices=STATUS_CHOICES, default='FALSE')
    amount_rub = models.DecimalField(verbose_name='Сумма в рублях', max_digits=10, decimal_places=2, blank=True, null=True)
    in_advance = models.BooleanField(verbose_name='Предоплата', default=False)


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
    pay_id = models.IntegerField(verbose_name='ID (у нас и в обменнике)')
    pay_amount = models.IntegerField(verbose_name='Сумма')
    date = models.DateField(verbose_name='Дата')
    pay_type = models.TextField(verbose_name='Тип')
    user_id = models.TextField(verbose_name='ID пользователя')
    cancel_id = models.IntegerField(verbose_name='ID отмены')
    status = models.TextField(verbose_name='Статус', choices=STATUS_CHOICES, default='FALSE')
    in_advance = models.BooleanField(verbose_name='Предоплата', default=False)
    
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
    user_id = models.TextField(verbose_name='ID пользователя', unique=True)
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
    activate_ref_count = models.IntegerField(verbose_name='Активные рефералы', blank=True, null=True)
    remove_dep = models.IntegerField(verbose_name='Депозит доступный для вывода', blank=True, null=True, editable=False)
    percent_ref_money = models.FloatField(verbose_name='Заработок с рефералов', blank=True, null=True, editable=False)
    gift_money_invest = models.FloatField(verbose_name='Деньги на вывод с инвестиций', blank=True, null=True, editable=False)
    reinvest = models.FloatField(verbose_name='Реинвестирование с системы дарения', blank=True, null=True, editable=False)
    archive_dep = models.FloatField(verbose_name='Архив с системы дарения', blank=True, null=True)
    last_month_active = models.IntegerField(blank=True, null=True)
    last_month_ref_count = models.IntegerField(verbose_name='Рефералы с прошлого месяца', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        managed = False
        db_table = 'users'


WIDTHDRAW_CHOISES = (
    ('CANCEL', '⛔️ Отменен'),
    ('WAIT', '⏳ В ожидании оплаты'),
    ('GOOD', '✅ Операция проведена'),
)


class Withdraw(models.Model):
    card = models.TextField(verbose_name='Реквизиты', )
    type = models.TextField(verbose_name='Тип', choices=WITHDRAWAL_TYPES)
    amount = models.IntegerField(verbose_name='Сумма', )
    data = models.TextField(verbose_name='Доп. данные', )
    user_id = models.TextField(verbose_name='ID пользователя', )
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


class ApiTokens(models.Model):
    title = models.CharField(verbose_name='Название', max_length=100, unique=True)
    api = models.CharField(verbose_name='Токен', max_length=300)

    class Meta:
        managed = False
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'
        db_table = 'tokens'


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
    user_id = models.TextField(verbose_name='ID пользователя', )
    ref_id = models.TextField(verbose_name='ID реферала', )
    money = models.DecimalField(verbose_name='Сумма', max_digits=10, decimal_places=2)
    date = models.DateTimeField(verbose_name='Дата', )
    class Meta:
        managed = False
        db_table = 'ref_money'


class Photo(models.ImageField):
    max_size_mb = 20

    def __init__(self, *args, **kwargs):
        kwargs['upload_to'] = self.get_path
        kwargs['validators'] = [self.validate_image]

        return super().__init__(*args, **kwargs)

    def get_path(self, instance, filename, length=10):
        file_format = filename.split('.')[-1].lower()

        filename = ''
        for index in range(length):
            filename += random.choice(ascii_lowercase)

        return f'{filename}.{file_format}'

    def validate_image(self, image):
        image_size_bytes = image.file.size
        max_size_bytes = self.max_size_mb * 1024 * 1024

        if image_size_bytes > max_size_bytes:
            raise ValidationError(f'Максимальный размер файла - {self.max_size_mb} МБ')


class Post(models.Model):
    created = models.DateTimeField('Дата создания, UTC',
        auto_now_add=True
    )
    status = models.CharField('Статус',
        max_length=9,
        choices=[
            ('created', 'Создан'),
            ('postponed', 'Отложен'),
            ('queue', 'В очереди'),
            ('process', 'Рассылается'),
            ('done', 'Разослан')
        ],
        default='created'
    )

    photo = Photo('Изображение до 5МБ',
        blank=True, null=True
    )

    video = models.FileField('Видео', blank=True, null=True)

    message = models.TextField('Форматированный текст, до 1024 символов',
        max_length=1024
    )
    button_text = models.CharField('Текст кнопки',
        max_length=50, blank=True, null=True
    )
    button_url = models.URLField('Ссылка кнопки',
        blank=True, null=True
    )

    postpone = models.BooleanField('Отложить',
        default=False
    )
    postpone_time = models.DateTimeField('Время публикации, UTC',
        default=datetime(2020, 1, 1)
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.postpone:
                self.status = 'postponed'
            else:
                self.status = 'queue'

        elif self.status == 'postponed' and not self.postpone:
            self.status = 'queue'

        if not self.button_text or not self.button_url:
            self.button_text = None
            self.button_url = None

        super().save(*args, **kwargs)

    amount_of_receivers = models.IntegerField('Количество получателей',
        blank=True, null=True
    )

    def __str__(self):
        time_isoformat = self.created.isoformat(sep=' ', timespec='seconds')
        time_isoformat = time_isoformat[:time_isoformat.index('+')]

        return time_isoformat

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        managed = False
        db_table = 'posts'


class AdvancePay(models.Model):
    user_id = models.TextField(verbose_name='ID пользователя')
    date = models.DateTimeField(verbose_name='Дата')

    class Meta:
        verbose_name = 'Предоплата'
        verbose_name_plural = 'Предоплаты'
        managed = False
        db_table = 'advance_pay'
