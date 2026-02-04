from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from flask import Flask, jsonify, render_template, request
from markupsafe import escape
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "roles.json"
MAX_TEXT_LENGTH = 8000

app = Flask(__name__)


@dataclass
class RoleProfile:
    name: str
    skills: List[str]
    description: str


@dataclass
class AnalysisResult:
    role: str
    similarity: float
    matched_skills: List[str]
    missing_skills: List[str]
    roadmap: List[str]


def load_roles() -> List[RoleProfile]:
    with open(DATA_PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return [RoleProfile(**role) for role in data["roles"]]


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def extract_skills(text: str, skills_catalog: List[str]) -> List[str]:
    normalized = normalize_text(text)
    return sorted({skill for skill in skills_catalog if skill.lower() in normalized})


def build_roadmap(missing_skills: List[str]) -> List[str]:
    if not missing_skills:
        return [
            "You already cover the core skills for this role.",
            "Keep building projects to deepen your expertise.",
        ]
    roadmap = [
        "Focus on fundamentals and build a mini project for each new skill.",
        "Follow with a capstone project that combines the missing skills.",
        "Document progress in a portfolio or GitHub repository.",
    ]
    roadmap.extend(
        [f"Learn and practice: {skill}." for skill in missing_skills]
    )
    return roadmap


def analyze_resume(resume_text: str, role: RoleProfile) -> AnalysisResult:
    resume_text = normalize_text(resume_text)
    skills_text = " ".join(role.skills)
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([resume_text, skills_text])
    similarity_score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

    matched_skills = extract_skills(resume_text, role.skills)
    missing_skills = [
        skill for skill in role.skills if skill not in matched_skills
    ]

    return AnalysisResult(
        role=role.name,
        similarity=round(similarity_score * 100, 1),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        roadmap=build_roadmap(missing_skills),
    )


@app.route("/")
def index() -> str:
    roles = load_roles()
    return render_template("index.html", roles=roles)


@app.post("/analyze")
def analyze() -> tuple:
    payload = request.get_json(silent=True) or {}
    resume_text = escape(payload.get("resume", ""))
    role_name = escape(payload.get("role", ""))

    if not resume_text or not role_name:
        return jsonify({"error": "Resume text and role are required."}), 400

    if len(resume_text) > MAX_TEXT_LENGTH:
        return (
            jsonify({"error": "Resume text exceeds maximum length."}),
            400,
        )

    roles = load_roles()
    role_lookup = {role.name: role for role in roles}
    selected_role = role_lookup.get(role_name)
    if not selected_role:
        return jsonify({"error": "Role not found."}), 404

    result = analyze_resume(resume_text, selected_role)
    return jsonify(
        {
            "role": result.role,
            "similarity": result.similarity,
            "matched_skills": result.matched_skills,
            "missing_skills": result.missing_skills,
            "roadmap": result.roadmap,
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
