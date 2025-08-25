// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // --- [수정] 더 이상 사용하지 않는 DOM 요소 선택 코드를 삭제합니다. ---
    // const sidebar = document.querySelector('.sidebar');
    // const mainContent = document.querySelector('.main-content');
    // const hamburgerIcon = document.querySelector('.hamburger-icon');

    // 2. 헬퍼 함수 및 DatePicker 초기화
    function formatDate(date) {
        if (!date) return '';
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // 대시보드 페이지의 DatePicker 생성 함수
    window.initDatePicker = (elementId, updateChartCallback) => {
        const datePickerEl = document.getElementById(elementId);
        if (!datePickerEl) return null;

        const today = new Date();
        const weekAgo = new Date();
        weekAgo.setDate(today.getDate() - 6);
        let stagedRange = [weekAgo, today];

        const instance = flatpickr(datePickerEl, {
            mode: "range",
            dateFormat: "Y-m-d",
            defaultDate: stagedRange,
            locale: "ko",
            closeOnSelect: false,
            onChange: (selectedDates) => {
                if (selectedDates.length === 2) stagedRange = selectedDates;
            },
            onReady: (_, __, fp) => {
                const container = document.createElement('div');
                container.className = 'custom-buttons-container';
                const periodButtons = document.createElement('div');
                periodButtons.className = 'period-buttons';
                ['오늘', '1주일', '1개월'].forEach(text => {
                    const button = document.createElement('button');
                    button.innerText = text;
                    button.addEventListener('click', () => {
                        const today_btn = new Date();
                        let startDate_btn = new Date();
                        if (text === '오늘') startDate_btn.setDate(today_btn.getDate());
                        else if (text === '1주일') startDate_btn.setDate(today_btn.getDate() - 6);
                        else if (text === '1개월') startDate_btn.setMonth(today_btn.getMonth() - 1);
                        fp.setDate([startDate_btn, today_btn], true);
                    });
                    periodButtons.appendChild(button);
                });
                const actionButtons = document.createElement('div');
                actionButtons.className = 'action-buttons';
                const applyBtn = document.createElement('button');
                applyBtn.className = 'apply-btn';
                applyBtn.innerText = '적용';
                applyBtn.addEventListener('click', () => {
                    const [start, end] = stagedRange;
                    if (!start || !end) return alert('조회 기간을 선택해주세요.');
                    updateChartCallback(formatDate(start), formatDate(end));
                    fp.close();
                });
                actionButtons.appendChild(applyBtn);
                container.appendChild(periodButtons);
                container.appendChild(actionButtons);
                fp.calendarContainer.appendChild(container);
            },
        });
        
        const [start, end] = instance.selectedDates;
        if (start && end) {
            updateChartCallback(formatDate(start), formatDate(end));
        }
        return instance;
    };


    // 3. 이벤트 핸들러 및 초기화
    const initialize = () => {
        // --- [수정] 햄버거 메뉴 토글 관련 코드를 전부 삭제합니다. ---
        
        // --- [수정] 사이드바 메뉴 관련 코드를 전부 삭제합니다. ---
    };

    initialize();
});