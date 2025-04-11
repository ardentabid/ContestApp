from flask import Flask, render_template, request, jsonify, send_file
from openpyxl import Workbook
import io
import datetime

app = Flask(__name__)

questions = {
    "Q1": {"text": "What is 2 + 2?", "options": ["3", "4", "5"], "answer": "4"},
    "Q2": {"text": "Capital of France?", "options": ["Paris", "London", "Rome"], "answer": "Paris"},
    "Q3": {"text": "Color of sky?", "options": ["Blue", "Green", "Red"], "answer": "Blue"},
    "Q4": {"text": "Fastest land animal?", "options": ["Cheetah", "Tiger", "Lion"], "answer": "Cheetah"},
    "Q5": {"text": "Water freezes at?", "options": ["0°C", "100°C", "50°C"], "answer": "0°C"},
    "Q6": {"text": "Python is?", "options": ["Programming Language", "Snake", "Car"], "answer": "Programming Language"},
    "Q7": {"text": "Which is a fruit?", "options": ["Carrot", "Apple", "Potato"], "answer": "Apple"},
    "Q8": {"text": "Largest planet?", "options": ["Earth", "Mars", "Jupiter"], "answer": "Jupiter"},
    "Q9": {"text": "What is H2O?", "options": ["Water", "Oxygen", "Hydrogen"], "answer": "Water"},
    "Q10": {"text": "Which is a prime number?", "options": ["4", "9", "7"], "answer": "7"},
}

vote_log = []  # list of dicts, one per user

@app.route('/')
def index():
    return render_template('index.html', questions=questions)

@app.route('/vote', methods=['POST'])
def vote():
    name = request.form.get('name')
    if not name:
        return 'Name is required', 400

    user_votes = {"name": name, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for q_id in questions:
        answer = request.form.get(q_id)
        correct = "Yes" if answer == questions[q_id]["answer"] else "No"
        user_votes[q_id] = {"selected": answer, "correct": correct}

    vote_log.append(user_votes)
    return '', 204

@app.route('/results')
def results():
    # Count per question per option
    summary = {q: {opt: 0 for opt in questions[q]["options"]} for q in questions}
    for entry in vote_log:
        for q_id in questions:
            selected = entry.get(q_id, {}).get("selected")
            if selected:
                summary[q_id][selected] += 1
    return jsonify(summary)

@app.route('/download')
def download():
    wb = Workbook()
    ws = wb.active
    ws.title = "Votes"

    # Header
    headers = ["Name", "Timestamp"]
    for q_id, q_data in questions.items():
        headers.append(f"{q_data['text']} (Answer)")
        headers.append(f"{q_data['text']} (Correct?)")
    ws.append(headers)

    for entry in vote_log:
        row = [entry["name"], entry["timestamp"]]
        for q_id in questions:
            vote_info = entry.get(q_id, {})
            row.append(vote_info.get("selected", ""))
            row.append(vote_info.get("correct", ""))
        ws.append(row)

    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    return send_file(
        file_stream,
        as_attachment=True,
        download_name="votes.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == '__main__':
    app.run(debug=True)
