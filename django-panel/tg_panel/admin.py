import pytz
import telebot
from decimal import Decimal
from django.contrib import admin
from  django.contrib.auth.models  import  Group
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum
from daterange_filter.filter import DateRangeFilter

from .models import TgUser, Pay, CryptPay, Transaction, Withdraw, ApiTokens, Statistic, AllStats, Post, RefMoney, Clones
from .forms import PeriodDateTimePicker

from . import utils

from datetime import datetime, date, timedelta, timezone


HTML_TAGS = '''
</br>
Доступные html теги:</br>
</br>
&lt;b&gt;bold&lt;/b&gt;, &lt;strong&gt;bold&lt;/strong&gt; - <b>жирный текст</b></br>
&lt;i&gt;italic&lt;/i&gt;, &lt;em&gt;italic&lt;/em&gt; - <b>курсив</b></br>
&lt;a href="http://www.example.com/"&gt;inline URL&lt;/a&gt; - <b>ссылка</b></br>
&lt;a href="tg://user?id=123456789"&gt;inline mention of a user&lt;/a&gt; - <b>упоминание пользователя</b></br>
&lt;code&gt;inline fixed-width code&lt;/code&gt; - <b>код</b></br>
&lt;pre&gt;pre-formatted fixed-width code block&lt;/pre&gt; - <b>блок кода</b></br>
</br>
'''

STANDART_DATE_PICKER = {
    'day': lambda: (datetime.now(timezone.utc) - timedelta(days=1)),
    'week': lambda: (datetime.now(timezone.utc) - timedelta(days=7)),
    'month': lambda: (datetime.now(timezone.utc) - timedelta(days=31)),
}

bot = telebot.TeleBot(ApiTokens.objects.get(api='bot_api').title)
bot.token = ApiTokens.objects.get(api='bot_api').title


class TgUserAdmin(admin.ModelAdmin):
    search_fields = ('user_id', 'name')
    list_filter = ('name', 'user_id', 'referrer_id')
    list_display = ('name', 'depozit', 'get_widhdraws', 'get_referrer', 'stats_link', 'count_ref')
    readonly_fields = ('user_id', 'name', 'date', 'money', 'date_now', 'link_name', 'gift_value', 'now_depozit', 'first_dep')
    exclude = ('last_withd', 'jump', 'gift_value', 'now_depozit')
    
    def get_widhdraws(self, obj):
        count = Withdraw.objects.filter(user_id=obj.user_id).count()
        return format_html('<a href="/admin/tg_panel/withdraw/?user_id={}">{} Withdraws</a>', obj.user_id, count)
    
    get_widhdraws.short_description = "Вывод"

    def get_referrer(self, obj):
        referrer = TgUser.objects.filter(user_id=obj.referrer_id)
        
        if referrer.count() == 0:
            return format_html('-')
        
        referrer = referrer[0]
        text_to_out = referrer.name or referrer.user_id
        
        return format_html('<a href="/admin/tg_panel/tguser/{}/change/">Пригласивший: {}</a>', referrer.pk, text_to_out)
    
    def stats_link(self, obj):
        return format_html(f'<a href="/admin/tg_panel/statistic/{obj.pk}/change/">Статистика</a>')
    
    stats_link.short_description = "Статистика"
    get_referrer.short_description = "Пригласивший"


