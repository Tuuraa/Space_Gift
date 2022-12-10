from django import forms

from datetime import datetime


class DatePicker(forms.DateInput):
    input_type = 'date'


class TimePicker(forms.TimeInput):
    input_type = 'time'


class PeriodDateTimePicker(forms.Form):
    start_date = forms.DateField(
        widget=DatePicker(
            attrs={
                'onchange': 'delete_standart_pick(); this.form.submit();',
                'value': datetime.now().strftime("%Y-%m-%d"),
            }
        ), required=False)
    start_time = forms.DateField(
        widget=TimePicker(
            attrs={
                'onchange': 'delete_standart_pick(); this.form.submit();',
                'value': datetime.now().strftime("%H:%M"),
            }), required=False)
    end_date = forms.DateField(
        widget=DatePicker(
            attrs={
                'onchange': 'delete_standart_pick(); this.form.submit();',
                'value': datetime.now().strftime("%Y-%m-%d"),
            }), required=False)
    end_time = forms.DateField(
        widget=TimePicker(
            attrs={
                'onchange': 'delete_standart_pick(); this.form.submit();',
                'value': datetime.now().strftime("%H:%M"),                
            }), required=False)
