from flask import Flask, request, render_template
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
from datetime import datetime

app = Flask(__name__)


with open("model.pkl", "rb") as f:
    data = pickle.load(f)

model = data['model']
model_features = data['features']  
target = data['target']

mean_temp, std_temp = 25.0, 5.0
mean_qv, std_qv = 0.004, 0.001
mean_w2m, std_w2m = 2.5, 1.0
mean_tql, std_tql = 0.1, 0.05

@app.route("/", methods=["GET","POST"])
def index():
    prediction = None
    graph_urls = []

    if request.method == "POST":
        input_values = []

        for feat in model_features:
            if feat in ["t2m_toc","qv2m_toc","w2m_toc","tql_toc",
                        "t2m_dav","qv2m_dav","tql_dav","w2m_dav"]:
                val = float(request.form.get(feat, 0))
                input_values.append(val)

            elif feat == "t2m_san":
                t2m_toc = float(request.form.get("t2m_toc", 25.0))
                input_values.append((t2m_toc - mean_temp)/std_temp)
            elif feat == "qv2m_san":
                qv2m_toc = float(request.form.get("qv2m_toc", 0.004))
                input_values.append((qv2m_toc - mean_qv)/std_qv)
            elif feat == "w2m_san":
                w2m_toc = float(request.form.get("w2m_toc", 2.5))
                input_values.append((w2m_toc - mean_w2m)/std_w2m)
            elif feat == "tql_san":
                tql_toc = float(request.form.get("tql_toc", 0.1))
                input_values.append((tql_toc - mean_tql)/std_tql)

            elif feat in ["year","month","day","dayofweek"]:
                date_val = request.form.get("date")
                if date_val:
                    dt = datetime.strptime(date_val, "%Y-%m-%d")
                    if feat=="year": input_values.append(dt.year)
                    elif feat=="month": input_values.append(dt.month)
                    elif feat=="day": input_values.append(dt.day)
                    elif feat=="dayofweek": input_values.append(dt.isoweekday())
                else:
                    input_values.append(0)

            else:
                val = float(request.form.get(feat, 0))
                input_values.append(val)


        model_input = pd.DataFrame([input_values], columns=model_features)


        prediction = round(model.predict(model_input)[0], 2)


        hours = list(range(24))
        hourly_inputs = []

        for h in hours:
            row = input_values.copy()
            hour_index = model_features.index("hour")
            row[hour_index] = h
            hourly_inputs.append(row)

        hourly_df = pd.DataFrame(hourly_inputs, columns=model_features)
        hourly_pred = model.predict(hourly_df)

        plt.figure(figsize=(8,4))
        plt.plot(hours, hourly_pred, marker='o', color='blue')
        plt.title("Hourly Electricity Demand Prediction")
        plt.xlabel("Hour")
        plt.ylabel("Predicted Demand (MW)")
        plt.grid(True)

        filename = f"static/graphs/hourly_{uuid.uuid4().hex}.png"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename)
        plt.close()
        graph_urls.append("/" + filename)

    return render_template("index.html", prediction=prediction, graph_urls=graph_urls)


if __name__ == "__main__":
    app.run(debug=True)
