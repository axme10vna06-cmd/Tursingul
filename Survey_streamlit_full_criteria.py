import csv
import io
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple

import streamlit as st


# Embedded fallback questions are intentionally kept to demonstrate
# that questions can be embedded in code as well as loaded externally.
EMBEDDED_QUESTIONS: List[Dict[str, Any]] = [
    {
        "question": "How often do you measure your success by your own improvement rather than by other people's results?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "When setting goals, how much do you focus on your personal starting point and progress?",
        "options": [
            ("Completely focus on my own progress", 1),
            ("Mostly focus on my own progress", 2),
            ("Focus on both equally", 3),
            ("Mostly compare with others", 4),
            ("Fully compare with others", 5),
        ],
    },
    {
        "question": "How often do you feel satisfied when you improve, even if others perform better?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How often do you keep track of your own growth instead of checking where others stand?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How much does personal progress motivate you even without outside recognition?",
        "options": [
            ("Very strongly", 1),
            ("Strongly", 2),
            ("Moderately", 3),
            ("Slightly", 4),
            ("Not at all", 5),
        ],
    },
    {
        "question": "How often do other people's achievements make you question your own worth?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "When someone around you succeeds, how often can you stay focused on your own path?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How often do you compare your academic or work results with those of your peers?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How often do you feel discouraged after seeing someone else progress faster than you?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How easy is it for you to appreciate others' success without feeling behind?",
        "options": [
            ("Very easy", 1),
            ("Easy", 2),
            ("Neutral", 3),
            ("Difficult", 4),
            ("Very difficult", 5),
        ],
    },
    {
        "question": "How often do social media posts make you feel that you are not doing enough?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How often do you compare your lifestyle or achievements with people you see online?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How well do you manage to remind yourself that what you see online of successful people doesn't show the whole picture?",
        "options": [
            ("Very well", 1),
            ("Well", 2),
            ("Fairly well", 3),
            ("Poorly", 4),
            ("Very poorly", 5),
        ],
    },
    {
        "question": "How often do other people's expectations make you forget your own speed of progress?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How much does it improve your motivation if you avoid comparisons?",
        "options": [
            ("Improves it very strongly", 1),
            ("Improves it strongly", 2),
            ("Improves it somewhat", 3),
            ("Improves it a little", 4),
            ("Does not help", 5),
        ],
    },
    {
        "question": "How often do you celebrate small victories of yours?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How often do you manage to remind yourself that progress may look different for different people?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
    {
        "question": "How often do you lose motivation due to the feeling that other people are ahead of you?",
        "options": [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5),
        ],
    },
    {
        "question": "How confident are you in pursuing your goals without needing to outperform others?",
        "options": [
            ("Very confident", 1),
            ("Confident", 2),
            ("Neutral", 3),
            ("Not very confident", 4),
            ("Not confident at all", 5),
        ],
    },
    {
        "question": "How often do you define what success means to you?",
        "options": [
            ("Always", 1),
            ("Often", 2),
            ("Sometimes", 3),
            ("Rarely", 4),
            ("Never", 5),
        ],
    },
]


@dataclass
class Question:
    prompt: str
    options: List[Tuple[str, int]]


