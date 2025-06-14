// 설정: 더보기 버튼 클릭 횟수
const MORE_CLICK_COUNT = 1;

// 팝업 메인 UI 렌더링 함수
function renderMainUI() {
  const mainContent = document.getElementById('mainContent');
  mainContent.innerHTML = `
    <img src="images/logo.png" alt="서비스 로고" class="logo">
    <h1>정제된 피드백 추출 서비스, CleansedFeedback</h1>
    <p>정제된 댓글을 확인하고 싶은<br>웹툰 페이지에서 아래 버튼을 눌러주세요!</p>
    <button id="modifyBtn">댓글 정제</button>
  `;

  document.getElementById('modifyBtn').addEventListener('click', handleClick);
}

// 댓글 정제 버튼 클릭 핸들러
async function handleClick() {
  const mainContent = document.getElementById('mainContent');
  mainContent.innerHTML = `
    <div style="display: flex; flex-direction: column; align-items: center; height: 100%; box-sizing: border-box;">
      <img src="images/logo.png" alt="서비스 로고" class="logo">
      <div style="width: 50px; height: 50px; border: 6px solid #f3f3f3; border-top: 6px solid #4CAF50; border-radius: 50%; animation: spin 1s linear infinite; margin: 20px 0;"></div>
      <div style="font-size: 16px; color: #444;">댓글을 정제 중입니다...<br>잠시만 기다려주세요...</div>
    </div>
  `;

  // 스피너 애니메이션 추가
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(style);

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // 1. 더보기 버튼 N번 클릭
  for (let i = 0; i < MORE_CLICK_COUNT; i++) {
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const moreBtn = document.querySelector('span.u_cbox_page_more');
        if (moreBtn) moreBtn.click();
      }
    });
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // 2. 댓글 정제 요청
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: async (moreClickCount) => {
      const url = window.location.href;
      localStorage.setItem('cleansed_status', 'processing');

      const response = await fetch("http://localhost:5000/process_webtoon", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, more_click_count: moreClickCount })
      });

      const data = await response.json();
      const results = data.results;

      const nodes = document.querySelectorAll('span.u_cbox_contents');
      nodes.forEach((node, i) => {
        const r = results[i];
        if (!r) return;

        const m = r.final_hate;
        const f = r.final_feedback;
        const segment = r.cleansed || r.segment;
        const original = r.original;

        // 기존 텍스트 초기화
        node.textContent = "";

        // label 생성 (아이디 줄에 들어갈)
        const label = document.createElement("span");
        label.style.display = "inline-block";
        label.style.fontWeight = "bold";
        label.style.marginLeft = "8px";
        label.style.padding = "2px 6px";
        label.style.borderRadius = "4px";
        label.style.fontSize = "12px";
        label.style.verticalAlign = "middle";
        label.style.color = "#000";

        // 댓글 본문용 text div
        const text = document.createElement("div");
        text.style.display = "inline-block";
        text.style.padding = "2px 6px";
        text.style.borderRadius = "4px";
        text.style.color = "#000";

        // label + text 내용 설정
        if (m === "clean" && f === "feedback") {
          label.textContent = "순수 피드백 댓글";
          text.textContent = original;
          label.style.backgroundColor = "lightgreen";
          node.appendChild(text);  // ✅ 추가
        } else if (m === "clean" && f === "none") {
          label.textContent = "중립 댓글";
          text.textContent = original;
          label.style.backgroundColor = "lightblue";
          node.appendChild(text);  // ✅ 추가
        } else if (m !== "clean" && f === "feedback") {
          label.textContent = "비난 섞인 피드백 댓글";
          text.textContent = segment;
          label.style.backgroundColor = "lightyellow";

          // 원문 보기 기능 추가
          const originalDiv = document.createElement("div");
          originalDiv.textContent = original;
          originalDiv.style.display = "none";
          originalDiv.style.marginTop = "5px";
          originalDiv.style.padding = "2px 6px";
          originalDiv.style.borderRadius = "4px";
          //originalDiv.style.backgroundColor = "#eee";
          originalDiv.style.color = "#000";

          const showButton = document.createElement("button");
          showButton.textContent = "원문 보기";
          showButton.style.marginTop = "5px";
          showButton.style.padding = "2px 6px";
          showButton.style.border = "none";
          showButton.style.backgroundColor = "#eee";
          showButton.style.cursor = "pointer";
          showButton.style.borderRadius = "4px";
          showButton.style.fontSize = "12px";

          showButton.addEventListener("click", () => {
            if (originalDiv.style.display === "none") {
              originalDiv.style.display = "block";
              showButton.textContent = "원문 숨기기";
            } else {
              originalDiv.style.display = "none";
              showButton.textContent = "원문 보기";
            }
          });

          // text 다음에 버튼과 원문 div 추가
          node.appendChild(text);
          node.appendChild(showButton);
          node.appendChild(originalDiv);

        } else if (m !== "clean" && f === "none") {
          label.textContent = "순수 비난 댓글";
          text.textContent = "숨김";
          label.style.backgroundColor = "lightgray";
          node.appendChild(text);
        }

        // "아이디 영역"에 label 추가 (중복 방지 처리)
        const infoDiv = node.closest('.u_cbox_comment_box')?.querySelector('.u_cbox_info');
        if (infoDiv && !infoDiv.querySelector('.my_custom_label')) {
          label.classList.add('my_custom_label');
          infoDiv.appendChild(label);
        }
      });

      localStorage.setItem('cleansed_status', 'done');
    },
    args: [MORE_CLICK_COUNT]
  });

  // 3. 결과 상태 감시
  const interval = setInterval(() => {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => localStorage.getItem('cleansed_status')
    }, (results) => {
      if (results[0].result === 'done') {
        clearInterval(interval);

        mainContent.innerHTML = `
          <img src="images/logo.png" alt="서비스 로고" class="logo">
          <div style="font-size: 16px; color: #333; margin: 20px 0;">댓글 정제가 완료되었습니다.<br>결과를 확인하세요!</div>
          <button id="backBtn" style="
            width: 100%;
            padding: 10px 0;
            font-size: 14px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s ease-in-out;
          ">
            메인으로 돌아가기
          </button>
        `;

        document.getElementById('backBtn').addEventListener('click', () => {
          renderMainUI();
        });
      }
    });
  }, 500);
}

// 초기 로딩 시 메인 UI 표시
renderMainUI();
