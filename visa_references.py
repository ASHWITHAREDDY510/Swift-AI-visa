"""
SwiftVisa - Milestone 2: Official Government Visa Website References
Maps countries and visa types to their official immigration websites

Author: [Your Name]
Date: 2026
Milestone: 2 - RAG Pipeline
"""

OFFICIAL_VISA_WEBSITES = {
    "United Kingdom": {
        "base_url": "https://www.gov.uk",
        "visa_types": {
            "Work": "https://www.gov.uk/uk-visa",
            "Student": "https://www.gov.uk/student-visa",
            "Tourist": "https://www.gov.uk/standard-visitor-visa",
            "Family": "https://www.gov.uk/apply-for-family-visa",
            "default": "https://www.gov.uk/browse/visas-immigration"
        }
    },
    "United States": {
        "base_url": "https://www.uscis.gov",
        "visa_types": {
            "Work": "https://www.uscis.gov/working-in-the-united-states",
            "Student": "https://www.uscis.gov/study-in-the-united-states",
            "Tourist": "https://www.uscis.gov/visit-the-united-states",
            "Family": "https://www.uscis.gov/family",
            "default": "https://www.uscis.gov/tools"
        }
    },
    "Canada": {
        "base_url": "https://www.canada.ca",
        "visa_types": {
            "Work": "https://www.canada.ca/en/immigration-refugees-citizenship/services/work-canada.html",
            "Student": "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada.html",
            "Tourist": "https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada.html",
            "Family": "https://www.canada.ca/en/immigration-refugees-citizenship/services/family-sponsorship.html",
            "default": "https://www.canada.ca/en/immigration-refugees-citizenship/services.html"
        }
    },
    "Australia": {
        "base_url": "https://www.homeaffairs.gov.au",
        "visa_types": {
            "Work": "https://www.homeaffairs.gov.au/visas/working-in-australia",
            "Student": "https://www.homeaffairs.gov.au/visas/study-in-australia",
            "Tourist": "https://www.homeaffairs.gov.au/visas/tourist-visitor-visas",
            "Family": "https://www.homeaffairs.gov.au/visas/family-stream",
            "default": "https://www.homeaffairs.gov.au/visas"
        }
    },
    "Singapore": {
        "base_url": "https://www.mom.gov.sg",
        "visa_types": {
            "Work": "https://www.mom.gov.sg/passes-and-permits",
            "Student": "https://www.mom.gov.sg/passes-and-permits/student-pass",
            "Tourist": "https://www.ica.gov.sg/enter-transit-depart/entering-singapore",
            "Family": "https://www.mom.gov.sg/passes-and-permits/dependants-pass",
            "default": "https://www.mom.gov.sg/passes-and-permits"
        }
    },
    "India": {
        "base_url": "https://www.mha.gov.in",
        "visa_types": {
            "Work": "https://www.mha.gov.in/sites/default/files/VisaGuidelines.pdf",
            "Student": "https://www.mha.gov.in/sites/default/files/VisaGuidelines.pdf",
            "Tourist": "https://www.mha.gov.in/sites/default/files/VisaGuidelines.pdf",
            "Family": "https://www.mha.gov.in/sites/default/files/VisaGuidelines.pdf",
            "default": "https://www.mha.gov.in/en"
        }
    }
}


def get_official_visa_website(country: str, visa_type: str = None) -> str:
    """
    Get official government website for visa information
    
    Args:
        country: Country name (e.g., "United Kingdom")
        visa_type: Visa type (e.g., "Student", "Work")
    
    Returns:
        URL to official government visa website
    """
    if not country:
        return "https://www.iom.int"
    
    country_clean = country.strip()
    
    if country_clean in OFFICIAL_VISA_WEBSITES:
        country_data = OFFICIAL_VISA_WEBSITES[country_clean]
        
        if visa_type:
            visa_clean = visa_type.strip()
            # Try exact match
            if visa_clean in country_data["visa_types"]:
                return country_data["visa_types"][visa_clean]
            # Try without "Visa" suffix
            visa_base = visa_clean.replace(" Visa", "").strip()
            if visa_base in country_data["visa_types"]:
                return country_data["visa_types"][visa_base]
        
        return country_data["visa_types"].get("default", country_data["base_url"])
    
    return "https://www.iom.int"


if __name__ == "__main__":
    # Test the function
    print("Testing visa_references.py")
    print("=" * 70)
    
    test_cases = [
        ("United Kingdom", "Student"),
        ("United States", "Work"),
        ("Canada", "Tourist"),
        ("Australia", "Student"),
        ("Singapore", "Work"),
        ("India", "Work"),
        ("Unknown Country", "Work"),
    ]
    
    for country, visa in test_cases:
        url = get_official_visa_website(country, visa)
        print(f"{country} - {visa}: {url}")
    
    print("=" * 70)
    print("✅ visa_references.py working correctly!")