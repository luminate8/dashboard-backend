
  1. Start the Backend Server
  Open your terminal (PowerShell or CMD) in the project folder and run:

   1 # 1. Activate the virtual environment
   2 .\venv\Scripts\activate
   3
   4 # 2. Run the server (it will auto-reload when you change code)
   5 python main.py

  2. Verify it is Running
  Once the server starts, you can check if it's healthy by visiting this link in your browser:
  👉 http://localhost:8000/health

  ---

  3. Summary of Demo Commands
  You have three main ways to show the project to your client:

  ┌─────────────────┬─────────────────────────────────┬───────────────────────────────────────────────────────────┐
  │ Feature         │ Command                         │ Purpose                                                   │
  ├─────────────────┼─────────────────────────────────┼───────────────────────────────────────────────────────────┤
  │ Celebrity Agent │ python test_dynamic_flow.py     │ Demo real-time Twitter scraping & Persona chat.           │
  │ Document Agent  │ python test_dynamic_doc_flow.py │ Demo uploading a PDF/Doc and chatting with its data.      │
  │ Full Auto Test  │ python test_full_flow.py        │ Runs a pre-set test with Elon Musk & Messi automatically. │