import streamlit as st

from pdf_parser import extract_text_from_pdf
from scorer import calculate_score


# Page configuration
st.set_page_config(
    page_title="ResumeMatch AI",
    page_icon="🎯",
    layout="wide"
)


# Custom styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fb;
    }

    [data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }

    [data-testid="stMetricLabel"] p {
        color: #555555 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: #111827 !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Header
st.title("🎯 ResumeMatch AI")
st.subheader("AI-powered Resume & Job Description Matcher")

st.write(
    "Upload your resume, provide a job description, "
    "and discover how well your skills align with the role."
)

st.divider()


# Input section
left_column, right_column = st.columns(2)

with left_column:
    st.markdown("### 📄 Upload Your Resume")

    uploaded_resume = st.file_uploader(
        "Choose a PDF resume",
        type=["pdf"]
    )

with right_column:
    st.markdown("### 💼 Job Description")

    job_description = st.text_area(
        "Paste the job description here",
        height=220,
        placeholder=(
            "Example: We are looking for an AI/ML intern "
            "with Python, SQL, Machine Learning..."
        )
    )


# Analyze button
if st.button("🚀 Analyze Resume", use_container_width=True):

    if uploaded_resume is None:
        st.error("Please upload a PDF resume.")

    elif not job_description.strip():
        st.error("Please enter a job description.")

    else:
        try:
            with st.spinner("Analyzing your resume..."):

                resume_text = extract_text_from_pdf(
                    uploaded_resume
                )

                if not resume_text.strip():
                    st.error(
                        "No text was found in this PDF. "
                        "It may be a scanned document."
                    )

                else:
                    results = calculate_score(
                        resume_text,
                        job_description
                    )

                    st.success("Analysis completed!")

                    st.divider()
                    st.markdown("## 📊 Analysis Results")

                    # ATS-style 
                    # score metrics
                    st.markdown("### 🎯 ATS-Style Resume Score")

                    st.caption(
                        "An estimated compatibility score based on skills, "
                        "text relevance, and resume section coverage."
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    col1.metric(
                        "Overall ATS Score",
                        f"{results['overall_score']:.1f}/100"
                    )

                    col2.metric(
                        "Skill Match",
                        f"{results['skill_score']:.1f}%"
                    )

                    col3.metric(
                        "Text Similarity",
                        f"{results['text_similarity']:.1f}%"
                    )

                    col4.metric(
                        "Section Coverage",
                        f"{results['section_score']:.1f}%"
                    )

                    st.progress(
                        min(max(int(results["overall_score"]), 0), 100)
                    )

                    st.divider()

                    # Resume section analysis
                    st.markdown("### 📋 Resume Section Analysis")

                    section_details = results["section_details"]

                    section_columns = st.columns(len(section_details))

                    for column, (section, score) in zip(
                        section_columns,
                        section_details.items()
                    ):
                        with column:
                            if score == 100:
                                st.success(f"✓ {section}")
                                st.caption("Detected")
                            else:
                                st.warning(f"○ {section}")
                                st.caption("Not detected")
                    # Skill Match Breakdown
                    import plotly.graph_objects as go

                    st.markdown("### 📊 Skill Match Breakdown")

                    matched_count = len(results["matched_skills"])
                    missing_count = len(results["missing_skills"])
                    total_count = matched_count + missing_count

                    if total_count > 0:
                        chart_col, info_col = st.columns([1.2, 1])

                        with chart_col:
                            fig = go.Figure(
                                data=[
                                    go.Pie(
                                        labels=[
                                            "Matched Skills",
                                            "Missing Skills"
                                        ],
                                        values=[
                                            matched_count,
                                            missing_count
                                        ],
                                        hole=0.65,
                                        marker=dict(
                                            colors=["#22C55E", "#F87171"],
                                            line=dict(
                                                color="#111827",
                                                width=3
                                            )
                                        ),
                                        textinfo="none",
                                        sort=False,
                                        hovertemplate=(
                                            "<b>%{label}</b><br>"
                                            "Count: %{value}<br>"
                                            "Percentage: %{percent}"
                                            "<extra></extra>"
                                        )
                                    )
                                ]
                            )

                            fig.update_layout(
                                height=300,
                                showlegend=False,
                                margin=dict(l=10, r=10, t=10, b=10),
                                paper_bgcolor="rgba(0,0,0,0)",
                                annotations=[
                                    dict(
                                        text=(
                                            f"<b>{matched_count}</b>"
                                            f"<br><sup>of {total_count} skills</sup>"
                                        ),
                                        x=0.5,
                                        y=0.5,
                                        font=dict(
                                            size=23,
                                            color="#FFFFFF"
                                        ),
                                        showarrow=False
                                    )
                                ]
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True,
                                config={"displayModeBar": False}
                            )

                        with info_col:
                            st.markdown("#### Skill Coverage")

                            st.markdown(
                                f"""
                                <div style="
                                    background:#123524;
                                    padding:18px;
                                    border-radius:12px;
                                    border-left:5px solid #22C55E;
                                    margin-bottom:12px;">
                                    <div style="color:#86EFAC;font-size:14px;">
                                        MATCHED SKILLS
                                    </div>
                                    <div style="color:white;font-size:32px;font-weight:700;">
                                        {matched_count}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            st.markdown(
                                f"""
                                <div style="
                                    background:#3B2025;
                                    padding:18px;
                                    border-radius:12px;
                                    border-left:5px solid #F87171;
                                    margin-bottom:12px;">
                                    <div style="color:#FCA5A5;font-size:14px;">
                                        MISSING SKILLS
                                    </div>
                                    <div style="color:white;font-size:32px;font-weight:700;">
                                        {missing_count}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            coverage = (matched_count / total_count) * 100

                            st.markdown(
                                f"**Skill coverage:** {coverage:.1f}%"
                            )

                            st.progress(int(coverage))

                    else:
                        st.info(
                            "No technical skills were detected in the job description. "
                            "Try adding specific skills such as Python, SQL, or Machine Learning."
                        )
                        
                    # Skill analysis
                    matched_column, missing_column = st.columns(2)

                    with matched_column:
                        st.markdown("### ✅ Matched Skills")

                        if results["matched_skills"]:
                            for skill in results["matched_skills"]:
                                st.write(f"✓ {skill}")
                        else:
                            st.write("No matching skills found.")

                    with missing_column:
                        st.markdown("### 📌 Missing Skills")

                        if results["missing_skills"]:
                            for skill in results["missing_skills"]:
                                st.write(f"• {skill}")
                        else:
                            st.write(
                                "All detected required skills "
                                "were found in the resume."
                            )

                    # Additional skills
                    with st.expander("View additional resume skills"):
                        if results["extra_skills"]:
                            st.write(
                                ", ".join(results["extra_skills"])
                            )
                        else:
                            st.write(
                                "No additional skills identified."
                            )

                                        # Personalized improvement suggestions
                    st.markdown(
                        "### 💡 Personalized Improvement Suggestions"
                    )

                    if results["suggestions"]:
                        for suggestion in results["suggestions"]:
                            st.info(suggestion)

                    if results["missing_skills"]:
                        st.markdown("#### Skills to Work On")

                        for skill in results["missing_skills"]:
                            st.write(f"• {skill}")

                    st.caption(
                        "This score is an estimate based on "
                        "detected skills and text similarity. "
                        "It is not an official ATS score or a "
                        "prediction of hiring success."
                    )

        except Exception as error:
            st.error(
                f"Something went wrong during analysis: {error}"
            )


# Footer
st.divider()

st.caption(
    "ResumeMatch AI | Built with Python, "
    "Scikit-learn, PyMuPDF and Streamlit"
)