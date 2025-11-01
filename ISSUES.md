# UDC Polaris - Known Issues & Resolutions

**Last Updated:** October 31, 2025

---

## Active Issues

*No active issues*

---

## Resolved Issues

### 1. ✅ Qatar Open Data Portal API Access (RESOLVED)

**Status:** 🟢 **RESOLVED**  
**Reported:** 2025-10-31  
**Resolved:** 2025-10-31  
**Resolution Time:** Same day

**Issue:**
Original API endpoint `https://www.data.gov.qa/api/3/action/package_search` was returning 404 errors.

**Root Cause:**
Qatar migrated from CKAN v3 API to **Opendatasoft Explore API v2.1**

**Resolution:**
- ✅ Discovered new API endpoint: `https://www.data.gov.qa/api/explore/v2.1`
- ✅ Created updated scraper: `scripts/qatar_data_scraper_v2.py`
- ✅ Tested successfully: 1,167 datasets available
- ✅ Fixed API response structure (`results` instead of `datasets`)

**Working API:**
```
GET https://www.data.gov.qa/api/explore/v2.1/catalog/datasets
Response: 200 OK, 1,167 datasets available
```

**Files Updated:**
- `scripts/qatar_data_scraper_v2.py` - New scraper with v2.1 API
- `test_qatar_api_v2.py` - Connection test utility

---

## Notes

- This is MVP - manual data loading is acceptable for initial phase
- Agent development can proceed with sample datasets
- Phase 2 will include robust data pipeline with error handling
- Real-world APIs change - this validates our flexible architecture

---

**Reporting New Issues:**
1. Add to "Active Issues" section above
2. Include: Status, Date, Component, Description, Impact, Workaround
3. Update TASK.md if it affects deliverables
4. Notify team in daily standup

