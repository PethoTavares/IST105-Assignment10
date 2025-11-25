import random
import requests
from datetime import datetime

from django.shortcuts import render, redirect

from .forms import ContinentForm

from pymongo import MongoClient



MONGODB_HOST = "172.31.69.155"
MONGODB_PORT = 27017

OPENWEATHER_API_KEY = "913f84a6b2789f6c6ef171d888a68a10"


def get_mongo_collection():
    client = MongoClient(f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/")
    db = client["assignment10_db"]
    collection = db["search_history"]
    return collection


def continent_form_view(request):
    if request.method == "POST":
        form = ContinentForm(request.POST)
        if form.is_valid():
            continent = form.cleaned_data["continent"]
            return redirect(f"/results/?continent={continent}")
    else:
        form = ContinentForm()

    return render(request, "continent_form.html", {"form": form})


def search_results_view(request):
    continent = request.GET.get("continent", None)

    if not continent:
        return redirect("/")

    # 1) REST Countries API
    countries_url = f"https://restcountries.com/v3.1/region/{continent}"

    try:
        resp = requests.get(countries_url, timeout=10)
        resp.raise_for_status()
        countries_data = resp.json()
    except Exception as e:
        return render(request, "search_results.html", {
            "continent": continent,
            "results": [],
            "error": f"Error fetching countries: {e}",
        })

    if not countries_data:
        return render(request, "search_results.html", {
            "continent": continent,
            "results": [],
            "error": "No countries found for this region.",
        })


    if len(countries_data) <= 5:
        sample_countries = countries_data
    else:
        sample_countries = random.sample(countries_data, 5)

    results = []

    
    for country in sample_countries:
        name = country.get("name", {}).get("common", "Unknown")
        capital_list = country.get("capital", [])
        if not capital_list:
            continue
        capital = capital_list[0]

        weather_url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={capital}&appid={OPENWEATHER_API_KEY}&units=metric"
        )

        try:
            w_resp = requests.get(weather_url, timeout=10)
            w_resp.raise_for_status()
            w_data = w_resp.json()

            temp = w_data.get("main", {}).get("temp")
            description = w_data.get("weather", [{}])[0].get("description", "No description")

            results.append({
                "country": name,
                "capital": capital,
                "temperature": temp,
                "description": description,
            })
        except Exception:
           
            continue

    # 4) Salvar histórico no MongoDB
    collection = get_mongo_collection()
    history_doc = {
        "continent": continent,
        "results": results,
        "created_at": datetime.utcnow(),
    }
    collection.insert_one(history_doc)

    context = {
        "continent": continent,
        "results": results,
    }
    return render(request, "search_results.html", context)


def history_view(request):
    collection = get_mongo_collection()
    cursor = collection.find().sort("created_at", -1).limit(10)
    history = list(cursor)

    return render(request, "history.html", {"history": history})

