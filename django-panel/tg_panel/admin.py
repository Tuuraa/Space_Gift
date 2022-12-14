from django.contrib import admin
from  django.contrib.auth.models  import  Group
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum
from jet.filters import DateRangeFilter

from .models import TgUser, Pay, CryptPay, Transaction, Withdraw, ApiTokens, Statistic, AllStats
from .forms import PeriodDateTimePicker

import tg_panel.utils

from datetime import datetime, date, timedelta, timezone


STANDART_DATE_PICKER = {
    'day': lambda: (datetime.now(timezone.utc) - timedelta(days=1)),
    'week': lambda: (datetime.now(timezone.utc) - timedelta(days=7)),
    'month': lambda: (datetime.now(timezone.utc) - timedelta(days=31)),
}


class TgUserAdmin(admin.ModelAdmin):
    search_fields = ('user_id', 'name')
    list_filter = ('name', 'user_id', 'referrer_id')
    list_display = ('name', 'depozit', 'get_widhdraws', 'get_referrer', 'stats_link', 'count_ref')
    readonly_fields = ('user_id', 'name', 'date', 'money', 'date_now', 'link_name', 'gift_value', 'now_depozit', 'first_dep', 'count_ref')
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
    search_fields = ('pay_id', 'pay_type', 'date')
    list_display = ('pay_id', 'get_pay_amount', 'date', 'pay_type', 'user_id', 'cancel_id', 'status')
    readonly_fields = ('pay_id', 'get_pay_amount', 'date', 'pay_type', 'user_id', 'cancel_id')
    exclude = ('pay_amount', )
    list_editable = ('status',)
    list_filter = (
        ('date', DateRangeFilter),
        'user_id',
    )

    def get_pay_amount(self, obj):
        return format_html(f'{obj.pay_amount} Руб.')
    get_pay_amount.short_description = 'Сумма'


class CryptPayAdmin(admin.ModelAdmin):
    search_fields = ('pay_id', 'pay_type', 'date')
    list_display = ('get_amount_rub', 'get_amount','pay_type', 'date', 'user_id', 'cancel_id', 'status')
    readonly_fields = ('get_amount', 'user_id', 'date', 'pay_type', 'cancel_id', 'get_amount_rub')
    exclude = ('amount', 'amount_rub')
    list_editable = ('status',)
    list_filter = (
        ('date', DateRangeFilter),
        'user_id',
    )

    def get_amount_rub(self, obj):
        return format_html(f'{obj.amount_rub} Руб.')
    get_amount_rub.short_description = 'Сумма'

    def get_amount(self, obj):
        return format_html(f'{obj.amount} {obj.pay_type}')
    get_amount.short_description = 'Сумма в криптовалюте'


class WithdrawAdmin(admin.ModelAdmin):
    search_fields = ('user_id',)
    readonly_fields = ('card', 'type', 'get_amount', 'data', 'user_id', 'date', 'amount_commission', 'amount_crypt', 'type_crypt')
    list_display = ('user_id', 'get_amount', 'card', 'type', 'data', 'status')
    list_filter = ('user_id', 'amount', 'card', 'type', 'data', ('date', DateRangeFilter),)
    list_editable = ('status',)
    exclude = ('amount',)

    def get_amount(self, obj):
        return format_html(str(obj.amount) + ' Руб.')

    get_amount.short_description = 'Сумма'

    def get_rangefilter_created_at_default(self, request):
        return (datetime.date.today, datetime.date.today)


class TokenAdmin(admin.ModelAdmin):
    list_display = ('title', 'api')


class StatAdmin(admin.ModelAdmin):
    change_form_template = 'admin/statis_view.html'
    def change_view(self, request, object_id, form_url = "", extra_context=None):
        start_date_filter , end_date_filter = None, None

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

        context = tg_panel.utils.get_statistic(object_id, start_date_filter, end_date_filter)

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
        start_date_filter , end_date_filter = None, None

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

        context = tg_panel.utils.get_all_stats(start_date_filter, end_date_filter)
        
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




admin.site.register(TgUser, TgUserAdmin)
admin.site.register(Pay, PayAdmin)
admin.site.register(CryptPay, CryptPayAdmin)
admin.site.register(Withdraw, WithdrawAdmin)
admin.site.register(ApiTokens, TokenAdmin)
admin.site.unregister(Group)
admin.site.register(Statistic, StatAdmin)
admin.site.register(AllStats, AllStatsAdmin)
