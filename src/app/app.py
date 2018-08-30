from flask import Flask, request, render_template
import pickle
import pandas as pd
import numpy as np
from flask.ext.mobility import Mobility
from flask.ext.mobility.decorators import mobile_template

app = Flask(__name__)
Mobility(app)

df = pd.read_csv('s3a://capstone-3/data/spark_model.csv')

def get_restricted_df(price,item_index,range):
    nums = range.split('-')
    min = int(nums[0])
    max = int(nums[1])
    restricted = df.copy()
    restricted = restricted[restricted['sale_price'] >= min]
    restricted = restricted[restricted['sale_price'] < max]
    if (price < min) or (price > max):
        restricted = restricted.append(products.iloc[item_index],ignore_index=True)
    return restricted

@app.route('/', methods =['GET','POST'])
def index():
    return render_template('home.html')

@app.route('/home', methods =['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/nlp', methods=['GET','POST'])
def nlp():
    return render_template('nlp.html')

@app.route('/neural_net', methods=['GET','POST'])
def neural_net():
    return render_template('neural_net.html')

@app.route('/nlp_recs', methods=['GET','POST'])
def nlp_recs():
    item_index= int(request.form['index'])
    range = str(request.form['price'])
    num_recs = int(request.form['recs'])
    item = products['product_title'].iloc[item_index]
    item_id = products['vendor_variant_id'].iloc[item_index]
    price = products['sale_price'].iloc[item_index]
    restricted = get_restricted_df(price,item_index,range)
    cluster_label = restricted['prediction'].iloc[item_index]
    cluster_members = restricted[restricted['prediction'] == cluster_label]
    recs = np.random.choice(cluster_members.index, 5, replace = False)
    for rec in recs:
        weblink = df.weblink.iloc[rec]
        print("Recommended: " + df['product_title'].iloc[rec] + "\nPrice: $" + str(df['sale_price'].iloc[rec]))

    return render_template('nlp_recs.html')

@app.route('/cnn_recs', methods=['GET','POST'])
def cnn_recs():
    item_index= int(request.form['index'])
    return render_template('cnn_recs.html')

if  __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
