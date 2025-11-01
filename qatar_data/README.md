# Qatar Open Data Directory

This directory contains data from the Qatar Open Data Portal and other Qatar government sources.

## Current Status

⚠️ **Note:** Automated API access to data.gov.qa is currently under investigation (see ISSUES.md). For MVP development, we're using manual downloads and sample datasets.

## Directory Structure

```
qatar_data/
├── raw/                    # Raw downloaded data files
│   ├── real_estate/       # Property, construction, housing
│   ├── population/        # Demographics, census, migration
│   ├── economy/           # GDP, inflation, trade
│   ├── tourism/           # Hotels, visitors
│   ├── labor/             # Employment, wages
│   ├── energy/            # Electricity, cooling
│   ├── infrastructure/    # Development, transport
│   └── sample/            # Sample datasets for development
│
├── processed/             # Cleaned and standardized data
│   └── (generated during processing)
│
├── metadata/              # Catalogs and quality reports
│   ├── catalog.csv       # Dataset catalog
│   └── sources.txt       # Data source documentation
│
└── README.md             # This file
```

## Manual Data Download Process (Temporary)

Until API access is restored, follow this process:

### 1. Visit Qatar Open Data Portal

https://www.data.gov.qa/explore/

### 2. Priority Datasets to Download

**Real Estate & Construction:**
- Real estate transactions
- Building permits
- Construction activity
- Property prices by zone

**Population & Demographics:**
- Monthly population statistics
- Population by nationality
- Household statistics
- Migration data

**Economic Indicators:**
- GDP growth rates
- Consumer Price Index (CPI)
- Inflation rates
- Trade statistics

**Tourism:**
- Hotel occupancy rates
- Tourist arrivals
- Average stay duration

**Labor Market:**
- Employment statistics by sector
- Wage levels
- Qatarization rates

**Energy:**
- Electricity consumption
- District cooling demand
- KAHRAMAA tariffs

### 3. Save to Appropriate Folders

```bash
# Example:
qatar_data/raw/real_estate/property_transactions_2023.csv
qatar_data/raw/population/monthly_population_2024.xlsx
qatar_data/raw/economy/gdp_quarterly_2024.xlsx
```

### 4. Document Source

Add entry to `metadata/sources.txt`:
```
Dataset: Property Transactions 2023
Source: https://www.data.gov.qa/explore/dataset/...
Download Date: 2025-10-31
File: raw/real_estate/property_transactions_2023.csv
Notes: Q1-Q3 2024 data
```

## Sample Data for Development

For immediate development needs, we've created sample datasets in `raw/sample/`:

- `sample_financial_metrics.csv` - UDC financial indicators
- `sample_market_data.csv` - Real estate market trends
- `sample_economic_indicators.csv` - Qatar economic data

These are based on:
- UDC Annual Reports 2023-2024
- Public financial statements
- Industry benchmarks

## Data Processing Pipeline

Once data is in `raw/`, process it:

```bash
# From backend directory
python -m app.data.process_qatar_data
```

This will:
1. Validate and clean data
2. Standardize formats
3. Create embeddings for ChromaDB
4. Load into PostgreSQL
5. Generate quality reports

## Contact

For API access issues:
- Email: info@psa.gov.qa
- Website: https://www.psa.gov.qa/

For UDC Polaris data questions:
- See: ISSUES.md
- Contact: Data Engineering Team

