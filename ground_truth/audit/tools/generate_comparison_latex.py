"""Generate an Overleaf-ready comparison of normalized ground truth and
the concrete requests actually reported by DRHL.

Ground-truth entries use ``p1`` for variable parameters. DRHL entries retain
the concrete values from ``runs/<application>/analysis/findings.json`` and
``vectors.json``. The table deliberately contains no policy descriptions and
no TP/FP/FN labels.
"""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
GROUND_TRUTH_DIR = HERE.parents[1]
CSV_PATH = GROUND_TRUTH_DIR / "ground_truth.csv"
OUTPUT_PATH = GROUND_TRUTH_DIR / "ground-truth_comparison.tex"


NORMALIZED_ENDPOINTS = {
    "GT-001": "m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1",
    "GT-002": "member.php?id=p1",
    "GT-003": "member.php?id=p1",
    "GT-004": "install/index.php",
    "GT-005": "control/db_backup.php",
    "GT-006": "admin/modifica_band.php",
    "GT-007": "admin/modifica_configurazione.php",
    "GT-008": "admin/modifica_votanti.php",
    "GT-009": "install/index.php",
    "GT-010": "article.php?do=comments&id=p1",
    "GT-011": "article.php?action=delete&do=comments&id=p1",
    "GT-012": "article.php?do=edit&id=p1",
    "GT-013": "article.php?do=editp&id=p1",
    "GT-014": "user.php?do=edit&id=p1",
    "GT-015": "user.php?do=editp (POST: id=p1)",
    "GT-016": "backdoor.php",
    "GT-017": "install.php",
    "GT-018": "secret-cors-1.php",
    "GT-019": "secret-cors-2.php",
    "GT-020": "secret-cors-3.php",
    "GT-021": "about.php",
    "GT-022": "instructions.php?doc=p1",
    "GT-023": "setup.php",
    "GT-024": "install.php",
    "GT-025": "comments.php",
    "GT-026": "generaloptions.php",
    "GT-027": "admin/setup.php",
    "GT-028": "admin/user_add.php",
    "GT-029": "usercp2.php?action=addsubscription&fid=p1&type=forum",
    "GT-030": "users/view.php?userid=p1",
    "GT-031": "users/sample.php?userid=p1",
    "GT-032": "admin/addnews.jsp",
    "GT-033": "admin/addnews2.jsp",
    "GT-034": "admin/adduser.jsp",
    "GT-035": "admin/adduser2.jsp",
    "GT-036": "admin/admin.jsp",
    "GT-037": "admin/editnews.jsp",
    "GT-038": "admin/editnews2.jsp?body=p1&headline=p1",
    "GT-039": "servlet/forum.AddForum",
    "GT-040": "servlet/forum.AddReply",
    "GT-041": "servlet/forum.AddThread",
    "GT-042": "servlet/forum.AddReply (POST: user=p1)",
    "GT-043": "servlet/forum.AddThread (POST: user=p1)",
    "GT-044": "forum/index.jsp?page=editmessage&forum_id=p1&thread_id=p1&reply_id=p1&start=p1",
    "GT-045": "blogger/viewEntry/p1/p1.html",
    "GT-046": "p1/",
    "GT-047": "add_item/",
    "GT-048": "bbs_pub/",
    "GT-049": "categories/p1/topics/p1/comments/p1/edit (POST: action=Update)",
    "GT-050": "categories/p1/topics/p1/comments/p1/edit (POST: action=Delete)",
}


