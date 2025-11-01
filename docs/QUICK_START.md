# Qatar Open Data Portal Web Scraper - Quick Start Guide

## For UDC Polaris Multi-Agent System

---

## Prerequisites

1. **Python 3.8 or higher** installed on your system
2. **Internet connection** to access data.gov.qa
3. **At least 5GB free disk space** for downloaded data

---

## Installation (5 minutes)

### Step 1: Install Python Dependencies

```bash
# Navigate to the scraper directory
cd /path/to/scraper

# Install required packages
pip install -r requirements.txt

# Or install manually:
pip install requests pandas openpyxl
```

### Step 2: Verify Installation

```bash
python -c "import requests, pandas; print('✓ Dependencies installed successfully')"
```

---

## Usage

### Option 1: Quick Test Run (Recommended First Time)

```bash
python qatar_data_scraper.py
```

When prompted, select option **1** to download top 10 datasets (takes ~5-10 minutes)

### Option 2: Full Extraction

```bash
python qatar_data_scraper.py
```

When prompted, select option **3** to download all relevant datasets (may take 2-4 hours)

---

## What Happens During Execution?

### Phase 1: Discovery
- Connects to data.gov.qa API
- Retrieves list of all available datasets
- **Output:** Complete inventory of datasets on the portal

### Phase 2: Filtering  
- Applies keyword matching for UDC-relevant data
- Focuses on: real estate, population, economy, tourism, labor, energy, infrastructure
- **Output:** Filtered list of ~80-100 priority datasets

### Phase 3: Cataloging
- Creates detailed catalog with metadata
- Assigns priority scores
- **Output:** `qatar_data/metadata/qatar_data_catalog.csv`

### Phase 4: Download
- Downloads files from selected datasets
- Organizes by category (real_estate, population, etc.)
- **Output:** Data files in `qatar_data/raw/[category]/`

### Phase 5: Reporting
- Generates execution summary
- Logs successes and failures
- **Output:** `qatar_data/metadata/execution_report.txt`

---

## Output Directory Structure

```
qatar_data/
├── raw/                           # Downloaded raw data files
│   ├── real_estate/              # Real estate & property data
│   ├── population/               # Population & demographics
│   ├── economy/                  # Economic indicators
│   ├── tourism/                  # Tourism & hospitality
│   ├── labor/                    # Labor market data
│   ├── energy/                   # Energy & utilities
│   ├── infrastructure/           # Infrastructure & development
│   └── other/                    # Miscellaneous datasets
│
├── metadata/                      # Catalog and reports
│   ├── qatar_data_catalog.csv    # Complete dataset catalog
│   ├── catalog_summary.txt       # Summary statistics
│   ├── execution_report.txt      # Detailed execution report
│   ├── download_results.json     # Download details
│   └── failed_downloads.json     # Failed download log
│
├── processed/                     # (For future processing)
└── aggregated/                    # (For future aggregation)
```

---

## Key Output Files

### 1. qatar_data_catalog.csv
- **Purpose:** Comprehensive list of all relevant datasets
- **Use:** Review to select specific datasets for deeper analysis
- **Columns:** 
  - Dataset ID, Title, Organization
  - Last Updated, Resources Count
  - Priority Score, Keywords Matched
  - URL for manual access

### 2. execution_report.txt
- **Purpose:** Summary of extraction execution
- **Contains:**
  - Total datasets discovered and downloaded
  - Success/failure counts
  - Category breakdown
  - Total data volume
  - Next steps recommendations

### 3. qatar_scraper.log
- **Purpose:** Detailed technical log
- **Use:** Troubleshooting errors or network issues

---

## Common Issues & Solutions

### Issue: "No module named 'requests'"
**Solution:** 
```bash
pip install requests pandas openpyxl
```

### Issue: "Connection timeout"
**Solution:** 
- Check internet connection
- data.gov.qa may be temporarily down
- Try again later or use VPN if blocked

### Issue: "Failed to download certain datasets"
**Solution:** 
- Normal - some datasets may have broken links
- Check `failed_downloads.json` for list
- Report issues to PSA if needed: info@psa.gov.qa

### Issue: "Disk space full"
**Solution:** 
- Free up at least 5GB space
- Or download in batches (option 1 or 2)
- Delete unnecessary files from previous runs

---

## Advanced Usage

### Download Specific Categories Only

Edit `qatar_data_scraper.py` and modify the `filter_relevant_datasets()` method to include only your desired keywords.

### Schedule Automatic Updates

```python
# Create update_scheduler.py
import schedule
import time
from qatar_data_scraper import QatarOpenDataScraper

def daily_update():
    scraper = QatarOpenDataScraper()
    # Check for new/updated datasets
    all_datasets = scraper.get_all_datasets()
    relevant = scraper.filter_relevant_datasets(all_datasets)
    # Download only new or updated ones
    # (Add logic to compare with previous catalog)

schedule.every().day.at("02:00").do(daily_update)

while True:
    schedule.run_pending()
    time.sleep(3600)
```

### Export to Database

After downloading, process CSV files and load into your database:

```python
import pandas as pd
from sqlalchemy import create_engine

# Connect to your database
engine = create_engine('postgresql://user:pass@localhost/udc_data')

# Load a dataset
df = pd.read_csv('qatar_data/raw/real_estate/some_dataset/file.csv')

# Write to database
df.to_sql('real_estate_data', engine, if_exists='append', index=False)
```

