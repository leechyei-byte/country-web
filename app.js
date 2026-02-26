let validCountries = [];
let currentIndex = 0;
let converter = null;

// The data is loaded via data.js which defines `countriesData`.

document.addEventListener('DOMContentLoaded', async () => {
    try {
        if (window.OpenCC) {
            converter = window.OpenCC.Converter({ from: 'cn', to: 'tw' });
        }
    } catch (e) {
        console.warn('OpenCC initialization failed', e);
    }

    await loadData();
    setupUI();
    setupEventListeners();
});

async function loadData() {
    try {
        let data;

        // Use data.js fallback if fetch is not allowed.
        if (typeof countriesData !== "undefined") {
            data = countriesData;
        } else {
            const response = await fetch('countries.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            data = await response.json();
        }

        for (let c of data) {
            const name_en = c.name?.common || 'Unknown';
            let name_zh = c.translations?.zho?.common || name_en;

            if (converter && name_zh !== name_en) {
                try {
                    name_zh = converter(name_zh);
                } catch (e) { }
            }

            let area = c.area;
            if (area === undefined || area === null) {
                area = -1;
            }

            let flag_url = c.flags?.png || '';
            if (flag_url) {
                flag_url = flag_url.replace('/w320/', '/w1280/');
            }

            validCountries.push({
                en: name_en,
                zh: name_zh,
                area: area,
                flag_url: flag_url
            });
        }

        validCountries.sort((a, b) => b.area - a.area);
        for (let i = 0; i < validCountries.length; i++) {
            validCountries[i].rank = i + 1;
        }

        document.getElementById('loadingMessage').style.display = 'none';

    } catch (e) {
        document.getElementById('loadingMessage').innerHTML = `載入失敗 (Failed to fetch data)<br><br>請確保 data.js 檔案存在，或使用網頁伺服器開啟。<br>詳細錯誤：${e.message}`;
        console.error(e);
    }
}

function setupUI() {
    if (validCountries.length === 0) return;

    // Create range buttons
    const rangeFrame = document.getElementById('rangeFrame');
    const totalCountries = validCountries.length;

    for (let i = 0; i < totalCountries; i += 50) {
        const start = i;
        const end = Math.min(i + 49, totalCountries - 1);

        const btn = document.createElement('button');
        btn.className = 'range-btn';
        btn.textContent = `排名 ${start + 1}-${end + 1}`;
        btn.onclick = () => showRangeWindow(start, end);
        rangeFrame.appendChild(btn);
    }

    showCountry();
}

function showCountry() {
    if (validCountries.length === 0) return;
    const cData = validCountries[currentIndex];

    const areaText = cData.area >= 0 ? new Intl.NumberFormat().format(cData.area) + " km²" : "無資料";
    document.getElementById('areaLabel').textContent = `領土面積 : ${areaText}`;

    const titleText = `No. ${cData.rank} - ${cData.zh} (${cData.en})`;
    document.getElementById('infoTitle').textContent = titleText;

    const flagImg = document.getElementById('flagImg');
    const flagText = document.getElementById('flagText');

    flagImg.style.display = 'none';
    flagText.style.display = 'block';

    if (!cData.flag_url) {
        flagText.textContent = "無國旗圖片 (No Flag Available)";
        return;
    }

    flagText.textContent = "載入國旗中... (Loading Flag...)";

    flagImg.onload = () => {
        flagText.style.display = 'none';
        flagImg.style.display = 'block';
    };

    flagImg.onerror = () => {
        flagImg.style.display = 'none';
        flagText.style.display = 'block';
        flagText.textContent = "國旗載入失敗 (Failed to load flag)";
    };

    flagImg.src = cData.flag_url;
}

function prevCountry() {
    if (validCountries.length === 0) return;
    currentIndex = (currentIndex - 1 + validCountries.length) % validCountries.length;
    showCountry();
}

function nextCountry() {
    if (validCountries.length === 0) return;
    currentIndex = (currentIndex + 1) % validCountries.length;
    showCountry();
}

function showRangeWindow(startIdx, endIdx) {
    const modal = document.getElementById('rangeModal');
    const title = document.getElementById('modalTitle');
    const list = document.getElementById('modalList');

    title.textContent = `國家列表 (排名 ${startIdx + 1} - ${endIdx + 1})`;
    list.innerHTML = '';

    for (let i = startIdx; i <= endIdx; i++) {
        if (i < validCountries.length) {
            const c = validCountries[i];
            const btn = document.createElement('button');
            btn.className = 'list-item-btn';
            btn.textContent = `No.${c.rank} - ${c.zh} (${c.en})`;
            btn.onclick = () => {
                currentIndex = i;
                showCountry();
                modal.style.display = 'none';
            };
            list.appendChild(btn);
        }
    }

    modal.style.display = 'block';
}

function setupEventListeners() {
    document.getElementById('prevBtn')?.addEventListener('click', prevCountry);
    document.getElementById('nextBtn')?.addEventListener('click', nextCountry);

    document.getElementById('exportBtn')?.addEventListener('click', () => {
        alert("網頁版暫不支援直接匯出 PDF，如果需要列印，建議使用原本的 Python 系統，或直接列印本網頁。");
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            prevCountry();
        } else if (e.key === 'ArrowRight') {
            nextCountry();
        }
    });

    // Modal close logic
    const rangeModal = document.getElementById('rangeModal');
    const flagModal = document.getElementById('flagModal');

    document.getElementById('closeModal').onclick = () => {
        rangeModal.style.display = 'none';
    };

    document.getElementById('closeFlagModal').onclick = () => {
        flagModal.style.display = 'none';
    };

    window.onclick = (e) => {
        if (e.target === rangeModal) {
            rangeModal.style.display = 'none';
        }
        if (e.target === flagModal) {
            flagModal.style.display = 'none';
        }
    };

    // Enlarged Flag
    document.getElementById('flagImg').onclick = () => {
        if (validCountries.length === 0) return;
        const cData = validCountries[currentIndex];
        if (!cData.flag_url) return;

        document.getElementById('flagModalTitle').textContent = `放大國旗 - ${cData.zh}`;
        document.getElementById('enlargedFlagImg').src = cData.flag_url;
        flagModal.style.display = 'block';
    };
}
