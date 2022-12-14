from django.shortcuts import render, redirect


def index(request, *args, **kwargs):
    return redirect('admin-page')
