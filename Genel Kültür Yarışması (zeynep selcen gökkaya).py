import http.server
import json
import socketserver
import threading
import time
import webbrowser

PORT = 8000

# 10 Adet Genel Kültür Sorusu
QUESTIONS = [
    {
        "q": "Türkiye'nin başkenti neresidir?",
        "options": ["İstanbul", "Ankara", "İzmir", "Bursa"],
        "answer": 1,
    },
    {
        "q": "Güneş sistemindeki en büyük gezegen hangisidir?",
        "options": ["Mars", "Satürn", "Jüpiter", "Venüs"],
        "answer": 2,
    },
    {
        "q": "İstiklal Marşı'mızın şairi kimdir?",
        "options": [
            "Mehmet Akif Ersoy",
            "Yahya Kemal",
            "Namık Kemal",
            "Cahit Sıtkı",
        ],
        "answer": 0,
    },
    {
        "q": "Dünyanın en uzun nehri hangisidir?",
        "options": ["Amazon", "Nil", "Mississippi", "Tuna"],
        "answer": 1,
    },
    {
        "q": "Pusulada 'N' harfi hangi yönü gösterir?",
        "options": ["Güney", "Doğu", "Kuzey", "Batı"],
        "answer": 2,
    },
    {
        "q": "Periyodik tabloda 'Au' simgesi hangi elementi temsil eder?",
        "options": ["Gümüş", "Bakır", "Altın", "Demir"],
        "answer": 2,
    },
    {
        "q": "Mona Lisa tablosu hangi ünlü ressama aittir?",
        "options": ["Picasso", "Leonardo da Vinci", "Van Gogh", "Salvador Dali"],
        "answer": 1,
    },
    {
        "q": "Futbolda bir takım sahada kaç kişiyle mücadele eder?",
        "options": ["10", "11", "12", "9"],
        "answer": 1,
    },
    {
        "q": "Cumhuriyet kaç yılında ilan edilmiştir?",
        "options": ["1919", "1920", "1922", "1923"],
        "answer": 3,
    },
    {
        "q": "Kendi ekseni etrafında dönüşünü yaklaşık 24 saatte tamamlayan gök cismi hangisidir?",
        "options": ["Ay", "Dünya", "Mars", "Güneş"],
        "answer": 1,
    },
]