class PayAdmin(admin.ModelAdmin):
    def user_link(self):
        user = TgUser.objects.filter(user_id=self.user_id).first()
        if user is not None:
            if user.link_name is not None:
                return mark_safe(f'<a href="/admin/tg_panel/tguser/{user.id}/change/">@{user.link_name}</a>')
            else:
                return mark_safe(f'<a href="/admin/tg_panel/tguser/{user.id}/change/">{user.name} ({user.user_id})</a>')
    user_link.short_description = 'Пользователь'

    search_fields = ('pay_id', 'user_id', 'get_pay_amount')
    list_display = ('pay_id', user_link, 'get_pay_amount', 'date', 'status')
    readonly_fields = ('pay_id', 'get_pay_amount', 'date', 'pay_type', 'user_id', 'cancel_id')
    exclude = ('pay_amount', )

    def get_pay_amount(self, obj):
        return format_html(f'{obj.pay_amount} Руб.')
    get_pay_amount.short_description = 'Сумма'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True

        return obj.status == 'WAIT_PAYMENT'

    def save_model(self, request, obj, form, change):
        user = TgUser.objects.filter(user_id=obj.user_id).first()

        super().save_model(request, obj, form, change)

        if obj.status == 'CANCELED':
            bot.send_message(user.user_id, text=f'⛔️ Ваша заявка на пополнение №{obj.pay_id} была отменена администратором', parse_mode='html')
            return
        elif obj.status == 'OPERATION_COMPLETED':
            if user.referrer_id is not None:
                ref_user = TgUser.objects.filter(user_id=user.referrer_id).first()
                if ref_user is not None and (user.depozit != 0 or user.status or int(user.planet) != 0):
                    ref_income = obj.pay_amount * .1
                    utc_now = pytz.utc.localize(datetime.utcnow())
                    date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

                    RefMoney.objects.create(user_id=user.user_id, ref_id=ref_user.user_id, money=ref_income, date=date_time_now)

                    ref_user.money += Decimal(ref_income)
                    ref_user.percent_ref_money += ref_income
                    ref_user.save()

                    try:
                        if user.link_name is not None:
                            user_name = f'@{user.link_name}'
                        else:
                            user_name = f'{user.name} ({user.user_id})'

                        bot.send_message(ref_user.user_id, text=f'Ваш реферал {user_name} пополнил баланс и вам подарили {int(ref_income)} RUB', parse_mode='html')
                    except Exception:
                        pass
            user.depozit += obj.pay_amount
            user.money += obj.pay_amount

            user.save()

            try:
                bot.send_message(user.user_id, text=f"Платеж №{obj.pay_id} успешно выполнен. Ваш счет пополнен на {obj.pay_amount} руб.", parse_mode='html')
            except Exception:
                pass

            if user.status == 1 or int(user.planet) > 0:
                #clones_count = int(obj.pay_amount / 5000)
                #for clone in range(0, clones_count):
                #    Clones.objects.create(active=True)

                count_ref = int(obj.pay_amount/10_000)

                user.activate_ref_count += count_ref
                user.count_ref += count_ref
                user.save()


class CryptPayAdmin(admin.ModelAdmin):
    def user_link(self):
        user = TgUser.objects.filter(user_id=self.user_id).first()
        if user is not None:
            if user.link_name is not None:
                return mark_safe(f'<a href="/admin/tg_panel/tguser/{user.id}/change/">@{user.link_name}</a>')
            else:
                return mark_safe(f'<a href="/admin/tg_panel/tguser/{user.id}/change/">{user.name} ({user.user_id})</a>')
    user_link.short_description = 'Пользователь'

    search_fields = ('id', 'user_id', 'amount_rub')
    list_display = ('id', user_link, 'get_amount_rub', 'get_amount', 'date', 'status')
    readonly_fields = ('get_amount', 'user_id', 'date', 'pay_type', 'cancel_id', 'get_amount_rub')
    exclude = ('amount', 'amount_rub')

    def get_amount_rub(self, obj):
        return format_html(f'{int(obj.amount_rub)} руб')
    get_amount_rub.short_description = 'Сумма'

    def get_amount(self, obj):
        return format_html(f'{obj.amount} {obj.pay_type}')
    get_amount.short_description = 'Сумма в криптовалюте'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True

        return obj.status == 'WAIT_PAYMENT'

    def save_model(self, request, obj, form, change):
        user = TgUser.objects.filter(user_id=obj.user_id).first()

        super().save_model(request, obj, form, change)

        if obj.status == 'CANCELED':
            bot.send_message(user.user_id, text=f'⛔️ Ваша заявка на пополнение №{obj.id} была отменена администратором', parse_mode='html')
            return
        elif obj.status == 'OPERATION_COMPLETED':
            if user.referrer_id is not None:
                ref_user = TgUser.objects.filter(user_id=user.referrer_id).first()
                if ref_user is not None and (user.depozit != 0 or user.status or int(user.planet) != 0):
                    ref_income = float(obj.amount_rub) * .1
                    utc_now = pytz.utc.localize(datetime.utcnow())
                    date_time_now = utc_now.astimezone(pytz.timezone("UTC"))

                    RefMoney.objects.create(user_id=user.user_id, ref_id=ref_user.user_id, money=ref_income, date=date_time_now)

                    ref_user.money += Decimal(ref_income)
                    ref_user.percent_ref_money += ref_income
                    ref_user.save()

                    try:
                        if user.link_name is not None:
                            user_name = f'@{user.link_name}'
                        else:
                            user_name = f'{user.name} ({user.user_id})'

                        bot.send_message(ref_user.user_id, text=f'Ваш реферал {user_name} пополнил баланс и вам подарили {int(ref_income)} RUB', parse_mode='html')
                    except Exception:
                        pass
            user.depozit += float(obj.amount_rub)
            user.money += obj.amount_rub
            user.save()
            try:
                bot.send_message(user.user_id, text=f"Платеж №{obj.id} успешно выполнен. Ваш счет пополнен на {int(obj.amount_rub)} руб.", parse_mode='html')
            except Exception:
                pass

            if user.status == 1 or int(user.planet) > 0:
                #clones_count = int(obj.amount_rub / 5000)
                #for clone in range(0, clones_count):
                #    Clones.objects.create(active=True)

                count_ref = int(obj.amount_rub/10_000)

                user.activate_ref_count += count_ref
                user.count_ref += count_ref
                user.save()


