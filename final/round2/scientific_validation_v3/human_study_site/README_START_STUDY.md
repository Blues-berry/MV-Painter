# Start the blinded image study

## Participant instructions

1. The coordinator gives you a participant ID and a copy of
   `participant_handoff.zip`.
2. Extract the zip. It creates a folder named `human_study_site` containing
   the page and its local images. Keep the files together.
3. Open a terminal in that folder and run:

   ```sh
   python3 -m http.server 8000 --bind 127.0.0.1
   ```

4. Open this address in your browser: **http://127.0.0.1:8000/**
5. Enter your assigned participant ID, confirm the consent statement, and
   complete 24 comparisons. Each object appears once. A/B placement and
   question order are randomized.
6. Download the CSV at the end and return it to the coordinator with your
   participant ID. Do not send your name, email, phone number, or account
   information.
7. Close the server with Ctrl+C after downloading your CSV.

The server listens only on this computer. The page does not upload answers or
send them to a remote service. Keep the tab open until the CSV has downloaded.
Progress is saved in this browser when browser storage is available.

## Coordinator instructions

Run `assignment_generator.py` once before inviting anyone. It freezes 40
balanced assignments, copies the blinded images into `assets/`, creates the
participant handoff zip, and stores method/task keys under
`coordinator_private/`. Give participants only the zip and one assigned ID.
Never distribute `coordinator_private/` or the entire repository.

Put one downloaded response CSV per participant in
`coordinator_private/responses/`. Do not inspect preferences while collection
is active. After the collection window ends or 40 complete responses have
arrived, run:

```sh
python3 analyze_human_study.py
```

Incomplete participants are excluded as a whole. The analysis reports every
comparison and question separately, including ties and results favoring the
comparator. Do not create or substitute synthetic responses.
