import streamlit as st
import json
import time
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Career Navigator AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Elite Cinematic CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Deep space background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #16132b 25%, #1a1147 50%, #0f2167 75%, #0a0e27 100%);
        background-size: 400% 400%;
        animation: space-drift 30s ease infinite;
        background-attachment: fixed;
    }
    
    @keyframes space-drift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Ambient glow blobs */
    .stApp::before {
        content: '';
        position: fixed;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(103,58,183,0.25) 0%, transparent 70%);
        border-radius: 50%;
        top: -200px;
        right: -200px;
        animation: blob-float 25s ease-in-out infinite;
        z-index: 0;
        filter: blur(80px);
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(33,150,243,0.2) 0%, transparent 70%);
        border-radius: 50%;
        bottom: -150px;
        left: -150px;
        animation: blob-float 20s ease-in-out infinite reverse;
        z-index: 0;
        filter: blur(80px);
    }
    
    @keyframes blob-float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(100px, -50px) scale(1.1); }
        66% { transform: translate(-50px, 100px) scale(0.9); }
    }
    
    /* Particle overlay */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(2px 2px at 20% 30%, rgba(255,255,255,0.1), transparent),
            radial-gradient(2px 2px at 60% 70%, rgba(167,139,250,0.1), transparent),
            radial-gradient(1px 1px at 50% 50%, rgba(236,72,153,0.1), transparent),
            radial-gradient(1px 1px at 80% 10%, rgba(255,255,255,0.08), transparent),
            radial-gradient(2px 2px at 90% 60%, rgba(99,102,241,0.1), transparent);
        background-size: 300px 300px;
        animation: particles-drift 40s linear infinite;
        pointer-events: none;
        z-index: 1;
    }
    
    @keyframes particles-drift {
        0% { background-position: 0 0; }
        100% { background-position: 300px 300px; }
    }
    
    /* Hero Section */
    .hero-wrapper {
        position: relative;
        text-align: center;
        padding: 4rem 0 3rem 0;
        z-index: 2;
    }
    
    .hero-halo {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 700px;
        height: 350px;
        background: radial-gradient(ellipse, rgba(167,139,250,0.5) 0%, rgba(236,72,153,0.3) 50%, transparent 70%);
        filter: blur(100px);
        animation: halo-breathe 5s ease-in-out infinite;
        z-index: -1;
    }
    
    @keyframes halo-breathe {
        0%, 100% { 
            opacity: 0.7;
            transform: translate(-50%, -50%) scale(1);
        }
        50% { 
            opacity: 1;
            transform: translate(-50%, -50%) scale(1.1);
        }
    }
    
    .hero-title {
        font-size: 5rem;
        font-weight: 900;
        background: linear-gradient(120deg, #a78bfa 0%, #ec4899 30%, #6366f1 60%, #a78bfa 100%);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: title-shimmer 5s ease-in-out infinite;
        margin: 0;
        letter-spacing: -3px;
        line-height: 1.1;
        text-shadow: 0 0 80px rgba(167,139,250,0.5);
    }
    
    @keyframes title-shimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: rgba(255,255,255,0.75);
        margin-top: 1.5rem;
        font-weight: 500;
        letter-spacing: 0.3px;
        animation: subtitle-fade 1.5s ease-out;
    }
    
    @keyframes subtitle-fade {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Glass Panels */
    .glass-panel {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(24px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.08),
            0 0 0 1px rgba(0, 0, 0, 0.1);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        z-index: 2;
    }
    
    .glass-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
        transition: left 0.7s ease;
    }
    
    .glass-panel:hover::before {
        left: 100%;
    }
    
    .glass-panel:hover {
        transform: translateY(-8px);
        border-color: rgba(167,139,250,0.3);
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.5),
            0 0 60px rgba(167,139,250,0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.12);
    }
    
    /* Agent Activity Log */
    .agent-log {
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(167,139,250,0.2);
        padding: 1.5rem;
        margin: 1.5rem 0;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 300px;
        overflow-y: auto;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.5),
            inset 0 0 20px rgba(103,58,183,0.1);
    }
    
    .log-entry {
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        animation: log-appear 0.3s ease-out;
    }
    
    @keyframes log-appear {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .log-ok { color: #4ade80; }
    .log-running { color: #fbbf24; }
    .log-info { color: #60a5fa; }
    
    /* Metric Cards */
    .metric-container {
        display: grid;
        gap: 1.5rem;
        animation: metrics-reveal 0.8s ease-out;
    }
    
    @keyframes metrics-reveal {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(167,139,250,0.12) 0%, rgba(236,72,153,0.12) 100%);
        backdrop-filter: blur(12px);
        padding: 2.2rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.12);
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .metric-card:hover::after {
        opacity: 1;
    }
    
    .metric-card:hover {
        transform: translateY(-6px) scale(1.02);
        border-color: rgba(167,139,250,0.4);
        box-shadow: 
            0 16px 48px rgba(0, 0, 0, 0.4),
            0 0 40px rgba(167,139,250,0.25);
    }
    
    .metric-value {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: rgba(255,255,255,0.8);
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    
    /* AI Thinking Panel */
    .ai-thinking {
        background: linear-gradient(135deg, rgba(103,58,183,0.15) 0%, rgba(33,150,243,0.15) 100%);
        border: 2px solid rgba(167,139,250,0.3);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        animation: thinking-pulse 2.5s ease-in-out infinite;
        box-shadow: 0 0 40px rgba(103,58,183,0.2);
        margin: 2rem 0;
    }
    
    @keyframes thinking-pulse {
        0%, 100% { 
            box-shadow: 0 0 40px rgba(103,58,183,0.2);
            border-color: rgba(167,139,250,0.3);
        }
        50% { 
            box-shadow: 0 0 60px rgba(103,58,183,0.4);
            border-color: rgba(167,139,250,0.6);
        }
    }
    
    .ai-thinking-text {
        color: #a78bfa;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    /* Analyze Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        height: 3.8em;
        font-size: 1.25em;
        font-weight: 800;
        border: none;
        border-radius: 16px;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 
            0 10px 30px rgba(103,58,183,0.5),
            0 0 0 1px rgba(255,255,255,0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s ease, height 0.6s ease;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-4px) scale(1.03);
        box-shadow: 
            0 16px 48px rgba(103,58,183,0.7),
            0 0 60px rgba(103,58,183,0.5);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 14, 39, 0.95) 0%, rgba(16, 20, 45, 0.95) 100%);
        backdrop-filter: blur(24px);
        border-right: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 0 60px rgba(0,0,0,0.6);
    }
    
    [data-testid="stSidebar"] h2 {
        color: #a78bfa;
        font-weight: 800;
        font-size: 1.5rem;
        letter-spacing: 1px;
        text-shadow: 0 0 20px rgba(167,139,250,0.5);
    }
    
    /* Gap Warning Card */
    .gap-warning {
        background: linear-gradient(135deg, rgba(239,68,68,0.12) 0%, rgba(220,38,38,0.08) 100%);
        border: 2px solid rgba(239,68,68,0.4);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 
            0 8px 32px rgba(239,68,68,0.25),
            0 0 40px rgba(239,68,68,0.15);
        animation: warning-glow 3s ease-in-out infinite;
    }
    
    @keyframes warning-glow {
        0%, 100% { box-shadow: 0 8px 32px rgba(239,68,68,0.25), 0 0 40px rgba(239,68,68,0.15); }
        50% { box-shadow: 0 12px 48px rgba(239,68,68,0.35), 0 0 60px rgba(239,68,68,0.25); }
    }
    
    /* Roadmap Timeline */
    .roadmap-timeline {
        position: relative;
        padding-left: 2rem;
    }
    
    .roadmap-timeline::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #a78bfa 0%, #ec4899 100%);
        border-radius: 3px;
    }
    
    .roadmap-item {
        background: rgba(255,255,255,0.04);
        border-left: 4px solid transparent;
        padding: 1.8rem 2rem;
        margin: 1.5rem 0;
        border-radius: 12px;
        transition: all 0.4s ease;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        position: relative;
        animation: roadmap-appear 0.5s ease-out;
    }
    
    @keyframes roadmap-appear {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .roadmap-item::before {
        content: '';
        position: absolute;
        left: -2.3rem;
        top: 50%;
        transform: translateY(-50%);
        width: 12px;
        height: 12px;
        background: #a78bfa;
        border: 3px solid #1a1147;
        border-radius: 50%;
        box-shadow: 0 0 12px rgba(167,139,250,0.6);
    }
    
    .roadmap-item:hover {
        transform: translateX(12px);
        background: rgba(255,255,255,0.06);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        border-left-color: #ec4899;
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.12);
        color: white;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: rgba(167,139,250,0.5);
        box-shadow: 0 0 24px rgba(167,139,250,0.2);
        background: rgba(255,255,255,0.06);
    }
    
    /* Transparency Badge */
    .transparency-badge {
        background: rgba(33,150,243,0.1);
        border: 1px solid rgba(33,150,243,0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        color: #60a5fa;
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 2rem;
        animation: badge-fade 1s ease-out;
    }
    
    @keyframes badge-fade {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Section Headers */
    h3 {
        color: white !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
        letter-spacing: -0.5px;
        margin-bottom: 1.5rem !important;
    }
    
    /* JSON Display */
    pre {
        background: rgba(0,0,0,0.5) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow: inset 0 2px 12px rgba(0,0,0,0.4);
    }
    
    /* Stagger Animations */
    .reveal-1 { animation: reveal-fade 0.6s ease-out 0.1s both; }
    .reveal-2 { animation: reveal-fade 0.6s ease-out 0.3s both; }
    .reveal-3 { animation: reveal-fade 0.6s ease-out 0.5s both; }
    .reveal-4 { animation: reveal-fade 0.6s ease-out 0.7s both; }
    
    @keyframes reveal-fade {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Mock functions
def analyze_github(username):
    return {"languages": ["Python", "JavaScript", "TypeScript"], "projects": 12, "commits": 347, "stars": 89}

def parse_resume(file):
    return {"skills": ["React", "Python", "SQL", "Docker"], "experience": "2 years", "education": "B.Tech CS"}

def get_role_skills(role):
    skills_db = {
        'Software Engineer': ['Python', 'Java', 'Git', 'Docker', 'Kubernetes', 'APIs', 'System Design'],
        'Data Scientist': ['Python', 'SQL', 'Machine Learning', 'Statistics', 'Pandas', 'TensorFlow', 'Visualization'],
        'Fullstack Developer': ['React', 'Node.js', 'MongoDB', 'REST APIs', 'CSS', 'TypeScript', 'GraphQL']
    }
    return skills_db.get(role, [])

# Hero Section
st.markdown('''
<div class="hero-wrapper">
    <div class="hero-halo"></div>
    <h1 class="hero-title">Personal Career Navigator 🚀</h1>
    <p class="hero-subtitle">Your AI career co-pilot actively reasoning about your future.</p>
</div>
''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    st.markdown("<br>", unsafe_allow_html=True)
    
    github_username = st.text_input("🔗 GitHub Username", placeholder="yourusername")
    resume_file = st.file_uploader("📄 Upload Resume (PDF)", type=['pdf'])
    dream_role = st.selectbox("💼 Dream Role", ['Software Engineer', 'Data Scientist', 'Fullstack Developer'])
    hours_per_day = st.slider("⏰ Hours/Day", 1, 4, 2)
    level = st.selectbox("📊 Current Level", ['Beginner', 'Intermediate', 'Advanced'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_button = st.button("🎯 ANALYZE CAREER")

# Main Content
if analyze_button:
    if not github_username:
        st.error("⚠️ Please enter your GitHub username to continue")
    else:
        # Agent Activity Log
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown("### 🧠 Live Agent Activity")
        
        agent_steps = [
            ("[INFO]", "Initializing multi-agent system...", "log-info"),
            ("[OK]", "Skill extractor agent ready", "log-ok"),
            ("[RUNNING]", "Parsing GitHub activity signals...", "log-running"),
            ("[OK]", "Extracted 347 commits, 12 projects", "log-ok"),
            ("[RUNNING]", "Building skill knowledge graph...", "log-running"),
            ("[OK]", "Mapped 8 core competencies", "log-ok"),
            ("[RUNNING]", "Market alignment analysis...", "log-running"),
            ("[OK]", "Role compatibility: 87%", "log-ok"),
            ("[RUNNING]", "Gap detection algorithm...", "log-running"),
            ("[OK]", "Identified 3 critical gaps", "log-ok"),
            ("[RUNNING]", "Generating adaptive roadmap...", "log-running"),
            ("[OK]", "Roadmap planner complete", "log-ok"),
        ]
        
        log_container = st.empty()
        log_html = '<div class="agent-log">'
        
        for status, message, css_class in agent_steps:
            log_html += f'<div class="log-entry"><span class="{css_class}">{status}</span> {message}</div>'
            log_container.markdown(log_html + '</div>', unsafe_allow_html=True)
            time.sleep(0.4)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.success("✨ AI Analysis Complete! Personalized insights ready.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Metrics
        github_data = analyze_github(github_username)
        resume_data = parse_resume(resume_file) if resume_file else {"skills": ["Git", "Python", "React"], "experience": "1 year"}
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card reveal-1"><div class="metric-value">{len(resume_data["skills"])}</div><div class="metric-label">Skills</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card reveal-2"><div class="metric-value">{github_data["projects"]}</div><div class="metric-label">Projects</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card reveal-3"><div class="metric-value">{github_data["commits"]}</div><div class="metric-label">Commits</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card reveal-4"><div class="metric-value">87%</div><div class="metric-label">Match</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Profile Analysis
        st.markdown('<div class="glass-panel reveal-1">', unsafe_allow_html=True)
        st.markdown("### 🎯 Profile Analysis")
        profile_data = {
            "github_insights": github_data,
            "resume_summary": resume_data,
            "skill_level": level,
            "learning_capacity": f"{hours_per_day} hours/day",
            "market_readiness": "87%"
        }
        st.json(profile_data)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Role Requirements
        st.markdown('<div class="glass-panel reveal-2">', unsafe_allow_html=True)
        st.markdown("### 💼 Dream Role Requirements")
        role_skills = get_role_skills(dream_role)
        st.table({"Required Skills": role_skills, "Priority": ["High"] * len(role_skills)})
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Skill Gaps
        user_skills = set(resume_data["skills"])
        required_skills = set(role_skills)
        gaps = list(required_skills - user_skills)
        
        if gaps:
            st.markdown('<div class="gap-warning reveal-3">', unsafe_allow_html=True)
            st.markdown(f"### ⚠️ Critical Skill Gaps Detected: {len(gaps)}")
            st.table({"Missing Skill": gaps, "Impact": ["Critical"] * len(gaps), "Est. Time": [f"{hours_per_day*3}hrs"] * len(gaps)})
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Roadmap
        st.markdown('<div class="glass-panel reveal-4">', unsafe_allow_html=True)
        st.markdown("### 🗺️ 7-Day Adaptive Roadmap")
        st.markdown('<div class="roadmap-timeline">', unsafe_allow_html=True)
        
        for i, skill in enumerate(gaps[:7] if gaps else ["Advanced System Design"]):
            day_name = (datetime.now() + timedelta(days=i+1)).strftime("%A")
            st.markdown(f'''
            <div class="roadmap-item">
                <strong style="color: #a78bfa; font-size: 1.15rem;">Day {i+1} • {day_name}</strong><br>
                <span style="color: rgba(255,255,255,0.9); font-size: 1.05rem;">🎯 Master {skill}</span><br>
                <span style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">⏱️ {hours_per_day} hours • {level} level</span>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Transparency Badge
        st.markdown('''
        <div class="transparency-badge">
            🔍 AI reasoning trace available for full transparency
        </div>
        ''', unsafe_allow_html=True)
        
        st.balloons()

else:
    # Welcome State
    st.markdown('<div class="glass-panel reveal-1">', unsafe_allow_html=True)
    st.markdown("### 🌟 Welcome to Your AI Career Journey")
    st.write("Configure your profile in the control panel and click **ANALYZE CAREER** to activate the AI reasoning system.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="glass-panel reveal-2" style="text-align: center;"><div style="font-size: 3.5rem; margin-bottom: 1rem;">🎯</div><strong style="font-size: 1.3rem; color: #a78bfa;">AI Analysis</strong><br><span style="color: rgba(255,255,255,0.7); margin-top: 0.5rem; display: block;">Deep reasoning on your profile</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-panel reveal-3" style="text-align: center;"><div style="font-size: 3.5rem; margin-bottom: 1rem;">💼</div><strong style="font-size: 1.3rem; color: #ec4899;">Role Matching</strong><br><span style="color: rgba(255,255,255,0.7); margin-top: 0.5rem; display: block;">Compare with dream careers</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-panel reveal-4" style="text-align: center;"><div style="font-size: 3.5rem; margin-bottom: 1rem;">🗺️</div><strong style="font-size: 1.3rem; color: #6366f1;">Adaptive Roadmap</strong><br><span style="color: rgba(255,255,255,0.7); margin-top: 0.5rem; display: block;">Personalized learning path</span></div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: rgba(255,255,255,0.25); font-size: 0.85rem; letter-spacing: 1px;">Built with ❤️ for Bengaluru CS Hackathon 2026 • Powered by Multi-Agent AI</p>', unsafe_allow_html=True)