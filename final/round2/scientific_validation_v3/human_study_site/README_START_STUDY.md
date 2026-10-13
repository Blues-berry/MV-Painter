# Participant instructions

1. The coordinator gives you a participant ID and a copy of
   `participant_handoff.zip`.
2. Extract the zip. It creates a folder named `human_study_site` containing
   the page and its local images. Keep the files together.
3. Open a terminal in that folder and run:

   ```sh
   python3 -m http.server 8000 --bind 127.0.0.1
   ```

4. Open **http://127.0.0.1:8000/** in your browser.
5. Enter your assigned participant ID, confirm the consent statement, and
   complete 24 comparisons. Each object appears once. Image side, comparison
   order, and question order are randomized.
6. Answer the brief comprehension check shown after the comparisons. An
   incorrect answer means the response cannot be included in analysis.
7. Download the response CSV and return it to the coordinator with your
   assigned ID. Do not send your name, email, phone number, or account
   information.
8. Close the server with Ctrl+C after downloading your CSV.

The server listens only on this computer. The page does not upload answers or
send them to a remote service. Keep the tab open until the CSV has downloaded.
Progress is saved in this browser when browser storage is available.