class SurveyApp:
    ALLOWED_SAVE_FORMATS: Tuple[str, ...] = ("txt", "csv", "json")
    ALLOWED_NAME_EXTRA_CHARS: frozenset = frozenset({"-", "'", " "})
    THRESHOLD_BANDS: range = range(20, 101)

    def __init__(self, question_file: str = "questions.json"):
        self.question_file: str = question_file
        self.questions: List[Question] = self.load_questions()
        self.result_states: List[Tuple[range, str]] = [
            (range(20, 36), "Excellent personal focus - strong self-growth mindset, very little unhealthy comparison"),
            (range(36, 51), "Healthy progress orientation - mostly focused on personal goals with only occasional comparison"),
            (range(51, 66), "Mild comparison tendency - comparison with others occurs but still able to focus on self-progress"),
            (range(66, 81), "Moderate comparison strain - comparison begins to impact motivation, confidence, satisfaction"),
            (range(81, 91), "High comparison pressure - frequent comparison with others occurs with reduced self-focus and increasing strain"),
            (range(91, 101), "Critical comparison pattern - strong dependency on others' achievements with significant impact on self-esteem and motivation"),
        ]

    def load_questions(self) -> List[Question]:
        raw_questions: List[Dict[str, Any]] = []
        if os.path.exists(self.question_file):
            try:
                with open(self.question_file, "r", encoding="utf-8") as file:
                    raw_questions = json.load(file)
            except (json.JSONDecodeError, OSError):
                raw_questions = EMBEDDED_QUESTIONS
        else:
            raw_questions = EMBEDDED_QUESTIONS

        questions: List[Question] = []
        for item in raw_questions:
            option_pairs: List[Tuple[str, int]] = [(str(text), int(score)) for text, score in item["options"]]
            questions.append(Question(str(item["question"]), option_pairs))
        return questions

    def validate_name(self, name: str) -> bool:
        cleaned: str = name.strip()
        if len(cleaned) < 3:
            return False

        has_letter: bool = False
        invalid_chars: set = set()

        for char in cleaned:
            if char.isalpha():
                has_letter = True
            elif char not in self.ALLOWED_NAME_EXTRA_CHARS:
                invalid_chars.add(char)

        if invalid_chars:
            return False
        return has_letter

    def validate_dob(self, dob_text: str) -> bool:
        try:
            parsed_date: datetime = datetime.strptime(dob_text, "%Y-%m-%d")
            return parsed_date <= datetime.now()
        except ValueError:
            return False

    def validate_student_id(self, student_id: str) -> bool:
        return student_id.strip().isdigit()

    def calculate_result(self, total_score: int) -> str:
        for score_range, state in self.result_states:
            if total_score in score_range:
                return state
        return "Invalid total score"

    def build_result_data(self, full_name: str, date_of_birth: str, student_id: str, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_score: int = sum(answer["score"] for answer in answers)
        return {
            "full_name": full_name,
            "date_of_birth": date_of_birth,
            "student_id": student_id,
            "total_score": total_score,
            "psychological_state": self.calculate_result(total_score),
            "answers": answers,
        }

    def result_as_json(self, result_data: Dict[str, Any]) -> str:
        return json.dumps(result_data, indent=4, ensure_ascii=False)

    def result_as_csv(self, result_data: Dict[str, Any]) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["full_name", result_data["full_name"]])
        writer.writerow(["date_of_birth", result_data["date_of_birth"]])
        writer.writerow(["student_id", result_data["student_id"]])
        writer.writerow(["total_score", result_data["total_score"]])
        writer.writerow(["psychological_state", result_data["psychological_state"]])
        writer.writerow([])
        writer.writerow(["question_number", "question", "selected_answer", "score"])
        for index, answer in enumerate(result_data["answers"], start=1):
            writer.writerow([index, answer["question"], answer["selected_answer"], answer["score"]])
        return buffer.getvalue()

    def result_as_txt(self, result_data: Dict[str, Any]) -> str:
        average_score: float = result_data["total_score"] / len(result_data["answers"])
        lines: List[str] = [
            "QUESTIONNAIRE RESULT",
            "=" * 50,
            f"Name: {result_data['full_name']}",
            f"Date of Birth: {result_data['date_of_birth']}",
            f"Student ID: {result_data['student_id']}",
            f"Total Score: {result_data['total_score']}",
            f"Average Score per Question: {average_score:.2f}",
            f"Psychological State: {result_data['psychological_state']}",
            "",
            "Answers:",
        ]
        for index, answer in enumerate(result_data["answers"], start=1):
            lines.append(f"{index}. {answer['question']}")
            lines.append(f"   Answer: {answer['selected_answer']}")
            lines.append(f"   Score: {answer['score']}")
        return "\n".join(lines)

    def parse_json(self, file_bytes: bytes) -> Dict[str, Any]:
        return json.loads(file_bytes.decode("utf-8"))

    def parse_csv(self, file_bytes: bytes) -> Dict[str, Any]:
        text = file_bytes.decode("utf-8")
        rows: List[List[str]] = list(csv.reader(io.StringIO(text)))
        metadata: Dict[str, str] = {}
        answers: List[Dict[str, Any]] = []
        answers_section_started: bool = False

        for row in rows:
            if not row:
                continue
            if row[0] == "question_number":
                answers_section_started = True
                continue
            if not answers_section_started and len(row) >= 2:
                metadata[row[0]] = row[1]
            elif answers_section_started and len(row) >= 4:
                answers.append({
                    "question": row[1],
                    "selected_answer": row[2],
                    "score": int(row[3]),
                })

        return {
            "full_name": metadata.get("full_name", "Unknown"),
            "date_of_birth": metadata.get("date_of_birth", "Unknown"),
            "student_id": metadata.get("student_id", "Unknown"),
            "total_score": int(metadata.get("total_score", 0)),
            "psychological_state": metadata.get("psychological_state", "Unknown"),
            "answers": answers,
        }

    def parse_txt(self, file_bytes: bytes) -> Dict[str, Any]:
        content = file_bytes.decode("utf-8")
        lines: List[str] = content.splitlines()
        data: Dict[str, Any] = {
            "full_name": "Unknown",
            "date_of_birth": "Unknown",
            "student_id": "Unknown",
            "total_score": 0,
            "psychological_state": "Unknown",
            "answers": [],
            "raw_text": content,
        }

        current_question: str = ""
        for line in lines:
            if line.startswith("Name: "):
                data["full_name"] = line.replace("Name: ", "", 1)
            elif line.startswith("Date of Birth: "):
                data["date_of_birth"] = line.replace("Date of Birth: ", "", 1)
            elif line.startswith("Student ID: "):
                data["student_id"] = line.replace("Student ID: ", "", 1)
            elif line.startswith("Total Score: "):
                try:
                    data["total_score"] = int(line.replace("Total Score: ", "", 1))
                except ValueError:
                    data["total_score"] = 0
            elif line.startswith("Psychological State: "):
                data["psychological_state"] = line.replace("Psychological State: ", "", 1)
            elif line[:2].strip().endswith(".") and len(line) > 3:
                current_question = line.split(". ", 1)[1] if ". " in line else line
            elif line.strip().startswith("Answer: ") and current_question:
                selected_answer = line.strip().replace("Answer: ", "", 1)
                data["answers"].append({
                    "question": current_question,
                    "selected_answer": selected_answer,
                    "score": 0,
                })
        return data

    def variable_type_demo(self) -> Dict[str, str]:
        demo_int: int = len(self.questions)
        demo_str: str = "Survey type demo"
        demo_float: float = 4.0
        demo_list: List[str] = [question.prompt for question in self.questions[:2]]
        demo_tuple: Tuple[str, ...] = self.ALLOWED_SAVE_FORMATS
        demo_range: range = self.THRESHOLD_BANDS
        demo_bool: bool = demo_int >= 15
        demo_dict: Dict[str, int] = {"minimum_questions_required": 15, "actual_questions": len(self.questions)}
        demo_set: set = {"txt", "csv", "json"}
        demo_frozenset: frozenset = self.ALLOWED_NAME_EXTRA_CHARS

        return {
            "int": str(demo_int),
            "str": demo_str,
            "float": str(demo_float),
            "list": str(demo_list),
            "tuple": str(demo_tuple),
            "range": f"{demo_range.start}-{demo_range.stop - 1}",
            "bool": str(demo_bool),
            "dict": str(demo_dict),
            "set": str(demo_set),
            "frozenset": str(demo_frozenset),
        }