---

## Integration with UDC Polaris

### Step 1: Review Downloaded Data
```bash
# Open the catalog
open qatar_data/metadata/qatar_data_catalog.csv

# Browse downloaded files
ls -R qatar_data/raw/
```

### Step 2: Identify High-Value Datasets
Look for datasets with:
- Recent updates (last_updated_days_ago < 30)
- High priority scores
- Relevant to specific Polaris agents

### Step 3: Process for Knowledge Graph
Transform data into graph-ready format:
```python
from qatar_data_scraper import QatarOpenDataScraper

scraper = QatarOpenDataScraper()
# Load your download results
with open('qatar_data/metadata/download_results.json') as f:
    results = json.load(f)

# Export for Neo4j
scraper.export_to_knowledge_graph_format(results)
```

### Step 4: Configure Polaris Agents
Point each agent to relevant data categories:
- **Market Intelligence Agent** → real_estate + economy + tourism
- **Risk Sentinel Agent** → economy + population + infrastructure  
- **Competitive Radar Agent** → real_estate + tourism
- **Predictive Analytics Agent** → all categories
- **Strategic Opportunity Agent** → real_estate + labor + economy

---

## Performance Expectations

| Metric | Value |
|--------|-------|
| Discovery (Phase 1-2) | 2-3 minutes |
| Catalog Creation (Phase 3) | < 1 minute |
| Top 10 datasets download | 5-10 minutes |
| Top 50 datasets download | 30-45 minutes |
| All datasets download | 2-4 hours |
| Average data size | 2-10 MB per dataset |
| Total estimated size | 500 MB - 2 GB |

---

## Best Practices

### 1. Start Small
- First run: Download top 10 datasets
- Review quality and relevance
- Then scale up to full extraction

### 2. Regular Updates
- Run weekly to catch new data releases
- PSA updates monthly statistics regularly
- Set up automated scheduling after initial extraction

### 3. Data Quality Checks
- Review `catalog_summary.txt` for data freshness
- Check `failed_downloads.json` for issues
- Validate critical datasets manually

### 4. Backup Strategy
- Keep raw downloads separate from processed data
- Archive monthly snapshots
- Document data lineage for compliance

### 5. Optimize Storage
- Compress old raw files after processing
- Delete duplicate or redundant datasets
- Keep only most recent versions unless historical analysis needed

---

## Support & Resources

### Qatar Open Data Portal
- **Website:** https://www.data.gov.qa/
- **Email:** info@psa.gov.qa
- **Documentation:** https://www.data.gov.qa/pages/handbook/

### Planning and Statistics Authority (PSA)
- **Main Site:** https://www.psa.gov.qa/
- **Statistics:** https://www.psa.gov.qa/en/statistics1/

### Technical Support
- **CKAN Documentation:** https://docs.ckan.org/
- **Issue Tracking:** Log issues in qatar_scraper.log
- **Developer:** Strategic Planning & Digital Transformation Advisor, Ministry of Labour

---

## FAQ

**Q: How often is Qatar Open Data Portal updated?**  
A: PSA publishes monthly statistics regularly. Most datasets update monthly or quarterly.

**Q: Can I use this data commercially?**  
A: Yes, Qatar Open Data License allows commercial use. Always check individual dataset licenses.

**Q: What if a dataset link is broken?**  
A: Report to PSA at info@psa.gov.qa. The scraper logs failed downloads automatically.

**Q: How do I get API access for real-time data?**  
A: The CKAN API is publicly accessible. No API key required for Qatar's portal.

**Q: Can I download datasets manually instead?**  
A: Yes, visit https://www.data.gov.qa/explore/ but the scraper automates and organizes everything.

**Q: How do I update an existing download?**  
A: Run the script again. It will download to new folders. Compare timestamps to identify updates.

---

## Next Steps After Successful Extraction

1. ✅ **Review Execution Report**
   - Check success rate
   - Identify any critical missing datasets
   - Note data volume and categories

2. ✅ **Validate Data Quality**  
   - Open sample files from each category
   - Check for completeness and accuracy
   - Verify date ranges and coverage

3. ✅ **Process for Analysis**
   - Clean and standardize formats
   - Handle missing values
   - Create derived metrics

4. ✅ **Load into Knowledge Graph**
   - Import into Neo4j
   - Create relationships between datasets
   - Build entity connections

5. ✅ **Integrate with Polaris Agents**
   - Configure agent data access
   - Set up query interfaces
   - Test agent responses

6. ✅ **Establish Update Cadence**
   - Schedule weekly/monthly runs
   - Monitor for new datasets
   - Track data freshness

---

## Success Criteria

After running the scraper, you should have:

- [x] Comprehensive catalog of 80-100+ relevant datasets
- [x] Downloaded files organized by business category  
- [x] Metadata and execution reports
- [x] Data covering key UDC intelligence domains
- [x] Foundation for Polaris multi-agent system
- [x] Automated pipeline for future updates

---

**Ready to begin? Run:** `python qatar_data_scraper.py`

**Questions?** Review execution_report.txt or check qatar_scraper.log for detailed information.
