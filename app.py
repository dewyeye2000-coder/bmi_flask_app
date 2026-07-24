import os

from dotenv import load_dotenv
from flask import Flask, render_template, request
from supabase import create_client

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def calculate_bmi(height_cm, weight_kg):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "과체중"
    else:
        return "비만"


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        try:
            height = float(request.form["height"])
            weight = float(request.form["weight"])

            if height <= 0 or weight <= 0:
                error = "키와 몸무게는 0보다 큰 값을 입력해주세요."
            else:
                bmi = calculate_bmi(height, weight)
                category = get_bmi_category(bmi)
                result = {"bmi": bmi, "category": category}

                if supabase:
                    supabase.table("bmi_records").insert({
                        "height_cm": height,
                        "weight_kg": weight,
                        "bmi": bmi,
                        "category": category,
                    }).execute()
        except (ValueError, KeyError):
            error = "올바른 숫자를 입력해주세요."

    history = []
    if supabase:
        response = (
            supabase.table("bmi_records")
            .select("*")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        history = response.data

    return render_template("index.html", result=result, error=error, history=history)


if __name__ == "__main__":
    app.run(debug=True)
