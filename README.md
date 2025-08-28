**🧘✨ Yoga Agent **

Yoga Agent is a Streamlit-based AI chatbot that helps users explore yoga poses, sequences, and anatomy.
It uses a LangChain agent with tools, function calling, long-term memory, and token tracking


**🌟 Features:**
💬 Conversational Chatbot – Ask questions about yoga poses or request full sequences.

🛠 Agent with Tools – The agent dynamically chooses between:

📌 Pose Info Tool – Returns benefits, contraindications, description, and a link to Yoga Journal.

📅 Sequence Generator Tool – Generates tailored yoga sequences, including single-day sequences.

📆 Multi-Day Routine Tool – Generates 2–7 day routines with different sequences each day.

🔎 Enrichment Buttons – Fetch detailed descriptions, benefits, contraindications, and links for any pose.

🧠 Memory – Keeps track of conversation context.

🔢 Token Usage Tracking – Displays tokens consumed per conversation using tiktoken.

☁️ Deployable on Render – Share your chatbot with the world!


**🗂 Architecture & Flowchart:**

```
                          ┌─────────────────────────────┐
                          │           Agent             │
                          │     (LangChain + Memory)    │
                          └─────────────┬───────────────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
┌─────────▼─────────┐         ┌─────────▼─────────┐         ┌─────────▼─────────┐
│   Pose Info Tool   │         │  Sequence Tool    │         │ Multi-Day Routine │
│     📌 Returns     │         │    📅 Generates   │         │       📆 Generates │
│ description,       │         │ single-day        │         │ multiple sequences │
│ benefits,          │         │ sequences         │         │ for 2–7 days       │
│ contraindications, │         │ tailored by       │         │ different each day │
│ Yoga Journal link  │         │ energy, duration, │         │                     │
│                    │         │ injuries          │         │                     │
└─────────┬─────────┘         └─────────┬─────────┘         └─────────┬─────────┘
          │                             │                             │
          │                             │                             │
          └─────────────┬───────────────┴─────────────┬───────────────┘
                        ▼                                  
                ┌────────────────┐
                │ Enrichment     │
                │ Button/Function│
                │ Fetches detailed│
                │ description,   │
                │ benefits,       │
                │ contraindications│
                │ Yoga Journal link│
                └─────────┬───────┘
                          │
                          ▼
                    ┌────────────┐
                    │ Streamlit  │
                    │    UI 🖥   │
                    │ Displays:  │
                    │ - Chat     │
                    │ - Sequences│
                    │ - Images   │
                    │ - Links    │
                    │ - Tokens   │
                    └────────────┘




```


**Quickstart – Local:**

1️⃣ Clone the repo:
   git clone https://github.com/TuringCollegeSubmissions/anaisp-AE.3.5.git
   cd anaisp-AE.3.5

2️⃣ Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

3️⃣ Install dependencies:
   pip install -r requirements.txt

4️⃣ Set your API key:
   export OPENAI_API_KEY=sk-xxxx  # Windows: setx OPENAI_API_KEY "sk-xxxx"

5️⃣ Run the app:
   streamlit run app.py



☁️ **Cloud Deployment (Render):**

1️⃣ Push code to GitHub.

2️⃣ Go to <a href="https://render.com">Render</a> → New Web Service

3️⃣ Connect your repo.

4️⃣ Configure:
   - Build Command: pip install -r requirements.txt
   - Start Command: streamlit run app.py --server.port 10000 --server.address 0.0.0.0
     
5️⃣ Add environment variable: OPENAI_API_KEY=sk-xxxx

6️⃣ Deploy and get your public URL.


🔢 **Token Usage:**

- Tokens are calculated in each conversation using tiktoken.
- Token count is displayed in the Streamlit UI for each response.


📷 **Screenshots:**

<img width="1351" height="702" alt="Screenshot 2025-08-28 at 16 13 18" src="https://github.com/user-attachments/assets/ad862fde-d8dc-4af7-923e-17abd0486604" />


📝 **Requirements:**

- Python 3.9+
- Streamlit
- LangChain
- OpenAI
- Tiktoken

(See requirements.txt for full list)