QUESTIONS_JSON = json.dumps(QUESTIONS, ensure_ascii=False)

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Genel Kültür Bilgi Yarışması</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
  body {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    color: #1f2937;
  }}
  .card {{
    background: #ffffff;
    border-radius: 20px;
    padding: 35px 30px;
    width: 100%;
    max-width: 550px;
    box-shadow: 0 20px 35px rgba(0,0,0,0.2);
    text-align: center;
    transition: all 0.3s ease;
  }}
  h1 {{ color: #4338ca; font-size: 26px; margin-bottom: 12px; }}
  p.desc {{ color: #6b7280; font-size: 15px; margin-bottom: 24px; line-height: 1.5; }}
  .input-group {{ margin-bottom: 20px; text-align: left; }}
  .input-group label {{ display: block; font-weight: 600; margin-bottom: 8px; color: #374151; font-size: 14px; }}
  input[type="text"] {{
    width: 100%;
    padding: 13px 16px;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    font-size: 16px;
    outline: none;
    transition: border-color 0.2s;
  }}
  input[type="text"]:focus {{ border-color: #6366f1; }}
  .btn {{
    background: #4f46e5;
    color: white;
    border: none;
    padding: 13px 28px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    width: 100%;
  }}
  .btn:hover {{ background: #4338ca; transform: translateY(-2px); box-shadow: 0 8px 15px rgba(79, 70, 229, 0.3); }}
  .btn:active {{ transform: translateY(0); }}
  .btn-next {{ background: #10b981; margin-top: 18px; display: none; }}
  .btn-next:hover {{ background: #059669; }}
  .alert {{ color: #ef4444; font-size: 14px; font-weight: 600; margin-bottom: 15px; display: none; }}
  
  /* Quiz Bölümü */
  .meta-bar {{
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    font-weight: bold;
    color: #6b7280;
    margin-bottom: 12px;
  }}
  .progress-bg {{
    width: 100%;
    background-color: #e5e7eb;
    border-radius: 8px;
    height: 8px;
    margin-bottom: 22px;
    overflow: hidden;
  }}
  .progress-fill {{
    background: #6366f1;
    height: 100%;
    width: 0%;
    border-radius: 8px;
    transition: width 0.3s;
  }}
  .question-text {{
    font-size: 19px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 22px;
    text-align: left;
    min-height: 55px;
    line-height: 1.4;
  }}
  .options-grid {{ display: flex; flex-direction: column; gap: 12px; }}
  .opt-btn {{
    background: #f9fafb;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 13px 18px;
    text-align: left;
    font-size: 15px;
    cursor: pointer;
    font-weight: 600;
    color: #374151;
    transition: all 0.2s;
  }}
  .opt-btn:hover:not(:disabled) {{
    background: #eef2ff;
    border-color: #a5b4fc;
    color: #4338ca;
  }}
  .opt-btn.correct {{ background: #d1fae5 !important; border-color: #10b981 !important; color: #065f46 !important; }}
  .opt-btn.wrong {{ background: #fee2e2 !important; border-color: #ef4444 !important; color: #991b1b !important; }}
  .feedback {{
    margin-top: 16px;
    font-size: 15px;
    font-weight: bold;
    padding: 10px;
    border-radius: 8px;
    display: none;
  }}
  .feedback.show {{ display: block; }}
  .feedback.success {{ color: #047857; background: #ecfdf5; }}
  .feedback.error {{ color: #b91c1c; background: #fef2f2; }}

  /* Sonuç Bölümü */
  .res-box {{
    background: #f3f4f6;
    border-radius: 14px;
    padding: 20px;
    margin: 20px 0;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    text-align: center;
  }}
  .res-item div:first-child {{ font-size: 13px; color: #6b7280; margin-bottom: 4px; font-weight: 600; }}
  .res-item div:last-child {{ font-size: 22px; font-weight: bold; color: #111827; }}
  .res-msg {{ font-size: 16px; font-weight: 600; color: #4338ca; margin-bottom: 22px; line-height: 1.5; }}
</style>
</head>
<body>

<div class="card">
  <!-- 1. GİRİŞ EKRANI -->
  <div id="start-screen">
    <h1>🏆 GENEL KÜLTÜR YARIŞMASI</h1>
    <p class="desc">Bilgine güveniyor musun? Hemen adını yaz, soruları yanıtla ve en yüksek skoru elde et!</p>
    <div class="input-group">
      <label for="username">Adınız:</label>
      <input type="text" id="username" placeholder="Örn: Ahmet Yılmaz" maxlength="25" autofocus>
    </div>
    <div id="name-alert" class="alert">⚠️ Lütfen yarışmaya başlamak için adınızı girin!</div>
    <button class="btn" onclick="startQuiz()">Yarışmaya Başla 🚀</button>
  </div>

  <!-- 2. SORU EKRANI -->
  <div id="quiz-screen" style="display: none;">
    <div class="meta-bar">
      <span id="progress-text">Soru 1 / 10</span>
      <span id="score-text">Puan: 0</span>
    </div>
    <div class="progress-bg">
      <div id="progress-bar" class="progress-fill"></div>
    </div>
    <div class="question-text" id="question-text">Soru metni</div>
    <div class="options-grid" id="options-container"></div>
    <div id="feedback" class="feedback"></div>
    <button id="next-btn" class="btn btn-next" onclick="nextQuestion()">Sonraki Soru ➔</button>
  </div>

  <!-- 3. SONUÇ EKRANI -->
  <div id="result-screen" style="display: none;">
    <h1>🎉 Tebrikler!</h1>
    <p class="desc"><b id="res-name">Kullanıcı</b>, yarışmayı başarıyla tamamladın.</p>
    <div class="res-box">
      <div class="res-item"><div>Toplam Puan</div><div id="res-score">0</div></div>
      <div class="res-item"><div>Başarı Oranı</div><div id="res-pct">%0</div></div>
      <div class="res-item"><div>Doğru Sayısı</div><div id="res-correct" style="color:#059669;">0</div></div>
      <div class="res-item"><div>Yanlış Sayısı</div><div id="res-wrong" style="color:#dc2626;">0</div></div>
    </div>
    <div id="res-message" class="res-msg">Sonuç değerlendirmesi</div>
    <button class="btn" onclick="restartQuiz()">Tekrar Oyna 🔄</button>
  </div>
</div>

<script>
  const questions = {QUESTIONS_JSON};
  let currentIdx = 0;
  let score = 0;
  let correctCount = 0;
  let wrongCount = 0;
  let userName = "";

  function startQuiz() {{
    const input = document.getElementById("username");
    userName = input.value.trim();
    if (!userName) {{
      document.getElementById("name-alert").style.display = "block";
      return;
    }}
    document.getElementById("name-alert").style.display = "none";
    document.getElementById("start-screen").style.display = "none";
    document.getElementById("quiz-screen").style.display = "block";
    loadQuestion();
  }}

  function loadQuestion() {{
    const q = questions[currentIdx];
    document.getElementById("progress-text").innerText = `Soru ${{currentIdx + 1}} / ${{questions.length}}`;
    document.getElementById("score-text").innerText = `Puan: ${{score}}`;
    const pct = ((currentIdx) / questions.length) * 100;
    document.getElementById("progress-bar").style.width = pct + "%";

    document.getElementById("question-text").innerText = `${{currentIdx + 1}}. ${{q.q}}`;
    const container = document.getElementById("options-container");
    container.innerHTML = "";
    const feedback = document.getElementById("feedback");
    feedback.className = "feedback";
    feedback.innerText = "";
    document.getElementById("next-btn").style.display = "none";

    q.options.forEach((opt, idx) => {{
      const btn = document.createElement("button");
      btn.className = "opt-btn";
      btn.innerText = `${{String.fromCharCode(65 + idx)}}) ${{opt}}`;
      btn.onclick = () => selectOption(idx);
      container.appendChild(btn);
    }});
  }}

  function selectOption(selectedIdx) {{
    const q = questions[currentIdx];
    const buttons = document.querySelectorAll(".opt-btn");
    buttons.forEach(b => b.disabled = true);
    const feedback = document.getElementById("feedback");

    if (selectedIdx === q.answer) {{
      buttons[selectedIdx].classList.add("correct");
      feedback.className = "feedback success show";
      feedback.innerText = "Doğru! 🎉 Harika gidiyorsun.";
      score += 10;
      correctCount++;
    }} else {{
      buttons[selectedIdx].classList.add("wrong");
      buttons[q.answer].classList.add("correct");
      feedback.className = "feedback error show";
      feedback.innerText = `Yanlış! ❌ Doğru cevap: ${{q.options[q.answer]}}`;
      wrongCount++;
    }}

    document.getElementById("score-text").innerText = `Puan: ${{score}}`;
    document.getElementById("next-btn").style.display = "block";
  }}

  function nextQuestion() {{
    currentIdx++;
    if (currentIdx < questions.length) {{
      loadQuestion();
    }} else {{
      showResult();
    }}
  }}

  function showResult() {{
    document.getElementById("progress-bar").style.width = "100%";
    document.getElementById("quiz-screen").style.display = "none";
    document.getElementById("result-screen").style.display = "block";

    document.getElementById("res-name").innerText = userName;
    document.getElementById("res-score").innerText = score;
    document.getElementById("res-correct").innerText = correctCount;
    document.getElementById("res-wrong").innerText = wrongCount;

    const pct = Math.round((correctCount / questions.length) * 100);
    document.getElementById("res-pct").innerText = `%${{pct}}`;

    let msg = "";
    if (pct >= 80) msg = "🌟 Harika bir başarı! Genel kültürün gerçekten mükemmel.";
    else if (pct >= 50) msg = "👏 Gayet başarılı! Genel kültürün oldukça iyi durumda.";
    else msg = "📚 İyi bir deneme! Biraz daha genel kültür pratiğiyle zirveye ulaşabilirsin.";
    document.getElementById("res-message").innerText = msg;
  }}

  function restartQuiz() {{
    currentIdx = 0;
    score = 0;
    correctCount = 0;
    wrongCount = 0;
    document.getElementById("result-screen").style.display = "none";
    document.getElementById("start-screen").style.display = "block";
  }}
</script>
</body>
</html>
"""


class QuizRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode("utf-8"))

    def log_message(self, format, *args):
        # Konsol çıktısını temiz tutmak için istekleri sessize al
        return


def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), QuizRequestHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    print(f"Sunucu başlatılıyor: http://127.0.0.1:{PORT}")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    time.sleep(0.5)
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    print("Tarayıcı açıldı. Çıkış yapmak için CTRL+C tuşlarına basabilirsiniz.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nUygulama sonlandırıldı.")
