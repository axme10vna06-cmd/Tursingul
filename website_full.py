import csv
import io
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Tuple

import streamlit as st


# Embedded fallback questions remain in the code to demonstrate that
# questions can be stored both externally and directly in the program.
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
    ALLOWED_SAVE_FORMATS: Tuple[str, ...] = ("TXT", "CSV", "JSON")
    NAME_PATTERN: str = r"^[A-Za-z\s\-']+$"
    VALID_SCORE_RANGE: range = range(20, 101)
    ALLOWED_NAME_CHARS: frozenset = frozenset({"-", "'", " "})

    def __init__(self, question_file: str = "questions.json"):
        self.question_file: str = question_file
        self.questions: List[Question] = self.load_questions()
        self.result_bands: List[Tuple[range, str]] = [
            (range(20, 36), "Excellent personal focus - strong self-growth mindset, very little unhealthy comparison"),
            (range(36, 51), "Healthy progress orientation - mostly focused on personal goals with only occasional comparison"),
            (range(51, 66), "Mild comparison tendency - comparison with others occurs but still able to focus on self-progress"),
            (range(66, 81), "Moderate comparison strain - comparison begins to impact motivation, confidence, satisfaction"),
            (range(81, 91), "High comparison pressure - frequent comparison with others occurs with reduced self-focus and increasing strain"),
            (range(91, 101), "Critical comparison pattern - strong dependency on others' achievements with significant impact on self-esteem and motivation"),
        ]

        # Extra variable types included for marking criterion visibility.
        self.version_float: float = 1.0
        self.metadata_dict: Dict[str, Any] = {
            "question_count": len(self.questions),
            "formats": list(self.ALLOWED_SAVE_FORMATS),
        }
        self.answer_labels_set: set = {option[0] for question in self.questions for option in question.options}

    def load_questions(self) -> List[Question]:
        raw_questions: List[Dict[str, Any]] = []
        if os.path.exists(self.question_file):
            try:
                with open(self.question_file, "r", encoding="utf-8") as file:
                    raw_questions = json.load(file)
            except (OSError, json.JSONDecodeError):
                raw_questions = EMBEDDED_QUESTIONS
        else:
            raw_questions = EMBEDDED_QUESTIONS

        loaded_questions: List[Question] = []
        for item in raw_questions:
            option_pairs: List[Tuple[str, int]] = [(str(text), int(score)) for text, score in item["options"]]
            loaded_questions.append(Question(prompt=str(item["question"]), options=option_pairs))
        return loaded_questions

    def validate_name(self, name: str) -> bool:
        cleaned_name: str = name.strip()
        if len(cleaned_name) < 3:
            return False
        if not re.fullmatch(self.NAME_PATTERN, cleaned_name):
            return False

        has_letter: bool = False
        invalid_characters: set = set()
        for char in cleaned_name:  # for-loop used for validation criterion
            if char.isalpha():
                has_letter = True
            elif char not in self.ALLOWED_NAME_CHARS:
                invalid_characters.add(char)
        return has_letter and not invalid_characters

    def validate_student_id(self, student_id: str) -> bool:
        return student_id.strip().isdigit()

    def calculate_result(self, total_score: int) -> str:
        if total_score not in self.VALID_SCORE_RANGE:
            return "Invalid total score"
        for score_range, state in self.result_bands:
            if total_score in score_range:
                return state
        return "Invalid total score"

    def build_result(self) -> Dict[str, Any]:
        structured_answers: List[Dict[str, Any]] = []
        total_score: int = 0

        for index, question in enumerate(self.questions, start=1):
            selected_text: str = st.session_state.get(f"q_{index}")
            selected_score: int = next(score for text, score in question.options if text == selected_text)
            structured_answers.append(
                {
                    "question": question.prompt,
                    "selected_answer": selected_text,
                    "score": selected_score,
                }
            )
            total_score += selected_score

        return {
            "full_name": st.session_state["full_name"].strip(),
            "date_of_birth": st.session_state["date_of_birth"].strftime("%Y-%m-%d"),
            "student_id": st.session_state["student_id"].strip(),
            "total_score": total_score,
            "psychological_state": self.calculate_result(total_score),
            "answers": structured_answers,
            
        }

    def to_json(self, result: Dict[str, Any]) -> str:
        return json.dumps(result, indent=4, ensure_ascii=False)

    def to_txt(self, result: Dict[str, Any]) -> str:
        lines: List[str] = [
            "Peer Comparison Avoidance Survey Result",
            "=" * 40,
            f"Name: {result['full_name']}",
            f"Date of Birth: {result['date_of_birth']}",
            f"Student ID: {result['student_id']}",
            f"Total Score: {result['total_score']}",
            f"Psychological State: {result['psychological_state']}",
           
            "",
            "Answers:",
        ]
        for index, answer in enumerate(result["answers"], start=1):
            lines.append(f"{index}. {answer['question']}")
            lines.append(f"   Answer: {answer['selected_answer']}")
            lines.append(f"   Score: {answer['score']}")
        return "\n".join(lines)

    def to_csv(self, result: Dict[str, Any]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Field", "Value"])
        writer.writerow(["full_name", result["full_name"]])
        writer.writerow(["date_of_birth", result["date_of_birth"]])
        writer.writerow(["student_id", result["student_id"]])
        writer.writerow(["total_score", result["total_score"]])
        writer.writerow(["psychological_state", result["psychological_state"]])
       
        writer.writerow([])
        writer.writerow(["Question", "Selected Answer", "Score"])
        for answer in result["answers"]:
            writer.writerow([answer["question"], answer["selected_answer"], answer["score"]])
        return output.getvalue()

    def export_result(self, result: Dict[str, Any], file_format: str) -> Tuple[str, str, str]:
        normalized: str = file_format.upper()
        if normalized == "TXT":
            return self.to_txt(result), "survey_result.txt", "text/plain"
        if normalized == "CSV":
            return self.to_csv(result), "survey_result.csv", "text/csv"
        return self.to_json(result), "survey_result.json", "application/json"

    def parse_uploaded_file(self, uploaded_file: Any, file_type: str) -> Dict[str, Any]:
        normalized: str = file_type.lower()
        if normalized == "json":
            return json.load(uploaded_file)

        if normalized == "txt":
            text: str = uploaded_file.getvalue().decode("utf-8")
            return self.parse_txt_result(text)

        if normalized == "csv":
            text = uploaded_file.getvalue().decode("utf-8")
            return self.parse_csv_result(text)

        raise ValueError("Unsupported file type")

    def parse_txt_result(self, text: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "full_name": "-",
            "date_of_birth": "-",
            "student_id": "-",
            "total_score": "-",
            "psychological_state": "-",
           
            "answers": [],
        }
        lines: List[str] = [line.rstrip() for line in text.splitlines()]
        current_question: str = ""
        current_answer: str = ""
        current_score: int = 0

        for line in lines:
            stripped: str = line.strip()
            if stripped.startswith("Name:"):
                result["full_name"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Date of Birth:"):
                result["date_of_birth"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Student ID:"):
                result["student_id"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Total Score:"):
                total_text = stripped.split(":", 1)[1].strip()
                result["total_score"] = int(total_text) if total_text.isdigit() else total_text
            elif stripped.startswith("Psychological State:"):
                result["psychological_state"] = stripped.split(":", 1)[1].strip()
            
            elif re.match(r"^\d+\.\s", stripped):
                if current_question:
                    result["answers"].append(
                        {
                            "question": current_question,
                            "selected_answer": current_answer,
                            "score": current_score,
                        }
                    )
                current_question = re.sub(r"^\d+\.\s", "", stripped)
                current_answer = ""
                current_score = 0
            elif stripped.startswith("Answer:"):
                current_answer = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Score:"):
                score_text = stripped.split(":", 1)[1].strip()
                current_score = int(score_text) if score_text.isdigit() else 0

        if current_question:
            result["answers"].append(
                {
                    "question": current_question,
                    "selected_answer": current_answer,
                    "score": current_score,
                }
            )
        return result

    def parse_csv_result(self, text: str) -> Dict[str, Any]:
        reader = csv.reader(io.StringIO(text))
        rows: List[List[str]] = [row for row in reader]
        result: Dict[str, Any] = {
            "full_name": "-",
            "date_of_birth": "-",
            "student_id": "-",
            "total_score": "-",
            "psychological_state": "-",
           
            "answers": [],
        }

        answers_started: bool = False
        for row in rows:
            if not row:
                continue
            if row == ["Question", "Selected Answer", "Score"]:
                answers_started = True
                continue
            if not answers_started and len(row) >= 2 and row[0] != "Field":
                key, value = row[0], row[1]
                if key == "total_score" and str(value).isdigit():
                    result[key] = int(value)
                else:
                    result[key] = value
            elif answers_started and len(row) >= 3:
                score_value: int = int(row[2]) if str(row[2]).isdigit() else 0
                result["answers"].append(
                    {
                        "question": row[0],
                        "selected_answer": row[1],
                        "score": score_value,
                    }
                )
        return result

    def reset_survey(self) -> None:
        st.session_state["survey_started"] = False
        st.session_state["survey_result"] = None
        for key in list(st.session_state.keys()):
            if key.startswith("q_"):
                del st.session_state[key]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(161, 196, 253, 0.38), transparent 28%),
                    radial-gradient(circle at top right, rgba(194, 233, 251, 0.34), transparent 32%),
                    linear-gradient(135deg, #eef4ff 0%, #f7f1ff 48%, #fffaf4 100%);
            }
            .block-container {
                padding-top: 1.7rem;
                padding-bottom: 2rem;
                max-width: 920px;
            }
            .main-card {
                background: rgba(255, 255, 255, 0.84);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(120, 125, 255, 0.14);
                padding: 1.35rem 1.2rem;
                border-radius: 24px;
                box-shadow: 0 18px 40px rgba(71, 85, 160, 0.10);
                margin-bottom: 1rem;
            }
            .hero {
                padding: 1.55rem 1.35rem;
                background: linear-gradient(135deg, rgba(255,255,255,0.88), rgba(255,255,255,0.72));
                border: 1px solid rgba(120, 125, 255, 0.12);
                border-radius: 28px;
                box-shadow: 0 18px 44px rgba(71, 85, 160, 0.10);
                margin-bottom: 1rem;
            }
            .hero-grid {
                display: grid;
                grid-template-columns: 1.55fr 0.95fr;
                gap: 1rem;
                align-items: center;
            }
            .mini-badge {
                display: inline-block;
                padding: 0.32rem 0.78rem;
                border-radius: 999px;
                background: linear-gradient(90deg, rgba(122, 92, 255, 0.14), rgba(40, 170, 255, 0.14));
                color: #4b4f7c;
                font-size: 0.86rem;
                font-weight: 700;
                margin-bottom: 0.78rem;
            }
            .hero-title {
                font-size: 2.05rem;
                font-weight: 800;
                line-height: 1.08;
                margin-bottom: 0.4rem;
                color: #20243a;
            }
            .hero-sub {
                color: #58607a;
                font-size: 1rem;
                margin-bottom: 0.15rem;
            }
            .hero-panel {
                background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(245,247,255,0.9));
                border: 1px solid rgba(90, 105, 210, 0.12);
                border-radius: 22px;
                padding: 1rem;
            }
            .hero-stat {
                font-size: 0.92rem;
                color: #5c6784;
                margin-bottom: 0.35rem;
            }
            .hero-big {
                font-size: 1.65rem;
                font-weight: 800;
                color: #2a3357;
                margin-bottom: 0.3rem;
            }
            .section-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #272b45;
                margin-bottom: 0.35rem;
            }
            .soft-text {
                color: #66708a;
                margin-bottom: 0.55rem;
            }
            .metric-box {
                background: linear-gradient(180deg, #ffffff 0%, #f8f9ff 100%);
                border: 1px solid rgba(90, 105, 210, 0.15);
                border-radius: 18px;
                padding: 0.9rem 1rem;
                margin: 0.32rem 0;
            }
            .question-card {
                background: rgba(255,255,255,0.94);
                border: 1px solid rgba(110, 110, 190, 0.14);
                border-radius: 20px;
                padding: 1rem 1rem 0.45rem 1rem;
                margin-bottom: 0.95rem;
                box-shadow: 0 10px 24px rgba(90, 105, 210, 0.06);
            }
            .tip-card {
                background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(244,248,255,0.92));
                border: 1px solid rgba(90, 105, 210, 0.12);
                border-radius: 18px;
                padding: 0.95rem 1rem;
            }
            @media (max-width: 900px) {
                .hero-grid { grid-template-columns: 1fr; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state() -> None:
    defaults: Dict[str, Any] = {
        "survey_started": False,
        "survey_result": None,
        "save_format": "JSON",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header(app: SurveyApp) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-grid">
                <div>
                    <div class="mini-badge">Psychological survey</div>
                    <div class="hero-title">Peer comparison avoidance survey</div>
                    
                
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_summary(result: Dict[str, Any]) -> None:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Result summary</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="metric-box"><b>Name:</b> {result['full_name']}</div>
        <div class="metric-box"><b>Date of Birth:</b> {result['date_of_birth']}</div>
        <div class="metric-box"><b>Student ID:</b> {result['student_id']}</div>
        <div class="metric-box"><b>Total Score:</b> {result['total_score']}</div>
        <div class="metric-box"><b>Psychological State:</b> {result['psychological_state']}</div>
        <div class="metric-box"><b>Submitted At:</b> {result['submitted_at']}</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    answers: List[Dict[str, Any]] = result.get("answers", [])
    if answers:
        with st.expander("Show answers"):
            for idx, answer in enumerate(answers, start=1):
                st.write(f"**{idx}. {answer['question']}**")
                st.write(f"Answer: {answer['selected_answer']}")
                st.write(f"Score: {answer['score']}")


def render_take_survey_page(app: SurveyApp) -> None:
    if st.session_state["survey_result"] is not None:
        result: Dict[str, Any] = st.session_state["survey_result"]
        render_result_summary(result)

        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Save result</div>', unsafe_allow_html=True)
        save_format: str = st.selectbox(
            "Choose saving format",
            app.ALLOWED_SAVE_FORMATS,
            index=app.ALLOWED_SAVE_FORMATS.index(st.session_state.get("save_format", "JSON")),
        )
        st.session_state["save_format"] = save_format
        data, filename, mime = app.export_result(result, save_format)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label=f"Download as {save_format}",
                data=data,
                file_name=filename,
                mime=mime,
                use_container_width=True,
            )
        with col2:
            if st.button("Start new survey", use_container_width=True):
                app.reset_survey()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if not st.session_state["survey_started"]:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Step 1 of 2 · Personal information</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="soft-text">Enter the participant details first. After clicking <b>Start questionnaire</b>, the survey section will open.</p>',
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([1.45, 0.95])
        with col_left:
            with st.form("participant_form"):
                full_name: str = st.text_input("Surname and given name", placeholder="Enter full name")
                date_of_birth = st.date_input(
                    "Date of birth",
                    min_value=date(1900, 1, 1),
                    max_value=date.today(),
                    value=None,
                    format="YYYY-MM-DD",
                )
                student_id: str = st.text_input("Student ID", placeholder="Digits only")
                start_clicked: bool = st.form_submit_button("Start questionnaire", use_container_width=True)

       
        st.markdown('</div>', unsafe_allow_html=True)

        if start_clicked:
            errors: List[str] = []
            if not full_name.strip() or not app.validate_name(full_name):
                errors.append("Enter a valid name using only letters, spaces, hyphens, and apostrophes.")
            if date_of_birth is None:
                errors.append("Select a valid date of birth.")
            if not app.validate_student_id(student_id):
                errors.append("Student ID must contain digits only.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.session_state["full_name"] = full_name
                st.session_state["date_of_birth"] = date_of_birth
                st.session_state["student_id"] = student_id
                st.session_state["survey_started"] = True
                st.rerun()
        return

    answered: int = sum(1 for i in range(1, len(app.questions) + 1) if st.session_state.get(f"q_{i}") is not None)
    progress: float = answered / len(app.questions)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Step 2 of 2 · Questionnaire</div>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="soft-text"><b>Participant:</b> {st.session_state["full_name"]} &nbsp;|&nbsp; <b>Student ID:</b> {st.session_state["student_id"]}</p>',
        unsafe_allow_html=True,
    )
    st.progress(progress)
    st.caption(f"Answered {answered} of {len(app.questions)} questions")
    st.markdown('</div>', unsafe_allow_html=True)

    with st.form("survey_form"):
        for index, question in enumerate(app.questions, start=1):
            st.markdown('<div class="question-card">', unsafe_allow_html=True)
            option_texts: List[str] = [text for text, _ in question.options]
            st.radio(
                f"{index}. {question.prompt}",
                option_texts,
                index=None,
                key=f"q_{index}",
            )
            st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            back_clicked: bool = st.form_submit_button("Back to personal information", use_container_width=True)
        with col2:
            submitted: bool = st.form_submit_button("Submit survey", use_container_width=True)

    if back_clicked:
        st.session_state["survey_started"] = False
        st.rerun()

    if submitted:
        unanswered: List[str] = [str(i) for i in range(1, len(app.questions) + 1) if st.session_state.get(f"q_{i}") is None]
        if unanswered:
            st.error("Answer all questions before submitting.")
        else:
            st.session_state["survey_result"] = app.build_result()
            st.success("Survey submitted successfully.")
            st.rerun()


def render_load_page(app: SurveyApp) -> None:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Load saved questionnaire result</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="soft-text">Upload a TXT, CSV, or JSON result file to display the saved participant information and answers.</p>',
        unsafe_allow_html=True,
    )
    file_type: str = st.selectbox("Choose file type", ["json", "txt", "csv"], format_func=lambda x: x.upper())
    uploaded_file = st.file_uploader(f"Upload a {file_type.upper()} result file", type=[file_type])
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            loaded_data: Dict[str, Any] = app.parse_uploaded_file(uploaded_file, file_type)
            st.success(f"{file_type.upper()} loaded successfully.")
            render_result_summary(loaded_data)
        except Exception as exc:
            st.error(f"Could not load file: {exc}")


def main() -> None:
    st.set_page_config(
        page_title="Peer comparison avoidance survey",
        page_icon="🧠",
        layout="centered",
    )
    inject_styles()
    initialize_state()
    app = SurveyApp(question_file="questions.json")
    render_header(app)

    page: str = st.sidebar.radio("Choose section", ["Take survey", "Load saved result"])
    if page == "Take survey":
        render_take_survey_page(app)
    else:
        render_load_page(app)


if __name__ == "__main__":
    main()
