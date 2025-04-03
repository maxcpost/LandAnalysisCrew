# Land Analysis Data Dictionary

This document provides descriptions for the columns in the `master.csv` file used for property analysis.

## Basic Property Information

| Column | Description |
|--------|-------------|
| StockNumber | Unique identifier for each property listing |
| Property Address | Street address of the property |
| City | City where the property is located |
| State | State where the property is located |
| Zip | ZIP/Postal code of the property location |
| For Sale Price | The listing price of the property in USD |
| PropertyID | Secondary identifier used in property management systems |
| Land Area (AC) | Property area in acres - critical for development density calculations |
| Latitude | Geographic coordinate (latitude) of the property |
| Longitude | Geographic coordinate (longitude) of the property |
| Zoning | Legal zoning classification that determines allowable development types |
| County Name | The county where the property is located |
| Proposed Land Use | Suggested or approved future use for the property |

## Ownership and Sales Information

| Column | Description |
|--------|-------------|
| Owner Name | Current owner of the property |
| Sale Company Name | Real estate company handling the property sale |
| Sale Company Contact | Contact person at the real estate company |
| Sale Company Phone | Phone number for the real estate company |
| Sale Company Fax | Fax number for the real estate company |
| Last Sale Date | Date when the property was last sold |
| Last Sale Price | Price at which the property was last sold in USD |

## Flood Risk Information

| Column | Description |
|--------|-------------|
| In SFHA | Whether property is in Special Flood Hazard Area (Yes/No) - indicates flood risk |
| Fema Flood Zone | FEMA-designated flood zone classification (e.g., A, AE, X) - details flood risk level |
| FEMA Map Date | Date of the FEMA flood map used for flood zone determination |
| Floodplain Area | Portion of the property within the designated floodplain (often in acres or %) |

## Population Growth Metrics (Critical for Market Analysis)

| Column | Description |
|--------|-------------|
| % Pop Grwth 2020-2024(5m) | Percentage population growth within 5 miles (2020-2024) - Key indicator of recent area growth |
| % Pop Grwth 2024-2029(5m) | Projected percentage population growth within 5 miles (2024-2029) - Forecasted future growth |
| % Pop Grwth 2020-2024(10m) | Percentage population growth within 10 miles (2020-2024) - Broader area growth trend |
| % Pop Grwth 2024-2029(10m) | Projected percentage population growth within 10 miles (2024-2029) - Broader future growth |

## Population Data by Distance

| Column | Description |
|--------|-------------|
| 2000 Population(3m) | Total population within 3 miles in 2000 - Historical benchmark |
| 2020 Population(3m) | Total population within 3 miles in 2020 - Recent census data |
| 2024 Population(3m) | Total population within 3 miles in 2024 - Current estimate |
| 2029 Population(3m) | Projected population within 3 miles in 2029 - Future forecast |
| 2000 Population(5m) | Total population within 5 miles in 2000 - Historical benchmark |
| 2020 Population(5m) | Total population within 5 miles in 2020 - Recent census data |
| 2024 Population(5m) | Total population within 5 miles in 2024 - Current estimate |
| 2029 Population(5m) | Projected population within 5 miles in 2029 - Future forecast |
| 2000 Population(10m) | Total population within 10 miles in 2000 - Historical benchmark for wider region |
| 2020 Population(10m) | Total population within 10 miles in 2020 - Recent census data for wider region |
| 2024 Population(10m) | Total population within 10 miles in 2024 - Current estimate for wider region |
| 2029 Population(10m) | Projected population within 10 miles in 2029 - Future forecast for wider region |

## Income Data by Distance (Critical for Affordability Analysis)

