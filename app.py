from flask import Flask, request, render_template, redirect, url_for, session, flash
import numpy as np
import pandas as pd
import sklearn
import pickle
import sqlite3

# importing model
model = pickle.load(open('model.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))
ms = pickle.load(open('minmaxscaler.pkl', 'rb'))

# creating flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Crop to image path mapping
crop_images = {
    1: 'static/rice.jpg',
    2: 'static/maize.jpg',
    3: 'static/jute.jpg',
    4: 'static/cotton.jpg',
    5: 'static/coconut.jpg',
    6: 'static/papaya.jpg',
    7: 'static/orange.jpg',
    8: 'static/apple.jpg',
    9: 'static/muskmelon.jpg',
    10: 'static/watermelon.jpg',
    11: 'static/grapes.jpg',
    12: 'static/mango.jpg',
    13: 'static/banana.jpg',
    14: 'static/pomegranate.jpg',
    15: 'static/lentil.jpg',
    16: 'static/blackgram.jpg',
    17: 'static/mungbean.jpg',
    18: 'static/mothbean.jpg',
    19: 'static/pigeonpeas.jpg',
    20: 'static/kidneybeans.jpg',
    21: 'static/chickpea.jpg',
    22: 'static/coffee.jpg'
}
# Crop to harvesting tips mapping
# Crop to detailed harvesting tips mapping
harvest_tips = {
    1: "Ensure fields are well-irrigated throughout the growing season. Monitor the crop closely for signs of pests and diseases. Harvest when grains are fully mature, usually 30–35 days after flowering.",
    2: "Choose the right time for planting based on local climate and soil conditions. Ensure proper spacing to avoid overcrowding and competition for nutrients. Harvest maize when kernels are hard and the husks are dry, typically 18–22 days after silking.",
    3: "Jute prefers warm, humid conditions with adequate rainfall. Weeding is crucial during the early growth stages. Harvest when the lower leaves start to shed, usually around 120–150 days after sowing.",
    4: "Cotton requires a long frost-free period and plenty of sunlight. Regular monitoring for pests like bollworms is essential. Pick cotton when the bolls are fully open and the fibers are fluffy, ensuring the moisture content is low.",
    5: "Maintain proper spacing and provide adequate irrigation during dry periods. Fertilize regularly with potassium to improve yield and quality. Harvest coconuts when they are fully mature, usually 11–12 months after flowering, and have a brown husk.",
    6: "Papayas thrive in warm, sunny locations with well-drained soil. Protect young plants from wind and cold temperatures. Harvest papayas when they are yellow and slightly soft, and handle them carefully to avoid bruising.",
    7: "Ensure the soil is well-drained and slightly acidic. Regularly check for pests and diseases, particularly citrus canker and aphids. Harvest oranges when they are bright orange and firm, typically 6–12 months after flowering.",
    8: "Choose apple varieties suitable for your climate zone. Prune trees regularly to improve air circulation and sunlight penetration. Harvest apples when they are firm, have a uniform color, and detach easily from the tree.",
    9: "Muskmelons prefer warm, well-drained soils with full sun exposure. Regularly water but avoid waterlogging to prevent root rot. Harvest when the fruit slips off the vine easily and has a pleasant aroma.",
    10: "Ensure adequate space between plants for proper growth. Water consistently, especially during fruit development. Harvest watermelons when the underside turns yellow and the tendril nearest the fruit dries up.",
    11: "Grapes thrive in well-drained soil with plenty of sunlight. Prune vines annually to maintain shape and productivity. Harvest when grapes are full-colored, sweet, and the seeds are brown.",
    12: "Mangoes require a warm, frost-free climate with dry periods for fruit maturation. Regularly monitor for pests like fruit flies and mealybugs. Harvest when the fruit has a sweet aroma, and the flesh gives slightly when pressed.",
    13: "Bananas need a warm climate and well-drained soil with high organic content. Protect plants from strong winds, which can cause damage. Harvest bananas when the fruit is full and plump, and the angles of the fruit are less pronounced.",
    14: "Pomegranates prefer hot, dry climates with well-drained soil. Regular irrigation is crucial, especially during flowering and fruit set. Harvest when the fruit is bright red, glossy, and makes a metallic sound when tapped.",
    15: "Lentils grow well in cool, dry climates with well-drained soil. Ensure the crop receives adequate water during flowering and pod development. Harvest when the pods turn brown, and the seeds are hard, but avoid over-drying, which can cause seed shattering.",
    16: "Blackgram requires warm, humid conditions with well-drained soil. Regular weeding and pest control are essential for a good yield. Harvest when the pods are fully mature and dry, ensuring they do not split open.",
    17: "Mungbean prefers warm temperatures and well-drained, sandy soils. Ensure regular watering, especially during flowering and pod formation. Harvest when the pods are dry, and the seeds rattle inside; avoid harvesting during humid conditions to prevent mold.",
    18: "Mothbeans are drought-resistant and prefer sandy, loamy soil. They require minimal irrigation and are ideal for arid regions. Harvest when the pods are fully mature and dry, as over-mature pods may split and lose seeds.",
    19: "Pigeonpeas thrive in tropical and subtropical climates with well-drained soil. They require little water and are tolerant of drought conditions. Harvest when the pods are dry and the seeds are hard, typically 5–6 months after planting.",
    20: "Kidneybeans prefer temperate climates with well-drained, fertile soil. Ensure proper spacing and trellising to support climbing varieties. Harvest when the pods are dry and brittle, and the seeds inside are hard and dry.",
    21: "Chickpeas grow best in cool, dry climates with well-drained soil. Regular monitoring for pests like pod borers is crucial. Harvest when the pods turn brown, and the seeds are hard and dry, avoiding over-maturity to prevent seed loss.",
    22: "Coffee plants thrive in warm, tropical climates with well-drained, acidic soil. Provide shade and protect from strong winds. Harvest coffee cherries when they are bright red and firm, picking only the ripe ones for the best quality beans."
}


# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'username' in session:
        return render_template("index.html", username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
        conn.close()
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    N = request.form['Nitrogen']
    P = request.form['Phosporus']
    K = request.form['Potassium']
    temp = request.form['Temperature']
    humidity = request.form['Humidity']
    ph = request.form['Ph']
    rainfall = request.form['Rainfall']

    feature_list = [N, P, K, temp, humidity, ph, rainfall]
    single_pred = np.array(feature_list).reshape(1, -1)

    scaled_features = ms.transform(single_pred)
    final_features = sc.transform(scaled_features)
    prediction = model.predict(final_features)

    crop_dict = {
        1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
        8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
        14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
        19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
    }

    if prediction[0] in crop_dict:
        crop = crop_dict[prediction[0]]
        result = "{} is the best crop to be cultivated right there".format(crop)
        image_path = crop_images.get(prediction[0], 'static/default.jpg')
        harvest_tip = harvest_tips.get(prediction[0], "No specific harvesting tip available for this crop.")
    else:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."
        image_path = 'static/default.jpg'
        harvest_tip = ""

    return render_template('index.html', result=result, image_path=image_path, harvest_tip=harvest_tip, username=session['username'])

if __name__ == "__main__":
    app.run(debug=True)
