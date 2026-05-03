from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# 🔑 OpenWeather API
API_KEY = "e8f2e5039b7871be2f50a6baebfe123a"

# 🌾 Crop Water Requirement (liters per acre)
CROP_WATER_REQUIREMENTS = {

    "rice": 130000,
    "sugarcane": 200000,
    "maize": 550000,
    "cotton": 1000000,
    "groundnut": 450000,
    "redgram": 350000,
    "greengram": 280000,
    "blackgram": 280000,
    "sunflower": 400000,
    "chilli": 900000,
    "turmeric": 1400000,
    "banana": 2200000,
    "mango": 700000,
    "tomato": 650000,
    "onion": 550000
}

# 💧 Soil Moisture Factor
MOISTURE_FACTORS = {

    "dry": 1.0,
    "moist": 0.6,
    "wet": 0.0

}

# 🌍 Soil Water Retention Factor
SOIL_FACTORS = {

    "Clayey / Alluvial Soil": 0.9,
    "Deep Loamy Soil": 1.0,
    "Well-drained Loamy Soil": 1.0,
    "Black Soil (Regur)": 0.95,
    "Sandy Loam Soil": 1.1,
    "Red Loamy Soil": 1.05,
    "Clay Loam Soil": 1.0,
    "Well-drained Loam Soil": 1.0,
    "Sandy Loam / Black Soil": 1.1,
    "Fertile Loamy Soil": 1.0,
    "Rich Loamy Soil": 1.0,
    "Well-drained Red Soil": 1.05

}

# 🌐 Home Page
@app.route('/')
def home():
    return render_template("frontend.html")


# 🌡 Temperature API
@app.route('/get_temperature')
def get_temperature():

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    response = requests.get(weather_url)
    weather_data = response.json()

    return jsonify({
        "temperature": weather_data["main"]["temp"],
        "city": weather_data["name"]
    })


# 💧 Water Calculation
@app.route('/calculate_water', methods=['POST'])
def calculate_water():

    data = request.get_json()

    crop = data.get("crop","").lower()
    soil = data.get("soil","")
    moisture = data.get("moisture","").lower()
    acres = float(data.get("acres",0))
    lat = data.get("lat")
    lon = data.get("lon")

    if crop not in CROP_WATER_REQUIREMENTS:
        return jsonify({"error":"Invalid crop"})

    base_water = CROP_WATER_REQUIREMENTS[crop]

    moisture_factor = MOISTURE_FACTORS.get(moisture,1)

    soil_factor = SOIL_FACTORS.get(soil,1)


    # 🌡 Get temperature
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    response = requests.get(weather_url)
    weather_data = response.json()

    temp = weather_data["main"]["temp"]
    weather = weather_data["weather"][0]["main"]


    # 💧 Base water calculation
    total_water = base_water * moisture_factor * soil_factor * acres


    # 🌡 Temperature adjustment
    if temp > 35:
        total_water *= 1.15
    elif temp > 30:
        total_water *= 1.05


    # ☔ Rain reduction
    if weather.lower() == "rain":
        total_water *= 0.4


    final_water = round(total_water,2)


    # 🚰 Motor logic
    if final_water > 0:
        motor_status = "ON"
    else:
        motor_status = "OFF"


    return jsonify({

        "water": final_water,
        "temperature": temp,
        "weather": weather,
        "motor": motor_status

    })


if __name__ == "__main__":
    app.run(debug=True)