| Column | Description |
|--------|-------------|
| 2020 Med HH Inc(3m) | Median household income within 3 miles in 2020 - Recent benchmark |
| 2024 Avg HH Inc(3m) | Average household income within 3 miles in 2024 - Current mean income |
| 2024 Med HH Inc(3m) | Median household income within 3 miles in 2024 - Current middle income point |
| 2029 Avg HH Inc(3m) | Projected average household income within 3 miles in 2029 - Future forecast of mean income |
| 2029 Med HH Inc(3m) | Projected median household income within 3 miles in 2029 - Future middle income point |
| 2020 Med HH Inc(5m) | Median household income within 5 miles in 2020 - Recent benchmark |
| 2024 Avg HH Inc(5m) | Average household income within 5 miles in 2024 - Current mean income |
| 2024 Med HH Inc(5m) | Median household income within 5 miles in 2024 - Current middle income point, key for affordability analysis |
| 2029 Avg HH Inc(5m) | Projected average household income within 5 miles in 2029 - Future income prediction |
| 2029 Med HH Inc(5m) | Projected median household income within 5 miles in 2029 - Future middle income point |
| 2020 Med HH Inc(10m) | Median household income within 10 miles in 2020 - Recent benchmark for wider region |
| 2024 Avg HH Inc(10m) | Average household income within 10 miles in 2024 - Current mean income for wider region |
| 2024 Med HH Inc(10m) | Median household income within 10 miles in 2024 - Current middle income point for wider region |
| 2029 Avg HH Inc(10m) | Projected average household income within 10 miles in 2029 - Future mean income for wider region |
| 2029 Med HH Inc(10m) | Projected median household income within 10 miles in 2029 - Future middle income for wider region |

## Home Value Data by Distance

| Column | Description |
|--------|-------------|
| 2024 Median Home Value(3m) | Median home value within 3 miles in 2024 - Current market benchmark |
| 2029 Median HH Value(3m) | Projected median home value within 3 miles in 2029 - Future market prediction |
| 2024 Median Home Value(5m) | Median home value within 5 miles in 2024 - Current market benchmark, crucial for price positioning |
| 2029 Median HH Value(5m) | Projected median home value within 5 miles in 2029 - Future market prediction |
| 2024 Median Home Value(10m) | Median home value within 10 miles in 2024 - Wider market context |
| 2029 Median HH Value(10m) | Projected median home value within 10 miles in 2029 - Future wider market |

## Housing Unit Growth

| Column | Description |
|--------|-------------|
| % HU Grwth 2020-2024(3m) | Percentage growth in housing units within 3 miles (2020-2024) - Recent construction activity |
| % HU Grwth 2020-2024(5m) | Percentage growth in housing units within 5 miles (2020-2024) - Area construction trends |
| % HU Grwth 2020-2024(10m) | Percentage growth in housing units within 10 miles (2020-2024) - Regional construction trends |

## Home Value Distribution Data (Price Brackets)

| Column | Description |
|--------|-------------|
| 2024 Home Value $1,000,000+(3m) | Number of homes valued over $1,000,000 within 3 miles in 2024 - Luxury housing presence |
| 2024 Home Value $100,000-200,000(3m) | Number of homes valued between $100,000-$200,000 within 3 miles in 2024 - Affordable housing stock |
| 2024 Home Value $200,000-300,000(3m) | Number of homes valued between $200,000-$300,000 within 3 miles in 2024 - Moderate housing stock |
| 2024 Home Value $300,000-400,000(3m) | Number of homes valued between $300,000-$400,000 within 3 miles in 2024 - Mid-level housing stock |
| 2024 Home Value $400,000-500,000(3m) | Number of homes valued between $400,000-$500,000 within 3 miles in 2024 - Upper-mid housing stock |
| 2024 Home Value $500,000-1,000,000(3m) | Number of homes valued between $500,000-$1,000,000 within 3 miles in 2024 - Upper housing stock |

## Detailed Demographic Data (5-mile radius)

| Column | Description |
|--------|-------------|
| TotPop_5 | Total population within 5 miles - Current population base |
| TotHHs_5 | Total households within 5 miles - Number of household units, important for market sizing |
| MedianHHInc_5 | Median household income within 5 miles - Middle income point, key for affordability |
| AvgHHInc_5 | Average household income within 5 miles - Mean income level |
| TotHUs_5 | Total housing units within 5 miles - Housing supply metric |
| OccHUs_5 | Occupied housing units within 5 miles - Indicates demand level |
| OwnerOcc_5 | Owner-occupied housing units within 5 miles - Ownership rate metric |
| RenterOcc_5 | Renter-occupied housing units within 5 miles - Rental market size |
| AvgOwnerHHSize_5 | Average owner household size within 5 miles - Typical family size of owners |
| AvgRenterHHSize_5 | Average renter household size within 5 miles - Typical family size of renters |
| VacHUs_5 | Vacant housing units within 5 miles - Key indicator of oversupply or seasonal area |
| VacantForSale_5 | Vacant units for sale within 5 miles - Direct competition metric |
| VacantForRent_5 | Vacant units for rent within 5 miles - Rental market vacancy |
| OwnerVacRate_5 | Owner vacancy rate within 5 miles - Percentage of for-sale homes vacant |
| RenterVacRate_5 | Renter vacancy rate within 5 miles - Percentage of rental units vacant, key market tightness indicator |
| MedianHValue_5 | Median home value within 5 miles - Middle price point of homes |
| MedianGrossRent_5 | Median gross rent within 5 miles - Middle price point for rentals |
| AvgGrossRent_5 | Average gross rent within 5 miles - Mean rental cost, important for investment analysis |

