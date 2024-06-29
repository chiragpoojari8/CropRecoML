from flask import Flask,request,render_template
import numpy as np
import pandas
import sklearn
import pickle


# importing model
model = pickle.load(open('model.pkl', 'rb'))
sc = pickle.load(open('standscaler.pkl', 'rb'))
ms = pickle.load(open('minmaxscaler.pkl', 'rb'))

# creating flask app
app = Flask(__name__)

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
    18: 'static/mothbeans.jpg',
    19: 'static/pigeonpeas.jpg',
    20: 'static/kidneybeans.jpg',
    21: 'static/chickpea.jpg',
    22: 'static/coffee.jpg'
}

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
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

    crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                 14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                 19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}

    if prediction[0] in crop_dict:
        crop = crop_dict[prediction[0]]
        result = "{} is the best crop to be cultivated right there".format(crop)
        image_path = crop_images.get(prediction[0], 'static/default.jpg')
    else:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."
        image_path = 'static/default.jpg'
    
    return render_template('index.html', result=result, image_path=image_path)

# python main
if __name__ == "__main__":
    app.run(debug=True)


