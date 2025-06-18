🚦 Traffic LLM Dashboard

An interactive, AI-assisted dashboard built with Streamlit to explore how various factors like weather, air quality, and public transport affect traffic congestion across major global cities.

📊 What It Does

Accepts natural language questions like:

"Which city is most affected by AQI?"

"Where does precipitation impact traffic the most?"

Calculates correlations between congestion index and selected environmental/transport features

Generates dynamic bar charts to visualize the results

Provides automated insights for each query

🏙️ Cities Included

London

New York

Barcelona

Buenos Aires

Paris

Melbourne

Bengaluru

Los Angeles

📁 Project Structure

traffic-llm-dashboard/
├── app.py                # Streamlit dashboard code
├── city_data.csv         # Merged and cleaned traffic dataset
├── requirements.txt      # Python dependencies

🚀 How to Run It

Streamlit Cloud

Fork or clone the repo

Go to https://streamlit.io/cloud

Log in and click "New app"

Select this repo and deploy

Local Machine

git clone https://github.com/YOUR_USERNAME/traffic-llm-dashboard.git
cd traffic-llm-dashboard
pip install -r requirements.txt
streamlit run app.py

📌 Features

Real-time visual analysis

Clean UI with interactive sidebar

Easily extendable with LLM APIs (e.g., Gemini, OpenAI)

🔧 Future Enhancements

Gemini/OpenAI chatbot integration

User-uploaded CSV support

Predictive modeling for future congestion levels

📄 License

MIT License

🙌 Acknowledgments

Developed by Maheep Mouli with data from multiple international city sources.

🌐 Live App

🔗 Coming soon after Streamlit Cloud deployment!