## Demographic Details (5-mile radius)

| Column | Description |
|--------|-------------|
| InElementary_5 | Number of children enrolled in elementary school within 5 miles - Family demographic indicator |
| InHighSchool_5 | Number of children enrolled in high school within 5 miles - Teen demographic indicator |
| InCollege_5 | Number of people enrolled in college within 5 miles - Young adult demographic indicator |
| VacantSeasonal_5 | Vacant units for seasonal use within 5 miles - Indicator of vacation/second home market |
| MobileHomes_5 | Number of mobile homes within 5 miles - Alternative housing market indicator |
| MobileHomesPerK_5 | Mobile homes per 1,000 housing units within 5 miles - Affordable housing prevalence |

## Home Value Brackets in 5-mile radius

| Column | Description |
|--------|-------------|
| HvalUnder50_5 | Homes valued under $50,000 within 5 miles - Very low-cost housing count |
| Hval50_5 | Homes valued $50,000-$99,999 within 5 miles - Low-cost housing count |
| Hval100_5 | Homes valued $100,000-$149,999 within 5 miles - Moderate-low cost housing |
| Hval150_5 | Homes valued $150,000-$199,999 within 5 miles - Moderate cost housing |
| Hval200_5 | Homes valued $200,000-$299,999 within 5 miles - Moderate-high cost housing |
| Hval300_5 | Homes valued $300,000-$499,999 within 5 miles - High cost housing |
| Hval500_5 | Homes valued $500,000-$999,999 within 5 miles - Very high cost housing |
| HvalOverMillion_5 | Homes valued over $1,000,000 within 5 miles - Luxury housing count |

## Nearby Amenities and Services

| Column | Description |
|--------|-------------|
| Nearest_Walmart_Distance_Miles | Distance to the nearest Walmart in miles - Retail convenience metric |
| Nearest_Walmart_Travel_Time_Minutes | Travel time to the nearest Walmart in minutes - Accessibility metric |
| Nearest_Hospital_Distance_Miles | Distance to the nearest hospital in miles - Healthcare access metric |
| Nearest_Hospital_Travel_Time_Minutes | Travel time to the nearest hospital in minutes - Emergency service access |
| Nearest_Park_Distance_Miles | Distance to the nearest park in miles - Recreation access metric |
| Nearest_Park_Travel_Time_Minutes | Travel time to the nearest park in minutes - Lifestyle amenity access |

## Composite Scoring Metrics

| Column | Description |
|--------|-------------|
| Home_Affordability | Score that measures property affordability relative to local incomes (higher is better) - Key for attainable housing viability |
| Rent_Affordability | Score that measures rent affordability in the area (higher is better) - Indicates rental burden levels |
| Convenience_Index | Score that measures proximity to amenities (higher is better) - Lifestyle and convenience factor |
| Population_Access | Score that measures access to population centers (higher is better) - Market size potential |
| Market_Saturation | Score that measures how saturated the market is (lower means less competition) - Competitive landscape metric |
| Composite_Score | Overall score combining all factors (higher is better) - Summary metric of development potential |

## Percentile Rankings

| Column | Description |
|--------|-------------|
| Home_Affordability Percentile | Percentile ranking for home affordability (higher is better) - How this property compares to others |
| Rent_Affordability Percentile | Percentile ranking for rent affordability (higher is better) - Relative position for rental stress |
| Convenience_Index Percentile | Percentile ranking for convenience (higher is better) - Relative amenity access position |
| Population_Access Percentile | Percentile ranking for population access (higher is better) - Relative market access position |
| Market_Saturation Percentile | Percentile ranking for market saturation (higher is better) - Relative competition position |
| Composite_Score Percentile | Percentile ranking for overall composite score (higher is better) - Overall relative position | 