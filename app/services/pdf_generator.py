import os
import subprocess
import jinja2
from datetime import datetime
import unicodedata

TEMPLATE_DIR = "/app/latex_templates"
OUTPUT_DIR = "/app/generated"


def safe_filename(text):
    text = str(text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return "".join([c for c in text if c.isalnum() or c == "_"])


def generate_pdf(student_data, template_filename, signers):
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    latex_env = jinja2.Environment(
        loader=template_loader,
        block_start_string="\BLOCK{",
        block_end_string="}",
        variable_start_string="\VAR{",
        variable_end_string="}",
        comment_start_string="\#{",
        comment_end_string="}",
        autoescape=False,
    )

    context = student_data.copy()
    context["timestamp"] = datetime.now().strftime("%d.%m.%Y")
    context["template_path"] = TEMPLATE_DIR

    context["signer_left_name"] = signers[0]["name"]
    context["signer_left_role"] = signers[0]["role"]

    context["signer_mid_name"] = signers[1]["name"]
    context["signer_mid_role"] = signers[1]["role"]

    context["signer_right_name"] = signers[2]["name"]
    context["signer_right_role"] = signers[2]["role"]

    template = latex_env.get_template(template_filename)
    rendered_tex = template.render(**context)

    clean_name = safe_filename(student_data.get("name", "Doc"))
    clean_index = str(student_data.get("index", "000"))
    base_filename = (
        f"{clean_name}_{clean_index}_{template_filename.replace('.tex', '')}"
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tex_path = os.path.join(OUTPUT_DIR, f"{base_filename}.tex")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(rendered_tex)

    for _ in range(2):
        subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory",
                OUTPUT_DIR,
                tex_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )

    return f"{base_filename}.pdf"
