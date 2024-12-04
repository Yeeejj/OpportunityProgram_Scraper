import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re

def scrape_scholarships():
    programs = []
    
    # Extended list of websites to scrape
    websites = [
        "https://opportunitiescorners.com/",
        "https://scholarshipscorner.website/",
        "https://www.youthop.com/",
        "https://opportunitiesforyouth.org/",
        "https://greatyop.com/",
        "https://www.un.org/en/",
        "https://www.levels.fyi/",
        "https://www.indeed.com/",
        "https://www.unesco.org/",
        "https://www.scholarshipportal.com/",
        "https://www.findaphd.com/",
        "https://www.educations.com/",
        "https://www.scholars4dev.com/",
        "https://www.opportunitiesforafricans.com/",
        "https://www.mladiinfo.eu/",
        "https://www.afterschoolafrica.com/",
        "https://www.european-funding-guide.eu/"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for website in websites:
        try:
            # Skip LinkedIn and Google as they require authentication/special handling
            if "linkedin.com" in website or "google.com" in website:
                continue
                
            response = requests.get(website, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Enhanced scraping logic with more detailed information
            program_elements = soup.find_all(['div', 'article'], class_=re.compile(r'program|scholarship|opportunity|job|position|grant'))
            
            for element in program_elements:
                # Extract year from deadline or posting date
                date_text = element.find(text=re.compile(r'\d{4}'))
                year = extract_year(date_text) if date_text else "Ongoing"
                
                program = {
                    'title': clean_text(element.find(class_=re.compile(r'title|heading')).text if element.find(class_=re.compile(r'title|heading')) else ""),
                    'university': clean_text(element.find(class_=re.compile(r'university|institution|organization|company')).text if element.find(class_=re.compile(r'university|institution|organization|company')) else ""),
                    'country': clean_text(element.find(class_=re.compile(r'country|location')).text if element.find(class_=re.compile(r'country|location')) else ""),
                    'deadline': clean_text(element.find(class_=re.compile(r'deadline|date|apply-by')).text if element.find(class_=re.compile(r'deadline|date|apply-by')) else ""),
                    'type': determine_program_type(element),
                    'funding': extract_funding_info(element),
                    'year': year,
                    'link': extract_link(element, website),
                    'description': clean_text(element.find(class_=re.compile(r'description|content|summary')).text if element.find(class_=re.compile(r'description|content|summary')) else ""),
                    'requirements': extract_requirements(element),
                    'posted_date': extract_posted_date(element),
                    'source': website
                }
                programs.append(program)
                
            # Respect robots.txt and be nice to servers
            time.sleep(3)
            
        except Exception as e:
            print(f"Error scraping {website}: {str(e)}")
            continue
    
    return programs

def clean_text(text):
    """Clean and normalize text content"""
    return ' '.join(text.strip().split())

def extract_year(text):
    """Extract year from text"""
    match = re.search(r'\b20\d{2}\b', text)
    return match.group(0) if match else "Ongoing"

def determine_program_type(element):
    """Determine program type based on content"""
    text_content = element.get_text().lower()
    
    type_keywords = {
        'competition': 'competitions',
        'conference': 'conferences',
        'papers': 'papers_conferences',
        'code camp': 'code_camp',
        'hackathon': 'hackathons',
        'exchange': 'exchange_programs',
        'entrepreneur': 'entrepreneurial',
        'internship': 'internships',
        'fellowship': 'fellowships',
        'course': 'online_courses',
        'leadership': 'leadership',
        'sdg': 'sdgs',
        'summer program': 'summer_programs',
        'summer school': 'summer_schools',
        'training': 'training',
        'youth forum': 'youth_forums',
        'united nations': 'united_nations',
        'workshop': 'workshops',
        'government': 'gov_scholarships',
        'high school': 'highschool',
        'master': 'masters',
        'mba': 'mba',
        'phd': 'phd',
        'postdoc': 'postdoc',
        'undergraduate': 'undergraduate'
    }
    
    for keyword, program_type in type_keywords.items():
        if keyword in text_content:
            return program_type
    
    return 'miscellaneous'

def extract_funding_info(element):
    """Extract funding information"""
    funding_element = element.find(class_=re.compile(r'funding|scholarship|award'))
    if funding_element:
        return clean_text(funding_element.text)
    return "Contact institution for funding details"

def extract_link(element, base_url):
    """Extract and validate program link"""
    link_element = element.find('a', href=True)
    if link_element:
        link = link_element['href']
        return link if link.startswith('http') else f"{base_url.rstrip('/')}{link}"
    return base_url

def extract_requirements(element):
    """Extract program requirements"""
    req_element = element.find(class_=re.compile(r'requirements|eligibility'))
    if req_element:
        return clean_text(req_element.text)
    return "See program website for detailed requirements"

def extract_posted_date(element):
    """Extract posting date"""
    date_element = element.find(class_=re.compile(r'posted|published|date'))
    if date_element:
        return clean_text(date_element.text)
    return "Not specified"

if __name__ == "__main__":
    programs = scrape_scholarships()
    
    # Save to JSON file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'programs_{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(programs, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(programs)} programs and saved to {filename}")