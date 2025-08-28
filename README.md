**🧘✨ Yoga GPT – Agent Chatbot**

Yoga GPT is a Streamlit-based chatbot that helps users explore yoga poses, sequences, and anatomy.  
It uses LangGraph/LangChain agents with function calling and displays pose images and yoga sequences.


**🌟 Features:**
- 💬 Conversational Chatbot – Ask questions about yoga poses or request full sequences.
- 🛠 Agent with Tools – The agent chooses between:
    - 📌 Pose Info Tool – returns benefits, contraindications, and image
    - 📅 Sequence Generator Tool – creates tailored yoga sequences, including multi-day routines
- 🧠 Memory – Keeps track of conversation context.
- 🔢 Token Usage Tracking – Displays tokens consumed per conversation.
- ☁️ Deployable on Render – Share your chatbot with the world!


**🗂 Architecture & Flowchart:**

```

                    ┌─────────────────────────┐
                    │         Agent           │
                    │  (LangChain + Memory)   │
                    └─────────┬──────────────┘
                              │
               ┌──────────────┴───────────────┐
               │                              │
        ┌──────▼──────┐                ┌──────▼──────┐
        │ Pose Info   │                │ Sequence    │
        │ Tool 📌     │                │ Generator 📅 │
        └──────┬──────┘                └──────┬──────┘
               │                              │
   ┌───────────▼───────────┐       ┌──────────▼───────────┐
   │ Fetch pose data        │       │ Generate sequence(s)  │
   │ Return description     │       │ Include duration,     │
   │ Return benefits        │       │ energy, injuries      │
   │ Return contraindications│      │ Add images for poses  │
   │ Return image           │       │ Multi-day routines    │
   └───────────┬───────────┘       └──────────┬───────────┘
               │                              │
               └───────────────┬──────────────┘
                               ▼
                          ┌─────────┐
                          │ Streamlit│
                          │ UI 🖥    │
                          │ Displays│
                          │ chat,   │
                          │ sequences,
                          │ images, │
                          │ token   │
                          │ usage   │
                          └─────────┘


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

<img width="1381" height="649" alt="Screenshot 2025-08-28 at 09 49 07" src="https://github.com/user-attachments/assets/246ae728-5501-4924-b537-cedb2d26a503" />


📝 **Requirements:**

- Python 3.9+
- Streamlit
- LangChain
- OpenAI
- Tiktoken

(See requirements.txt for full list)


