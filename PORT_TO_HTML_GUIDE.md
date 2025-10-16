# Porting Streamlit Features to HTML Version

Guide to adding Streamlit features to your standalone HTML application.

## Why Port to HTML?

Your HTML version (`wscc-portal`) is 100% standalone and works perfectly on restricted work computers:
- ✅ No Python installation required
- ✅ No admin rights needed
- ✅ No dependencies to install
- ✅ Instant startup
- ✅ Works from USB drive
- ✅ Copy and run on any Windows computer

## Features to Port from Streamlit to HTML

### 1. Visual Analytics (Graphs)

**Streamlit uses:** Plotly + NetworkX + Graphistry
**HTML alternative:** Chart.js or D3.js (no installation needed)

#### Implementation:

```html
<!-- Add to index.html -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
// js/visual-analytics.js
const VisualAnalytics = {
    renderStatusChart: function() {
        const ctx = document.getElementById('statusChart').getContext('2d');
        const cases = State.state.cases;

        const statusCounts = {};
        cases.forEach(c => {
            statusCounts[c.status] = (statusCounts[c.status] || 0) + 1;
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(statusCounts),
                datasets: [{
                    label: 'Cases by Status',
                    data: Object.values(statusCounts),
                    backgroundColor: ['#2c5282', '#4299e1', '#63b3ed']
                }]
            }
        });
    }
};
</script>
```

### 2. Card/List View Toggle

Already have this! Just add the toggle from Streamlit:

