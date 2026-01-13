# 標準ライブラリのみで動く最小Webアプリ（BMI計算機）
# Render / ローカル共通対応

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>BMI計算機</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ font-family: sans-serif; background: #f5f5f5; }}
    .container {{
      max-width: 420px;
      margin: 40px auto;
      background: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}
    h1 {{ text-align: center; }}
    label {{ display: block; margin-top: 12px; }}
    input {{
      width: 100%;
      padding: 8px;
      margin-top: 4px;
      box-sizing: border-box;
    }}
    .buttons {{
      display: flex;
      gap: 8px;
      margin-top: 16px;
    }}
    button {{
      flex: 1;
      padding: 10px;
      cursor: pointer;
    }}
    .result {{
      margin-top: 16px;
      padding: 12px;
      background: #eef;
      border-radius: 6px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>BMI計算機</h1>
    <form method="POST">
      <label>
        身長（cm）
        <input type="number" step="0.1" name="height" value="{height}">
      </label>
      <label>
        体重（kg）
        <input type="number" step="0.1" name="weight" value="{weight}">
      </label>
      <div class="buttons">
        <button type="submit">計算する</button>
        <button type="button" onclick="clearForm()">クリア</button>
      </div>
    </form>

    {result_html}
  </div>

  <script>
    function clearForm() {{
      document.querySelector('input[name="height"]').value = '';
      document.querySelector('input[name="weight"]').value = '';
    }}
  </script>
</body>
</html>
"""

def calc_bmi(height_cm, weight_kg):
    try:
        h = float(height_cm) / 100.0
        w = float(weight_kg)
        if h <= 0 or w <= 0:
            return 0.0, "判定不能"
        bmi = w / (h * h)
    except Exception:
        return 0.0, "判定不能"

    if bmi < 18.5:
        judge = "低体重"
    elif bmi < 25:
        judge = "普通体重"
    elif bmi < 30:
        judge = "肥満（1度）"
    else:
        judge = "肥満（2度以上）"

    return bmi, judge

class Handler(BaseHTTPRequestHandler):
    def _send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        html = HTML_TEMPLATE.format(
            height="",
            weight="",
            result_html=""
        )
        self._send_html(html)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        params = parse_qs(body)

        height = params.get("height", [""])[0]
        weight = params.get("weight", [""])[0]

        bmi, judge = calc_bmi(height, weight)

        if bmi > 0:
            result_html = f"""
            <div class="result">
              <strong>BMI:</strong> {bmi:.2f}<br>
              <strong>判定:</strong> {judge}
            </div>
            """
        else:
            result_html = """
            <div class="result">
              数値を正しく入力してください。
            </div>
            """

        html = HTML_TEMPLATE.format(
            height=height,
            weight=weight,
            result_html=result_html
        )
        self._send_html(html)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Listening on port {port}...")
    server.serve_forever()
