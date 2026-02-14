import uuid
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Temporary storage (use database in production)
applications = {}

# -------------------------
# Scheme Prediction Logic
# -------------------------
def predict_scheme(data):
    income = int(data["income"])
    occupation = data["occupation"]
    category = data["category"]
    gender = data["gender"]

    if occupation == "Student" and income < 300000:
        return {
            "name": "Rural Student Scholarship",
            "link": "https://scholarships.gov.in/"
        }

    elif occupation == "Farmer" and income < 500000:
        return {
            "name": "PM Kisan Samman Nidhi",
            "link": "https://pmkisan.gov.in/"
        }

    elif category in ["SC", "ST"] and income < 400000:
        return {
            "name": "Social Welfare Support Scheme",
            "link": "https://socialjustice.gov.in/"
        }

    elif gender == "Female" and income < 300000:
        return {
            "name": "Women Empowerment Scheme",
            "link": "https://wcd.nic.in/"
        }

    else:
        return {
            "name": "No Specific Scheme Found",
            "link": "#"
        }

# -------------------------
# Home Route
# -------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_data = request.form.to_dict()
        scheme = predict_scheme(user_data)
        return render_template("result.html", scheme=scheme)

    return render_template("index.html")


# -------------------------
# Apply Page
# -------------------------
@app.route("/apply/<scheme_name>")
def apply_form(scheme_name):
    return render_template("apply.html", scheme=scheme_name)


# -------------------------
# Submit Application
# -------------------------
@app.route("/submit_application", methods=["POST"])
def submit_application():
    data = request.form.to_dict()

    # Generate Application ID
    app_id = str(uuid.uuid4())[:8]
    data["application_id"] = app_id

    applications[app_id] = data

    # Send to n8n webhook
    try:
        response = requests.post("https://diwakar142008.app.n8n.cloud/webhook-test/31ebd9d6-14d4-4525-a1c1-472704eaa88b", json=data)
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
    except Exception as e:
        print("Error sending data to n8n:", e)
        print("Failed to send data to n8n")
        

    return render_template("success.html", app_id=app_id, scheme=data["scheme"])


# -------------------------
# Check Status
# -------------------------
@app.route("/status/<app_id>")
def check_status(app_id):
    if app_id in applications:
        return f"Application {app_id} is Submitted Successfully"
    else:
        return "Application Not Found"


if __name__ == "__main__":
    app.run(debug=True)