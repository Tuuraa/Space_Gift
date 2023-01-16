from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from .models import TgUser


def index(request, *args, **kwargs):
    return redirect('admin-page')
