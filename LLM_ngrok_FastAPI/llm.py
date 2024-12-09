from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)

# Define WQI classifications
def classify_wqi(wqi):
    if wqi < 50:
        return "Excellent"
    elif 50 <= wqi <= 100:
        return "Good"
    elif 100 < wqi <= 200:
        return "Poor"
    elif 200 < wqi <= 300:
        return "Very Poor"
    else:
        return "Unsuitable for Drinking"

# Load model and tokenizer
model_name = "openai-community/gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    offload_folder="offload"
)

@app.route('/lake_summary', methods=['GET'])
def lake_summary():

    # Retrieve parameters from the query string
    try:
        lake = request.args.get('lake')
        dissolved_oxygen = round(float(request.args.get('dissolved_oxygen')), 2)
        year = int(request.args.get('year'))  # Year doesn't need rounding
        ph = round(float(request.args.get('ph')), 2)
        conductivity = round(float(request.args.get('conductivity')), 2)
        bod = round(float(request.args.get('bod')), 2)  # Biological Oxygen Demand
        nitrate_nitrite = round(float(request.args.get('nitrate_nitrite')), 2)
        fecal_coliform = int(request.args.get('fecal_coliform'))  # Counts don't need rounding
        total_coliform = int(request.args.get('total_coliform'))  # Counts don't need rounding
        wqi = round(float(request.args.get('wqi')), 2)
    except (TypeError, ValueError):
        return jsonify({"error": "All parameters are required and must be in the correct format"}), 400

    # Classify WQI
    wqi_classification = classify_wqi(wqi)
 
    summary = (
        f"The lake '{lake}' was assessed in the year {year}. The key parameters measured "
        f"include a dissolved oxygen level of {dissolved_oxygen} mg/L, pH of {ph}, conductivity of {conductivity} µS/cm, "
        f"biological oxygen demand (BOD) of {bod} mg/L, and nitrate plus nitrite levels of {nitrate_nitrite} mg/L. Additionally, "
        f"fecal coliform counts were reported at {fecal_coliform} CFU/100mL, while total coliform counts were {total_coliform} CFU/100mL. "
        f"Based on these parameters, the Water Quality Index (WQI) was calculated to be {wqi}, which falls under the '{wqi_classification}' category. "
        f"Overall, the water quality of this lake is considered '{wqi_classification}'."
    )  

    # Construct the prompt
    prompt = f"""
    Write a description of the current air quality in {lake}, highlighting pollutants, health risks, and recommendations for vulnerable groups. 
    
    Response:

    {summary}
    """

    # Generate text
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"], max_length=1000)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    index = result.index('Response:')

    return jsonify({"generated_text": result[index+10:].strip()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)