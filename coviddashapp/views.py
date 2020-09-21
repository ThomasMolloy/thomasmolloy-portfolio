from django.shortcuts import render

def dash_app(request):

    return render(request, 'covid_dash_app.html')


