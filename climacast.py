
# CLIMACAST: REAL-TIME WEATHER DASHBOARD
#  Import necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import matplotlib.pyplot as plt
from datetime import datetime
# Your personal OpenWeatherMap API key
API_KEY = "b1f79bb503f93984267d71b26b452956"
#  Function: Fetch Current Weather Data

def get_weather(city):
    """
    Fetches real-time weather data for a given city using OpenWeatherMap API.
    Returns a dictionary with temperature, humidity, and weather condition.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        weather = {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"],
            "desc": data["weather"][0]["description"],
        }
        return weather
    else:
        return None
# 🕒 Function: Fetch 12-Hour Forecast
def get_hourly_forecast(city):
    """
    Retrieves next 12-hour forecast (3-hour intervals).
    Returns list of tuples -> (time, temperature, description).
    """
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    resp = requests.get(url)
    forecasts = []

    if resp.status_code == 200:
        data = resp.json()
        for i in range(0, 12):  # Next 12 forecast entries (approx. 36 hours)
            entry = data["list"][i]
            time = datetime.fromtimestamp(entry["dt"]).strftime("%I %p")
            temp = round(entry["main"]["temp"])
            desc = entry["weather"][0]["description"].capitalize()
            forecasts.append((time, temp, desc))
    return forecasts

#  Function: Fetch 5-Day Forecast (Daily Data)

def get_weekly_weather(city):
    """
    Retrieves 5-day forecast data and extracts daily average temperatures.
    Returns two lists: dates and temperatures.
    """
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    resp = requests.get(url)
    temps, days = [], []

    if resp.status_code == 200:
        data = resp.json()
        for i in range(0, len(data["list"]), 8):  # Every 8th record = 1 per day
            entry = data["list"][i]
            temp = entry["main"]["temp"]
            date = entry["dt_txt"].split(" ")[0]
            temps.append(temp)
            days.append(date)
    return days, temps

# 🖥Class: WeatherDashboard (Tkinter GUI)
class WeatherDashboard:
    def _init_(self, root):
        """
        Initializes the weather dashboard window and layout.
        """
        self.root = root
        self.root.title("🌦 Real-time Weather Dashboard")
        self.root.geometry("650x450")
        self.root.configure(bg="#e9f0f7")
        self.city_var = tk.StringVar()
        self.create_widgets()

    # ------------------------------------------------
    #  GUI Layout & Widgets
    # ------------------------------------------------
    def create_widgets(self):
        ttk.Label(
            self.root,
            text="Enter City:",
            background="#e9f0f7",
            font=("Arial", 11, "bold")
        ).grid(row=0, column=0, padx=8, pady=10, sticky="e")

        ttk.Entry(
            self.root, textvariable=self.city_var, width=25
        ).grid(row=0, column=1, padx=5, pady=10)

        # Button Styles (Blue & Green)
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "BrightBlue.TButton",
            background="#00aaff",
            foreground="white",
            padding=8,
            font=("Arial", 10, "bold"),
            borderwidth=3,
            relief="raised",
        )
        style.map(
            "BrightBlue.TButton",
            background=[("active", "#0088cc")],
            relief=[("pressed", "sunken")]
        )

        style.configure(
            "BrightGreen.TButton",
            background="#00cc66",
            foreground="white",
            padding=8,
            font=("Arial", 10, "bold"),
            borderwidth=3,
            relief="raised",
        )
        style.map(
            "BrightGreen.TButton",
            background=[("active", "#00994d")],
            relief=[("pressed", "sunken")]
        )

        # Buttons: Get Weather + Show Trend
        ttk.Button(
            self.root,
            text="Get Weather",
            command=self.show_weather,
            style="BrightBlue.TButton"
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            self.root,
            text="Show Weekly Trend",
            command=self.show_trend,
            style="BrightGreen.TButton"
        ).grid(row=0, column=3, padx=5)

        # Output Text Area
        self.result = tk.Text(
            self.root, height=18, width=75,
            bg="#f7fbff", fg="black",
            font=("Consolas", 10)
        )
        self.result.grid(row=1, column=0, columnspan=4, padx=10, pady=10)
        self.result.config(state='disabled')


    # ------------------------------------------------
    # ☀ Show Current Weather and 12-Hour Forecast
    # ------------------------------------------------
    def show_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        weather = get_weather(city)
        forecast = get_hourly_forecast(city)

        self.result.config(state='normal')
        self.result.delete(1.0, tk.END)

        if weather:
            output = (
                f" City: {weather['city']}\n"
                f" Temperature: {weather['temp']} °C\n"
                f" Humidity: {weather['humidity']}%\n"
                f" Condition: {weather['desc'].capitalize()}\n\n"
                f" Next 12-Hour Forecast:\n"
            )
            self.result.insert(tk.END, output)
            self.result.insert(tk.END, "-" * 55 + "\n")
            for time, temp, desc in forecast:
                self.result.insert(tk.END, f"{time:<10} | {temp:>3}°C | {desc}\n")
        else:
            self.result.insert(tk.END, " Weather data not found. Please check the city name.")

        self.result.config(state='disabled')


    # ------------------------------------------------
    # Show 5-Day Temperature Trend Graph
    # ------------------------------------------------
    def show_trend(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        days, temps = get_weekly_weather(city)
        if days and temps:
            plt.figure(figsize=(8, 4))
            plt.plot(days, temps, marker='o', linestyle='-', color='#00aaff')
            plt.title(f"5-Day Temperature Trend for {city}", fontsize=12, weight='bold')
            plt.xlabel("Date")
            plt.ylabel("Temperature (°C)")
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showerror("Error", "Could not retrieve weekly forecast.")

#  MAIN PROGRAM ENTRY POINT

if _name_ == "_main_":
    root = tk.Tk()
    app = WeatherDashboard(root)
    root.mainloop()