# Concrete requests retained in DRHL's detection artifacts. Actor names are
# included because vertical and horizontal cases can share one normalized URL.
DRHL_DETECTIONS = {
    "GT-001": ("visitor", "GET", "m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=400&width=500"),
    "GT-002": ("user1", "GET", "member.php?id=1"),
    "GT-003": ("user1", "GET", "member.php?id=3"),
    "GT-004": ("visitor", "GET", "install/index.php"),
    "GT-005": ("visitor", "GET", "control/db_backup.php"),
    "GT-006": ("visitor", "POST", "admin/modifica_band.php"),
    "GT-007": ("visitor", "POST", "admin/modifica_configurazione.php"),
    "GT-008": ("visitor", "POST", "admin/modifica_votanti.php"),
    "GT-009": ("visitor", "GET", "install/index.php"),
    "GT-010": ("register", "GET", "article.php?do=comments&id=6"),
    "GT-011": ("register", "POST", "article.php?action=delete&do=comments&id=6"),
    "GT-012": ("user1", "GET", "article.php?do=edit&id=6"),
    "GT-013": ("user1", "POST", "article.php?do=editp&id=6"),
    "GT-014": ("user1", "GET", "user.php?do=edit&id=6"),
    "GT-015": ("user1", "POST", "user.php?do=editp (POST: id=6)"),
    "GT-016": ("visitor", "GET", "backdoor.php"),
    "GT-017": ("visitor", "GET", "install.php"),
    "GT-018": ("visitor", "GET", "secret-cors-1.php"),
    "GT-019": ("visitor", "GET", "secret-cors-2.php"),
    "GT-020": ("visitor", "GET", "secret-cors-3.php"),
    "GT-021": ("visitor", "GET", "about.php"),
    "GT-022": ("visitor", "GET", "instructions.php?doc=copying"),
    "GT-023": ("visitor", "GET", "setup.php"),
    "GT-024": ("visitor", "GET", "install.php"),
    "GT-025": ("visitor", "GET", "comments.php"),
    "GT-026": ("visitor", "POST", "generaloptions.php"),
    "GT-027": ("visitor", "GET", "admin/setup.php"),
    "GT-028": ("visitor", "POST", "admin/user_add.php"),
    "GT-029": ("user1", "GET", "usercp2.php?action=addsubscription&fid=2&type=forum"),
    "GT-030": ("user1", "GET", "users/view.php?userid=11"),
    "GT-031": ("visitor", "GET", "users/sample.php?userid=4"),
    "GT-032": ("visitor", "GET", "admin/addnews.jsp"),
    "GT-033": ("visitor", "POST", "admin/addnews2.jsp"),
    "GT-034": ("visitor", "GET", "admin/adduser.jsp"),
    "GT-035": ("visitor", "POST", "admin/adduser2.jsp"),
    "GT-036": ("visitor", "GET", "admin/admin.jsp"),
    "GT-037": ("visitor", "GET", "admin/editnews.jsp"),
    "GT-038": ("visitor", "GET", "admin/editnews2.jsp?body=DRHL generated body for access-control testing.&headline=AokwZT"),
    "GT-039": ("visitor", "POST", "servlet/forum.AddForum"),
    "GT-040": ("visitor", "POST", "servlet/forum.AddReply"),
    "GT-041": ("visitor", "POST", "servlet/forum.AddThread"),
    "GT-042": ("user1", "POST", "servlet/forum.AddReply (POST: user=user2)"),
    "GT-043": ("user1", "POST", "servlet/forum.AddThread (POST: user=user2)"),
    "GT-044": ("user1", "GET", "forum/index.jsp?page=editmessage&forum_id=0&thread_id=0&reply_id=2&start=0"),
    "GT-045": ("visitor", "GET", "blogger/viewEntry/5444/drhl_test_entry.html"),
    "GT-046": ("visitor", "GET", "eee/"),
    "GT-047": ("user1", "POST", "add_item/"),
    "GT-048": ("visitor", "GET", "bbs_pub/"),
    "GT-049": ("user1", "POST", "categories/1/topics/9/comments/34/edit (POST: action=Update)"),
    "GT-050": ("user1", "POST", "categories/1/topics/9/comments/34/edit (POST: action=Delete)"),
}


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def path_cell(text: str) -> str:
    return rf"\path{{{text}}}"


def render() -> str:
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    ids = {row["ID"] for row in rows}
    if ids != set(NORMALIZED_ENDPOINTS) or ids != set(DRHL_DETECTIONS):
        raise ValueError("Comparison mappings must contain exactly the 50 CSV ground-truth IDs")

    lines = [
        r"% Required packages (add these in the preamble):",
        r"% \usepackage{booktabs,longtable,array,pdflscape,xurl}",
        r"% \newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}",
        r"",
        r"\begin{landscape}",
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\begin{longtable}{@{}L{1.0cm}L{2.0cm}L{0.8cm}L{8.8cm}L{10.0cm}@{}}",
        r"\caption{Per-vulnerability comparison of normalized ground truth and concrete DRHL detections.}\label{tab:ground-truth-comparison}\\",
        r"\toprule",
        r"ID & Application & BAC & Ground Truth (normalized) & DRHL Detection (concrete request) \\",
        r"\midrule",
        r"\endfirsthead",
        r"\multicolumn{5}{c}{\tablename\ \thetable\ (continued)}\\",
        r"\toprule",
        r"ID & Application & BAC & Ground Truth (normalized) & DRHL Detection (concrete request) \\",
        r"\midrule",
        r"\endhead",
        r"\midrule",
        r"\multicolumn{5}{r}{Continued on next page}\\",
        r"\endfoot",
        r"\bottomrule",
        r"\endlastfoot",
    ]

    previous_app = None
    for row in rows:
        gt_id = row["ID"]
        app = row["Application"]
        if previous_app is not None and app != previous_app:
            lines.append(r"\addlinespace[2pt]")
        previous_app = app
        actor, method, concrete_request = DRHL_DETECTIONS[gt_id]
        detection_cell = (
            rf"\textsc{{{method.lower()}}} "
            + path_cell(concrete_request)
            + rf"; actor=\texttt{{{tex_escape(actor)}}}"
        )
        lines.append(
            " & ".join(
                [
                    rf"\texttt{{{gt_id}}}",
                    tex_escape(app),
                    tex_escape(row["BAC Type"]),
                    path_cell(NORMALIZED_ENDPOINTS[gt_id]),
                    detection_cell,
                ]
            )
            + r" \\"
        )

    lines.extend([r"\end{longtable}", r"\endgroup", r"\end{landscape}", ""])
    return "\n".join(lines)


def main() -> None:
    OUTPUT_PATH.write_text(render(), encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