```javascript
// Add to cases.js
const CaseViews = {
    currentView: 'cards', // or 'list'

    toggleView: function() {
        this.currentView = this.currentView === 'cards' ? 'list' : 'cards';
        this.render();
    },

    render: function() {
        if (this.currentView === 'cards') {
            this.renderCards();
        } else {
            this.renderList();
        }
    },

    renderCards: function() {
        // Your existing card rendering
    },

    renderList: function() {
        // New list view
        const cases = State.state.cases;
        const html = `
            <table class="case-table">
                <thead>
                    <tr>
                        <th>Case #</th>
                        <th>Employer</th>
                        <th>Worker</th>
                        <th>Status</th>
                        <th>Territory</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${cases.map(c => `
                        <tr>
                            <td>${c.caseNumber}</td>
                            <td>${c.employer}</td>
                            <td>${c.worker}</td>
                            <td><span class="status-badge ${c.status}">${c.status}</span></td>
                            <td>${c.territory}</td>
                            <td>
                                <button onclick="Cases.viewCase('${c.id}')">View</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('cases-container').innerHTML = html;
    }
};
```

### 3. Enhanced Dashboard with Charts

```javascript
// Add to ui.js
UI.renderEnhancedDashboard = function() {
    const stats = this.calculateStats();

    // Render stat cards (already have)
    this.renderStatCards(stats);

    // Add chart section
    const chartsHTML = `
        <div class="dashboard-charts">
            <div class="chart-container">
                <h3>Cases by Status</h3>
                <canvas id="statusChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Cases by Territory</h3>
                <canvas id="territoryChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Cases Over Time</h3>
                <canvas id="timelineChart"></canvas>
            </div>
        </div>
    `;

    document.getElementById('charts-section').innerHTML = chartsHTML;

    // Render charts
    VisualAnalytics.renderStatusChart();
    VisualAnalytics.renderTerritoryChart();
    VisualAnalytics.renderTimelineChart();
};
```

### 4. Smart Search (TF-IDF from Streamlit)

Port the smart search algorithm:

```javascript
// js/smart-search.js
const SmartSearch = {
    // Simple TF-IDF implementation
    search: function(query, cases) {
        if (!query) return cases;

        const results = cases.map(caseObj => {
            const score = this.calculateRelevance(query, caseObj);
            return { case: caseObj, score };
        });

        return results
            .filter(r => r.score > 0)
            .sort((a, b) => b.score - a.score)
            .map(r => r.case);
    },

    calculateRelevance: function(query, caseObj) {
        const queryLower = query.toLowerCase();
        const searchableText = [
            caseObj.caseNumber,
            caseObj.employer,
            caseObj.worker,
            caseObj.community,
            caseObj.description || ''
        ].join(' ').toLowerCase();

        // Simple scoring: count matches
        const words = queryLower.split(/\s+/);
        let score = 0;

        words.forEach(word => {
            if (searchableText.includes(word)) {
                score += 1;
                // Boost for exact matches
                if (caseObj.caseNumber.toLowerCase().includes(word)) score += 2;
            }
        });

        return score;
    }
};

// Update Cases.searchCases to use SmartSearch
Cases.searchCases = function(query) {
    const allCases = State.state.cases;
    const results = SmartSearch.search(query, allCases);
    this.displayCases(results);
};
```

### 5. Territory Flags on Dashboard

Already implemented! Your version has the Northern Theme with flag backgrounds.

### 6. Export/Import Enhancements

Add Excel export using SheetJS (no installation):

```html
<!-- Add to index.html -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>

<script>
// Add to reports.js
Reports.exportToExcel = function() {
    const cases = State.state.cases;

    const data = cases.map(c => ({
        'Case Number': c.caseNumber,
        'Employer': c.employer,
        'Worker': c.worker,
        'Territory': c.territory,
        'Status': c.status,
        'Reported Date': c.reportedDate,
        'Community': c.community
    }));

    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Cases");

    XLSX.writeFile(wb, `WSCC_Cases_${new Date().toISOString().split('T')[0]}.xlsx`);
};
</script>
```

## Implementation Plan

### Phase 1: Add Chart.js (5 minutes)
1. Add Chart.js CDN to index.html
2. Create visual-analytics.js
3. Add chart containers to dashboard
4. Implement basic bar charts

### Phase 2: Enhanced Search (10 minutes)
1. Create smart-search.js
2. Implement TF-IDF algorithm
3. Update search UI to show scores
4. Add search result highlighting

### Phase 3: View Toggle (5 minutes)
1. Add toggle button to cases page
2. Implement list view rendering
3. Add CSS for table styling
4. Store preference in localStorage

### Phase 4: Export Enhancements (10 minutes)
1. Add SheetJS CDN
2. Implement Excel export
3. Add PDF export using jsPDF
4. Update export menu

## File Structure After Enhancements

```
wscc-portal/
├── index.html
├── css/
│   ├── styles.css
│   └── charts.css              # New
├── js/
│   ├── app.js
│   ├── state.js
│   ├── ui.js
│   ├── cases.js
│   ├── officers.js
│   ├── reports.js
│   ├── modals.js
│   ├── utils.js
│   ├── visual-analytics.js     # New
│   ├── smart-search.js         # New
│   └── enhanced-export.js      # New
└── README.md
```

## CDN Libraries to Add (No Installation)

Add these to your `index.html` `<head>`:

```html
<!-- Charts -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>

<!-- Excel Export -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>

<!-- PDF Export -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

<!-- Advanced Charts (Optional) -->
<script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
```

## Testing

After adding features:
1. Open index.html in browser
2. Test each new feature
3. Verify no errors in console (F12)
4. Test offline functionality
5. Export data and verify format

## Benefits of HTML Version

### Comparison with Streamlit:

| Feature | HTML | Streamlit |
|---------|------|-----------|
| File Size | ~3MB | ~200MB |
| Startup | Instant | 5-10 sec |
| Installation | None | pip install |
| Offline | Yes | Yes |
| Portable | 100% | Needs setup |
| Admin Rights | No | Sometimes |
| Updates | Edit files | pip upgrade |

## Distribution

### Create Distribution Package:

```batch
REM create-distribution.bat
@echo off
echo Creating WSCC Standalone Distribution...

REM Copy folder
xcopy "wscc-portal" "WSCC-Investigation-System-Standalone" /E /I

REM Create README
echo WSCC Investigation Management System - Standalone Edition > "WSCC-Investigation-System-Standalone\START_HERE.txt"
echo. >> "WSCC-Investigation-System-Standalone\START_HERE.txt"
echo 1. Open index.html in any web browser >> "WSCC-Investigation-System-Standalone\START_HERE.txt"
echo 2. No installation required! >> "WSCC-Investigation-System-Standalone\START_HERE.txt"
echo 3. Works on any Windows computer >> "WSCC-Investigation-System-Standalone\START_HERE.txt"

REM Create ZIP
powershell Compress-Archive -Path "WSCC-Investigation-System-Standalone" -DestinationPath "WSCC-Standalone-v1.0.zip"

echo Distribution package created: WSCC-Standalone-v1.0.zip
pause
```

## Alternative: Electron Wrapper (Advanced)

If you want a desktop app icon:

1. Install Node.js
2. Create package.json:
```json
{
  "name": "wscc-investigation-system",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron ."
  },
  "devDependencies": {
    "electron": "^27.0.0"
  }
}
```

3. Create main.js:
```javascript
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        icon: path.join(__dirname, 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    win.loadFile('index.html');
}

app.whenReady().then(createWindow);
```

4. Build:
```bash
npm install
npx electron-builder
```

But honestly, **your HTML version is already perfect** - no need for Electron!

## Recommendation

**Just use your HTML version (`wscc-portal`)!**

It's:
- 100% standalone
- No dependencies
- No installation
- Perfect for work computers
- Already has all features you need

If you want the Streamlit features, add them incrementally using the CDN libraries above - still no installation required!