app = SurveyApp()

st.set_page_config(page_title="Psychological state survey", layout="wide")
st.title("Peer comparison avoidance and personal progress focus")


with st.sidebar:
    st.header("App Mode")
    mode: str = st.radio(
        "Choose an option",
        ("Start a new questionnaire", "Load an existing result"),
    )
    st.markdown("---")
    st.subheader("Criteria Evidence")
    st.write(f"Questions loaded: {len(app.questions)}")
    st.write("Question source: external file with embedded fallback")
    st.write("Save and load formats: TXT, CSV, JSON")

with st.expander("Show variable-type demonstration used in the program"):
    st.json(app.variable_type_demo())


def render_result(result_data: Dict[str, Any]) -> None:
    average_score: float = result_data["total_score"] / max(len(result_data.get("answers", [])), 1)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Score", result_data["total_score"])
    col2.metric("Average Score", f"{average_score:.2f}")
    col3.metric("Questions Answered", len(result_data.get("answers", [])))

    st.success(f"Psychological State: {result_data['psychological_state']}")
    st.write(f"**Name:** {result_data['full_name']}")
    st.write(f"**Date of Birth:** {result_data['date_of_birth']}")
    st.write(f"**Student ID:** {result_data['student_id']}")

    if result_data.get("answers"):
        st.subheader("Answers")
        for index, answer in enumerate(result_data["answers"], start=1):
            with st.container(border=True):
                st.write(f"**{index}. {answer['question']}**")
                st.write(f"Answer: {answer['selected_answer']}")
                st.write(f"Score: {answer.get('score', 0)}")

    if "raw_text" in result_data:
        with st.expander("Raw TXT content"):
            st.text(result_data["raw_text"])


