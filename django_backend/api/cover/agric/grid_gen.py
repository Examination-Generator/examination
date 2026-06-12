def generate_examiner_grid_html() -> str:
    rows = [
        {"section": "A", "question": "1-15", "max_score": 30},
        {"section": "B", "question": "16-19", "max_score": 20},
        {"section": "C", "question": "", "max_score": 20},
        {"section": "",  "question": "", "max_score": 20},
    ]

    s_body      = "font-family:Arial,sans-serif;display:flex;justify-content:center;padding:30px;"
    s_container = "width:480px;"
    s_heading   = "text-align:center;color:#cc0000;font-size:1.1rem;margin-bottom:10px;"
    s_table     = "border-collapse:collapse;width:100%;"
    s_th        = "border:1px solid #333;padding:8px 12px;text-align:center;font-size:0.9rem;background-color:#f0f0f0;font-weight:bold;"
    s_td        = "border:1px solid #333;padding:8px 12px;text-align:center;font-size:0.9rem;"
    s_td_bold   = s_td + "font-weight:bold;"
    s_td_total  = s_td + "font-weight:bold;background-color:#f0f0f0;"
    s_td_wide   = s_td + "min-width:80px;"

    html = f"""
  <div style="{s_container}">
    <h2 style="{s_heading}">For Examiner's Use Only</h2>
    <table style="{s_table}">
      <thead>
        <tr>
          <th style="{s_th}">Section</th>
          <th style="{s_th}">Question</th>
          <th style="{s_th}">Maximum Score</th>
          <th style="{s_th}{s_td_wide}">Candidate's Score</th>
        </tr>
      </thead>
      <tbody>
"""

    section_c_rows = [r for r in rows if r["section"] in ("C", "")]
    regular_rows   = [r for r in rows if r not in section_c_rows]

    for row in regular_rows:
        html += f"""        <tr>
          <td style="{s_td_bold}">{row['section']}</td>
          <td style="{s_td}">{row['question']}</td>
          <td style="{s_td}">{row['max_score']}</td>
          <td style="{s_td_wide}"></td>
        </tr>
"""

    # Section C with rowspan
    html += f"""        <tr>
          <td rowspan="{len(section_c_rows)}" style="{s_td_bold}">C</td>
          <td style="{s_td}"></td>
          <td style="{s_td}">{section_c_rows[0]['max_score']}</td>
          <td style="{s_td_wide}"></td>
        </tr>
"""
    for row in section_c_rows[1:]:
        html += f"""        <tr>
          <td style="{s_td}"></td>
          <td style="{s_td}">{row['max_score']}</td>
          <td style="{s_td_wide}"></td>
        </tr>
"""

    total = sum(r["max_score"] for r in rows)
    html += f"""        <tr>
          <td colspan="2" style="{s_td_total}">Total Score</td>
          <td style="{s_td_total}">{total}</td>
          <td style="{s_td_wide}"></td>
        </tr>
      </tbody>
    </table>
  </div>
"""
    return html