class WithdrawAdmin(admin.ModelAdmin):

    def user_link(self):
        user = TgUser.objects.filter(user_id=self.user_id).first()
        if user is not None:
            if user.link_name is not None:
                return mark_safe(f'<a href="/admin/tg_panel/tguser/{user.id}/change/">@{user.link_name}</a>')
            else:
                return mark_safe(f'<a href="/admin/tg_panel/tguser/{user.id}/change/">{user.name} ({user.user_id})</a>')
    user_link.short_description = 'Пользователь'

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True

        return obj.status == 'WAIT'

    def save_model(self, request, obj, form, change):
        user = TgUser.objects.filter(user_id=obj.user_id).first()

        if obj.status == 'CANCEL':
            user.gift_money += obj.amount
            user.save()

        super().save_model(request, obj, form, change)

        bot_token = ApiTokens.objects.get(api='bot_api')
        utils.tg_send_message(obj, bot_token.title)

    def sum(self):
        if self.type == 'crypt':
            return f'{self.amount_crypt} {self.type_crypt}'
        elif self.type == 'bank':
            return f'{int(self.amount_commission)} RUB'
    sum.short_description = 'Сумма с комиссией'

    search_fields = ('user_id',)
    readonly_fields = ('card', 'type', 'data', 'user_id', 'date', 'amount_commission', 'amount_crypt','type_crypt')
    list_display = ('id', user_link, sum, 'card', 'type', 'data', 'status')
    list_filter = ('user_id', 'amount', 'card', 'type', 'data', ('date', DateRangeFilter),)
    exclude = ('amount',)


class TokenAdmin(admin.ModelAdmin):
    list_display = ('title', 'api')


class StatAdmin(admin.ModelAdmin):
    change_form_template = 'admin/statis_view.html'

    def change_view(self, request, object_id, form_url="", extra_context=None):
        start_date_filter, end_date_filter = None, None

        if request.GET.get('start_time') and not request.GET.get('standart_period'):
            start_date = datetime.strptime(request.GET['start_date'], "%Y-%m-%d")
            start_time = datetime.strptime(request.GET['start_time'], "%H:%M")
            end_date = datetime.strptime(request.GET['end_date'], "%Y-%m-%d")
            end_time = datetime.strptime(request.GET['end_time'], "%H:%M")

            start_date_filter = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=start_time.hour, minute=start_time.minute)
            end_date_filter = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_time.hour, minute=end_time.minute)

        if request.GET.get('standart_period'):
            end_date_filter = datetime.now(timezone.utc)
            start_date_filter = STANDART_DATE_PICKER[request.GET['standart_period']]()

        context = utils.get_statistic(object_id, start_date_filter, end_date_filter)

        if start_date_filter is None:
            start_date_filter = datetime.now(timezone.utc)
        
        if end_date_filter is None:
            end_date_filter = datetime.now(timezone.utc)

        period_picker_data = {
            'end_date': end_date_filter.strftime("%Y-%m-%d"),'end_time': end_date_filter.strftime("%H:%M"),
            'start_date': start_date_filter.strftime("%Y-%m-%d"),'start_time': start_date_filter.strftime("%H:%M"),
        }
        
        context['period_picker'] = PeriodDateTimePicker(period_picker_data)

        return super().change_view(request, object_id, form_url, extra_context=context)


class AllStatsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/user_summary_change_list.html'

    def changelist_view(self, request, extra_context=None):
        print(request.POST)
        start_date_filter, end_date_filter = None, None

        if request.POST.get('start_time') and not request.POST.get('standart_period'):
            start_date = datetime.strptime(request.POST['start_date'], "%Y-%m-%d")
            start_time = datetime.strptime(request.POST['start_time'], "%H:%M")
            end_date = datetime.strptime(request.POST['end_date'], "%Y-%m-%d")
            end_time = datetime.strptime(request.POST['end_time'], "%H:%M")

            start_date_filter = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=start_time.hour, minute=start_time.minute)
            end_date_filter = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_time.hour, minute=end_time.minute)

        if request.POST.get('standart_period'):
            end_date_filter = datetime.now(timezone.utc)
            start_date_filter = STANDART_DATE_PICKER[request.POST['standart_period']]()

        context = utils.get_all_stats(start_date_filter, end_date_filter)
        
        if start_date_filter is None:
            start_date_filter = datetime.now(timezone.utc)
        
        if end_date_filter is None:
            end_date_filter = datetime.now(timezone.utc)

        period_picker_data = {
            'end_date': end_date_filter.strftime("%Y-%m-%d"),'end_time': end_date_filter.strftime("%H:%M"),
            'start_date': start_date_filter.strftime("%Y-%m-%d"),'start_time': start_date_filter.strftime("%H:%M"),
        }
        
        context['period_picker'] = PeriodDateTimePicker(period_picker_data)
        return super().changelist_view(request, extra_context=context)


class PostAdmin(admin.ModelAdmin):
    list_display = ['created', 'status', 'amount_of_receivers', 'photo', 'video', 'message', 'html_button']
    list_display_links = ['created']

    search_fields = ['message', 'button_text', 'button_url']
    list_filter = ['status']

    list_per_page = 10

    def html_button(self, obj):
        if obj.button_text and obj.button_url:
            return format_html(f'<a href="{obj.button_url}" target="_blank">{obj.button_text}</a>')
        else:
            return ''
    html_button.short_description = 'Кнопка'

    def get_fieldsets(self, request, obj=None):
        base_fieldsets = [
            (
                'Сообщение',
                {
                    'fields': [
                        'photo',
                        'video',
                        'message',
                        ('button_text', 'button_url'),
                    ],
                    'description': HTML_TAGS
                }
            ),
            (
                'Откладывание поста',
                {
                    'fields': [
                        'postpone',
                        'postpone_time',
                    ]
                }
            ),
        ]

        if not obj:
            return base_fieldsets
        else:
            return [
                (
                    'Общая информация',
                    {
                        'fields': [
                            'created',
                            'status'
                        ] + (
                            ['amount_of_receivers'] if obj.status == 'done' else []
                        )
                    }
                ),
            ] + base_fieldsets

    def get_readonly_fields(self, request, obj=None):
        return ['created', 'status', 'amount_of_receivers']

    def has_change_permission(self, request, obj=None):
        return (obj is None) or (obj.status in ['postponed'])

    def has_delete_permission(self, request, obj=None):
        return (obj is None) or (obj.status in ['postponed', 'queue', 'done'])

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False

        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False

        return super().change_view(request, object_id, form_url, extra_context)

    class Media:
        js = ('admin/js/post.js',)


admin.site.register(TgUser, TgUserAdmin)
admin.site.register(Pay, PayAdmin)
admin.site.register(CryptPay, CryptPayAdmin)
admin.site.register(Withdraw, WithdrawAdmin)
admin.site.register(ApiTokens, TokenAdmin)
admin.site.unregister(Group)
admin.site.register(Statistic, StatAdmin)
admin.site.register(AllStats, AllStatsAdmin)
admin.site.register(Post, PostAdmin)