def add_download_buttons(result_data: Dict[str, Any]) -> None:
    st.subheader("Save / Download Results")
    base_name: str = "survey_results"
    json_text: str = app.result_as_json(result_data)
    csv_text: str = app.result_as_csv(result_data)
    txt_text: str = app.result_as_txt(result_data)

    c1, c2, c3 = st.columns(3)
    c1.download_button("Download TXT", data=txt_text, file_name=f"{base_name}.txt", mime="text/plain")
    c2.download_button("Download CSV", data=csv_text, file_name=f"{base_name}.csv", mime="text/csv")
    c3.download_button("Download JSON", data=json_text, file_name=f"{base_name}.json", mime="application/json")


if mode == "Start a new questionnaire":
    with st.form("survey_form"):
        st.subheader("Personal Information")
        full_name: str = st.text_input("Surname and given name")
        date_of_birth: str = st.text_input("Date of birth (YYYY-MM-DD)")
        student_id: str = st.text_input("Student ID number")

        st.subheader("Survey Questions")
        answers: List[Dict[str, Any]] = []
        selected_indices: List[int] = []

        for index, question in enumerate(app.questions, start=1):
            labels: List[str] = [f"{text} ({score})" for text, score in question.options]
            choice_index: int = st.radio(
                f"{index}. {question.prompt}",
                options=list(range(len(labels))),
                format_func=lambda idx, labels=labels: labels[idx],
                index=0,
                key=f"question_{index}",
            )
            selected_indices.append(choice_index)

        submitted: bool = st.form_submit_button("Submit questionnaire")

    if submitted:
        errors: List[str] = []
        if not app.validate_name(full_name):
            errors.append("Name must contain only letters, spaces, hyphens, and apostrophes.")
        if not app.validate_dob(date_of_birth):
            errors.append("Date of birth must be a valid past date in YYYY-MM-DD format.")
        if not app.validate_student_id(student_id):
            errors.append("Student ID must contain digits only.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # for loop used for survey processing
            for index, question in enumerate(app.questions):
                selected_text, selected_score = question.options[selected_indices[index]]
                answers.append(
                    {
                        "question": question.prompt,
                        "selected_answer": selected_text,
                        "score": selected_score,
                    }
                )

            result_data: Dict[str, Any] = app.build_result_data(full_name.strip(), date_of_birth.strip(), student_id.strip(), answers)
            st.session_state["latest_result"] = result_data
            render_result(result_data)
            add_download_buttons(result_data)

    elif "latest_result" in st.session_state:
        st.subheader("Most Recent Result")
        render_result(st.session_state["latest_result"])
        add_download_buttons(st.session_state["latest_result"])

else:
    st.subheader("Load an Existing Result")
    uploaded_file = st.file_uploader("Upload a TXT, CSV, or JSON result file", type=["txt", "csv", "json"])

    if uploaded_file is not None:
        file_bytes: bytes = uploaded_file.read()
        file_name: str = uploaded_file.name.lower()

        try:
            if file_name.endswith(".json"):
                loaded_data = app.parse_json(file_bytes)
            elif file_name.endswith(".csv"):
                loaded_data = app.parse_csv(file_bytes)
            elif file_name.endswith(".txt"):
                loaded_data = app.parse_txt(file_bytes)
            else:
                loaded_data = None

            if loaded_data is None:
                st.error("Unsupported file format.")
            else:
                render_result(loaded_data)
                if "answers" in loaded_data and loaded_data["answers"]:
                    add_download_buttons(loaded_data)
        except Exception as error:
            st.error(f"Could not load the file: {error}")
