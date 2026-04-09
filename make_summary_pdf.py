from pathlib import Path


def esc(text: str) -> str:
    return text.replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)')


def wrap(text: str, width: int):
    words = text.split()
    lines = []
    line = ''
    for w in words:
        trial = (line + ' ' + w).strip()
        if len(trial) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


out_path = Path(r"G:\\Ejob_PROJECT\\myapp\\ai_resume_app_summary.pdf")

sections = [
    ("APP SUMMARY - AI Resume Analyzer", []),
    (
        "What it is",
        [
            "A Django web app where authenticated users upload PDF resumes, get sector-based skill matching and scores, and use Gemini-powered interview/career tools.",
            "Core flow in repo: register/login -> upload resume -> review dashboard report -> interview or AI suggestion.",
        ],
    ),
    (
        "Who it's for",
        [
            "Primary persona: individual job seekers/candidates tracking their resumes and preparing for interviews.",
        ],
    ),
    (
        "What it does",
        [
            "User registration/login/logout using Django auth.",
            "Upload PDF resume with required sector (tech/commerce/marketing/engineering/healthcare).",
            "Extract resume text using PyPDF2.",
            "Compare text against sector skill lists and compute match score.",
            "Show matched/missing skills and score on dashboard.",
            "Generate mock interview questions and feedback using Gemini.",
            "Provide AI career assistant suggestions from freeform prompts.",
        ],
    ),
    (
        "How it works (repo evidence)",
        [
            "Frontend: Django templates (dashboard/upload/interview/ai_suggest/login/register).",
            "Backend: Django app 'analyzer' (urls, views, models, forms) wired into project urls.",
            "Data: SQLite default DB with Resume model (file, extracted_text, sector, matched/missing skills, score, timestamp, user FK).",
            "Flow: PDF saved to media/resumes -> text extraction/normalization -> skill matching/scoring -> persist -> dashboard display.",
            "AI service: Gemini client initialized from GEMINI_API_KEY and used for interview + career assistant prompts.",
        ],
    ),
    (
        "How to run (minimal)",
        [
            "1) cd G:/Ejob_PROJECT/myapp/ai_resume",
            "2) Ensure dependencies are installed in your Python environment (Not found in repo: requirements/pyproject).",
            "3) Set GEMINI_API_KEY in ai_resume/.env.",
            "4) Run: python manage.py migrate",
            "5) Run: python manage.py runserver",
            "6) Open app, register/login, upload a PDF resume.",
        ],
    ),
    (
        "Not found in repo",
        [
            "Dependency manifest (requirements.txt/pyproject.toml/Pipfile).",
            "Documented install/setup guide (README).",
            "Production deployment config (project is in DEBUG=True).",
        ],
    ),
]

# Basic single-page layout on US Letter.
page_w = 612
page_h = 792
left = 42
right = 570
y = 760
leading = 12
font_title = 16
font_h = 11
font_body = 9

content_lines = []
for title, bullets in sections:
    if title == "APP SUMMARY - AI Resume Analyzer":
        content_lines.append(("title", title))
        content_lines.append(("space", ""))
        continue
    content_lines.append(("heading", title))
    for b in bullets:
        wrapped = wrap(b, 95)
        if wrapped:
            content_lines.append(("bullet", "- " + wrapped[0]))
            for cont in wrapped[1:]:
                content_lines.append(("cont", "  " + cont))
    content_lines.append(("space", ""))

# Keep one page by tightening if needed.
def needed_height(lines):
    h = 0
    for kind, _ in lines:
        if kind == "title":
            h += 20
        elif kind == "heading":
            h += 14
        elif kind == "space":
            h += 5
        else:
            h += 10
    return h

if needed_height(content_lines) > 730:
    leading = 10
    font_h = 10
    font_body = 8

stream_lines = []
for kind, text in content_lines:
    if kind == "title":
        stream_lines.append(f"BT /F2 {font_title} Tf {left} {y} Td ({esc(text)}) Tj ET")
        y -= 20
    elif kind == "heading":
        stream_lines.append(f"BT /F2 {font_h} Tf {left} {y} Td ({esc(text)}) Tj ET")
        y -= 12
    elif kind == "space":
        y -= 4
    else:
        if y < 35:
            break
        stream_lines.append(f"BT /F1 {font_body} Tf {left} {y} Td ({esc(text)}) Tj ET")
        y -= leading

content = "\n".join(stream_lines).encode("latin-1", errors="replace")

objects = []

def add_obj(data: bytes):
    objects.append(data)
    return len(objects)

font1 = add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
font2 = add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
contents = add_obj(b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream")
page = add_obj(
    b"<< /Type /Page /Parent 5 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 "
    + str(font1).encode()
    + b" 0 R /F2 "
    + str(font2).encode()
    + b" 0 R >> >> /Contents "
    + str(contents).encode()
    + b" 0 R >>"
)
pages = add_obj(b"<< /Type /Pages /Kids [" + str(page).encode() + b" 0 R] /Count 1 >>")
catalog = add_obj(b"<< /Type /Catalog /Pages " + str(pages).encode() + b" 0 R >>")

pdf = bytearray(b"%PDF-1.4\n")
offsets = [0]
for i, obj in enumerate(objects, start=1):
    offsets.append(len(pdf))
    pdf.extend(f"{i} 0 obj\n".encode("ascii"))
    pdf.extend(obj)
    pdf.extend(b"\nendobj\n")

xref_pos = len(pdf)
pdf.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
pdf.extend(b"0000000000 65535 f \n")
for off in offsets[1:]:
    pdf.extend(f"{off:010d} 00000 n \n".encode("ascii"))
pdf.extend(
    b"trailer\n<< /Size "
    + str(len(objects) + 1).encode()
    + b" /Root "
    + str(catalog).encode()
    + b" 0 R >>\nstartxref\n"
    + str(xref_pos).encode()
    + b"\n%%EOF\n"
)

out_path.write_bytes(pdf)
print(out_path)
