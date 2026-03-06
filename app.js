let validCountries = [];
let currentIndex = 0;

// The data is loaded via data.js which defines `countriesData`.

document.addEventListener('DOMContentLoaded', async () => {
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

            let area = c.area;
            if (area === undefined || area === null) {
                area = -1;
            }

            let flag_url = c.flags?.png || '';
            if (flag_url) {
                flag_url = flag_url.replace('/w320/', '/w1280/');
            }

            const capital_en = c.capital_en || 'N/A';
            const capital_zh = c.capital_zh || '無';
            let pop = c.population;
            if (pop === undefined || pop === null) {
                pop = -1;
            }

            validCountries.push({
                en: name_en,
                zh: name_zh,
                area: area,
                population: pop,
                flag_url: flag_url,
                capital_en: capital_en,
                capital_zh: capital_zh
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

    const actionContainer = document.createElement('div');
    actionContainer.style.display = 'inline-flex';
    actionContainer.style.flexDirection = 'column';
    actionContainer.style.gap = '5px';
    actionContainer.style.marginLeft = '15px';
    actionContainer.style.verticalAlign = 'bottom';

    const exportBtn = document.createElement('button');
    exportBtn.id = 'exportBtn';
    exportBtn.className = 'range-btn export-btn';
    exportBtn.textContent = '匯出 PDF';
    exportBtn.style.margin = '0';
    exportBtn.style.width = '120px';

    // Add event listener immediately
    exportBtn.addEventListener('click', () => {
        alert("網頁版暫不支援直接匯出 PDF，如果需要列印，建議使用原本的 Python 系統，或直接列印本網頁。");
    });

    const searchBtn = document.createElement('button');
    searchBtn.className = 'range-btn';
    searchBtn.textContent = `🔍 搜尋`;
    searchBtn.style.backgroundColor = "darkblue";
    searchBtn.style.margin = '0';
    searchBtn.style.width = '120px';
    searchBtn.onclick = showSearchWindow;

    actionContainer.appendChild(exportBtn);
    actionContainer.appendChild(searchBtn);
    rangeFrame.appendChild(actionContainer);

    showCountry();
}

function showCountry() {
    if (validCountries.length === 0) return;
    const cData = validCountries[currentIndex];

    const areaText = cData.area >= 0 ? new Intl.NumberFormat().format(cData.area) + " km²" : "無資料";
    document.getElementById('areaLabel').textContent = `領土面積 : ${areaText}`;

    const popText = cData.population >= 0 ? new Intl.NumberFormat().format(cData.population) : "無資料";
    const popLabel = document.getElementById('populationLabel');
    if (popLabel) {
        popLabel.textContent = `國家人口 : ${popText}`;
    }

    const titleText = `No. ${cData.rank} - ${cData.zh} (${cData.en})`;
    const infoTitle = document.getElementById('infoTitle');
    infoTitle.textContent = titleText;
    infoTitle.style.fontSize = titleText.length < 45 ? '28px' : titleText.length < 65 ? '20px' : '16px';

    const capitalText = cData.capital_en !== 'N/A' ? `首都: ${cData.capital_zh} (${cData.capital_en})` : '首都: 無資料';
    const capTitle = document.getElementById('capitalTitle');
    capTitle.textContent = capitalText;
    capTitle.style.fontSize = capitalText.length < 45 ? '1.6rem' : capitalText.length < 65 ? '1.2rem' : '1.0rem';

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

function showSearchWindow() {
    const modal = document.getElementById('searchModal');
    const list = document.getElementById('searchList');
    const input = document.getElementById('searchInput');

    input.value = '';

    function updateList() {
        const query = input.value.trim().toLowerCase();
        list.innerHTML = '';

        validCountries.forEach((c, idx) => {
            if (c.zh.toLowerCase().includes(query) || c.en.toLowerCase().includes(query)) {
                const btn = document.createElement('button');
                btn.className = 'list-item-btn';
                btn.textContent = `No.${c.rank} - ${c.zh} (${c.en})`;
                btn.onclick = () => {
                    currentIndex = idx;
                    showCountry();
                    modal.style.display = 'none';
                };
                list.appendChild(btn);
            }
        });
    }

    input.onkeyup = updateList;
    updateList(); // Run once initially to populate

    modal.style.display = 'block';
    setTimeout(() => input.focus(), 100);
}

function setupEventListeners() {
    document.getElementById('prevBtn')?.addEventListener('click', prevCountry);
    document.getElementById('nextBtn')?.addEventListener('click', nextCountry);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            prevCountry();
        } else if (e.key === 'ArrowRight') {
            nextCountry();
        }
    });

    // Modal close logic
    const rangeModal = document.getElementById('rangeModal');
    const searchModal = document.getElementById('searchModal');

    document.getElementById('closeModal').onclick = () => {
        rangeModal.style.display = 'none';
    };

    document.getElementById('closeSearchModal').onclick = () => {
        searchModal.style.display = 'none';
    };

    window.onclick = (e) => {
        if (e.target === rangeModal) {
            rangeModal.style.display = 'none';
        }
        if (e.target === searchModal) {
            searchModal.style.display = 'none';
        }
    };
}
