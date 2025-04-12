#!/usr/bin/env python3
"""
Resume Parser and Formatter
Created by: Andrew Arz
Date: 4/11/2025
Version: 1.0.0
License: MIT

This tool transforms a plain text resume into beautifully formatted HTML and PDF documents.
It parses sections like experience, education, skills, and certifications from a simple
text file and generates a professional-looking resume.

Copyright (c) 2025 Andrew Arz
All rights reserved.

Feel free to modify and use this code for your personal use.
For commercial use or redistribution, please contact the author.
"""

import re
import sys
import os
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check for PDF generation capabilities
PDF_SUPPORT = False
try:
    import pdfkit
    PDF_SUPPORT = True
except ImportError:
    try:
        from weasyprint import HTML
        PDF_SUPPORT = True
    except ImportError:
        pass


class ResumeParser:
    def __init__(self, input_file):
        self.input_file = input_file
        self.content = ""
        self.resume_data = {
            'name': 'Your Name',
            'contact': {},
            'summary': '',
            'experience': [],
            'education': [],
            'skills': {},
            'certifications': [],
            'honors_awards': []
        }
    
    def load_content(self):
        """Load content from the input file"""
        try:
            with open(self.input_file, 'r') as file:
                self.content = file.read()
                logger.info("Resume content loaded successfully")
        except FileNotFoundError:
            logger.error(f"File not found: {self.input_file}")
            sys.exit(1)
    
    def parse(self):
        """Parse resume content into structured data"""
        # Extract name (usually at the beginning)
        lines = self.content.split('\n')
        if lines and lines[0].strip():
            self.resume_data['name'] = lines[0].strip()
            logger.info(f"Found name: {self.resume_data['name']}")
        
        # Extract contact information
        self._extract_contact_info(lines[:10])  # Look in first few lines
        
        # Extract all sections
        self._extract_all_sections()
        
        logger.info("Resume parsed successfully")
        return self.resume_data
    
    def _extract_contact_info(self, top_lines):
        """Extract contact information from the top lines of the resume"""
        # Join the top lines for easier searching
        top_text = '\n'.join(top_lines)
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', top_text)
        if email_match:
            self.resume_data['contact']['email'] = email_match.group(0)
        
        # Extract phone number
        phone_match = re.search(r'\d{3}[\s\.-]?\d{3}[\s\.-]?\d{4}', top_text)
        if phone_match:
            self.resume_data['contact']['phone'] = phone_match.group(0)
        
        # Extract location (city, state/country) - FIXED VERSION
        # Look for location pattern on individual lines instead of across line breaks
        for line in top_lines:
            line = line.strip()
            # Look for typical location format (City, State) on a single line
            location_match = re.search(r'^([A-Za-z\s]+,\s+[A-Za-z\s]{2,})$', line)
            if location_match:
                self.resume_data['contact']['location'] = location_match.group(1)
                break
    
    def _extract_all_sections(self):
        """Extract all sections from the resume"""
        # Find the positions of all major section headers
        section_headers = {
            'SUMMARY': -1,
            'EXPERIENCE': -1,
            'EDUCATION': -1,
            'CERTIFICATIONS': -1,
            'SKILLS': -1,
            'HONORS AND AWARDS': -1
        }
        
        lines = self.content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip().upper()
            # Check for section headers
            for header in section_headers.keys():
                if line == header:
                    section_headers[header] = i
        
        # Extract sections based on their positions
        sections = {}
        headers_list = sorted([(pos, header) for header, pos in section_headers.items() if pos >= 0])
        
        for i, (pos, header) in enumerate(headers_list):
            start = pos + 1  # Start after the header
            end = len(lines)  # Default to end of file
            
            # If there's a next section, set end to that section's start
            if i < len(headers_list) - 1:
                end = headers_list[i+1][0]
            
            # Extract and clean the section content
            section_lines = [line for line in lines[start:end] if line.strip()]
            sections[header] = '\n'.join(section_lines)
        
        # Parse each section
        if 'SUMMARY' in sections:
            self.resume_data['summary'] = sections['SUMMARY']
        
        if 'EXPERIENCE' in sections:
            self.resume_data['experience'] = self._parse_experience(sections['EXPERIENCE'])
        
        if 'EDUCATION' in sections:
            self.resume_data['education'] = self._parse_education(sections['EDUCATION'])
        
        if 'CERTIFICATIONS' in sections:
            self.resume_data['certifications'] = self._parse_certifications(sections['CERTIFICATIONS'])
        
        if 'SKILLS' in sections:
            self.resume_data['skills'] = self._parse_skills(sections['SKILLS'])
        
        if 'HONORS AND AWARDS' in sections:
            self.resume_data['honors_awards'] = self._parse_honors_awards(sections['HONORS AND AWARDS'])
    
    def _parse_experience(self, content):
        """Parse experience section to extract jobs"""
        experience_entries = []
        
        # Split content into lines
        lines = content.split('\n')
        
        i = 0
        company = None
        position = None
        period = None
        description = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            # If line is empty, skip
            if not line:
                i += 1
                continue
            
            # Check if this is a bullet point
            if line.startswith('•'):
                # Add to current job description
                description.append(line[1:].strip())
                i += 1
                continue
            
            # Check if this might be a date range
            date_match = re.search(r'\d\d/\d\d\d\d', line)
            if date_match and 'present' in line.lower() or '-' in line and line.count('/') >= 2:
                # This is a date range
                period = line
                i += 1
                continue
            
            # Check if we should save the current job before starting a new one
            if company and (line.strip() and len(line.strip().split()) > 2):
                # This might be a new company, save the current job first
                experience_entries.append({
                    'company': company,
                    'position': position or '',
                    'period': period or '',
                    'description': description
                })
                company = line
                position = None
                period = None
                description = []
                i += 1
                continue
            
            # If we're here, this is either the first company or a position line
            if not company:
                company = line
            elif not position:
                position = line
            
            i += 1
        
        # Don't forget to add the last job
        if company:
            experience_entries.append({
                'company': company,
                'position': position or '',
                'period': period or '',
                'description': description
            })
        
        return experience_entries
    
    def _parse_education(self, content):
        """Parse education section"""
        education_entries = []
        
        # For now, just create a simple entry
        if content:
            education_entries.append({
                'institution': 'Education',
                'degree': content,
                'period': '',
                'details': []
            })
        
        return education_entries
    
    def _parse_certifications(self, content):
        """Parse certifications section"""
        certifications = []
        
        current_provider = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('•'):
                # This is a certification under the current provider
                cert_name = line[1:].strip()
                if current_provider:
                    certifications.append({
                        'provider': current_provider,
                        'certification': cert_name
                    })
            else:
                # This is a provider
                current_provider = line
        
        return certifications
    
    def _parse_skills(self, content):
        """Parse skills section - look for category headers and skills"""
        skills = {}
        
        lines = content.split('\n')
        current_category = "General"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a category header (ends with a colon)
            if line.endswith(':'):
                current_category = line[:-1].strip()
                skills[current_category] = []
            else:
                # Add skills to current category
                if current_category not in skills:
                    skills[current_category] = []
                
                # Split by common separators
                for skill in re.split(r',|\|', line):
                    skill = skill.strip()
                    if skill:
                        skills[current_category].append(skill)
        
        return skills
    
    def _parse_honors_awards(self, content):
        """Parse honors and awards section"""
        awards = []
        
        lines = content.split('\n')
        current_org = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('•'):
                # This is an award under the current organization
                award_name = line[1:].strip()
                if current_org:
                    awards.append({
                        'organization': current_org,
                        'award': award_name
                    })
            else:
                # This is an organization
                current_org = line
        
        return awards


class ResumeGenerator:
    def __init__(self, resume_data):
        self.data = resume_data
    
    def generate_html(self):
        """Generate HTML resume"""
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.data['name']} - Resume</title>
    <style>
        /* Modern, clean resume styling */
        :root {{
            --primary-color: #2d3e50;
            --secondary-color: #3498db;
            --text-color: #333;
            --light-color: #f5f5f5;
            --border-color: #ddd;
        }}
        
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
        }}
        
        /* Header section */
        .header {{
            margin-bottom: 30px;
        }}
        
        .name {{
            font-size: 2.2em;
            color: var(--primary-color);
            margin-bottom: 5px;
            font-weight: 700;
            text-align: center;
        }}
        
        .contact-info {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 10px;
            border-top: 2px solid var(--primary-color);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 0;
        }}
        
        .contact-item {{
            margin: 0 10px;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        /* Section styling */
        .section {{
            margin-bottom: 25px;
        }}
        
        .section-title {{
            color: var(--primary-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 5px;
            margin-top: 25px;
            font-size: 1.5em;
            font-weight: 600;
        }}
        
        .summary {{
            margin-bottom: 25px;
            line-height: 1.6;
        }}
        
        /* Experience and Education */
        .entry {{
            margin-bottom: 20px;
            page-break-inside: avoid;
        }}
        
        .entry-header {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }}
        
        .company, .institution {{
            font-weight: bold;
            font-size: 1.1em;
            color: var(--primary-color);
        }}
        
        .position, .degree {{
            font-style: italic;
            margin: 5px 0;
            color: var(--secondary-color);
        }}
        
        .period {{
            color: #666;
            font-weight: 500;
        }}
        
        ul {{
            margin-top: 8px;
            padding-left: 20px;
        }}
        
        ul li {{
            margin-bottom: 5px;
        }}
        
        /* Skills section */
        .skills-section {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .skill-category {{
            margin-bottom: 15px;
            flex: 1 0 45%;
        }}
        
        .skill-category-title {{
            color: var(--primary-color);
            margin-bottom: 5px;
            font-weight: 600;
        }}
        
        .skill-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .skill-item {{
            background-color: #f0f7ff;
            border: 1px solid #d1e6ff;
            border-radius: 15px;
            padding: 5px 12px;
            font-size: 0.9em;
        }}
        
        /* Certifications section */
        .cert-group {{
            margin-bottom: 15px;
        }}
        
        .cert-provider {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        /* Awards section */
        .award-group {{
            margin-bottom: 15px;
        }}
        
        .award-org {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        /* Print styling */
        @media print {{
            body {{
                padding: 0;
                font-size: 12pt;
                background-color: white;
            }}
            
            .contact-info {{
                padding: 8px 0;
            }}
            
            .section-title {{
                margin-top: 15px;
            }}
            
            a {{
                color: var(--text-color);
                text-decoration: none;
            }}
            
            .skill-item {{
                border: 1px solid #ccc;
                background-color: #f8f8f8;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="name">{self.data['name']}</h1>
        <div class="contact-info">
            {self._generate_contact_info()}
        </div>
    </div>
    
    {self._generate_summary()}
    
    <div class="section">
        <h2 class="section-title">Professional Experience</h2>
        {self._generate_experience()}
    </div>
    
    {self._generate_certifications()}
    
    {self._generate_education()}
    
    <div class="section">
        <h2 class="section-title">Skills</h2>
        {self._generate_skills()}
    </div>
    
    {self._generate_honors_awards()}
</body>
</html>'''
        
        return html
    
    def _generate_contact_info(self):
        """Generate contact information HTML"""
        contact_items = []
        
        if self.data['contact'].get('email'):
            contact_items.append(f'<div class="contact-item">📧 <a href="mailto:{self.data["contact"]["email"]}">{self.data["contact"]["email"]}</a></div>')
        
        if self.data['contact'].get('phone'):
            contact_items.append(f'<div class="contact-item">📱 {self.data["contact"]["phone"]}</div>')
        
        if self.data['contact'].get('linkedin'):
            linkedin_url = self.data["contact"]["linkedin"]
            if not linkedin_url.startswith('http'):
                linkedin_url = f"https://{linkedin_url}"
            contact_items.append(f'<div class="contact-item">💼 <a href="{linkedin_url}" target="_blank">{self.data["contact"]["linkedin"]}</a></div>')
        
        if self.data['contact'].get('location'):
            contact_items.append(f'<div class="contact-item">📍 {self.data["contact"]["location"]}</div>')
        
        return ''.join(contact_items)
    
    def _generate_summary(self):
        """Generate summary section HTML"""
        if not self.data['summary']:
            return ""
        
        return f'''<div class="section">
        <h2 class="section-title">Professional Summary</h2>
        <div class="summary">
            <p>{self.data['summary']}</p>
        </div>
    </div>'''
    
    def _generate_experience(self):
        """Generate work experience section HTML"""
        if not self.data['experience']:
            return "<p>No work experience provided</p>"
        
        entries_html = []
        
        for job in self.data['experience']:
            description_html = ""
            if job['description']:
                description_items = [f"<li>{item}</li>" for item in job['description']]
                description_html = f"<ul>{''.join(description_items)}</ul>"
            
            entries_html.append(f'''<div class="entry">
                <div class="entry-header">
                    <div class="company">{job['company']}</div>
                    <div class="period">{job['period']}</div>
                </div>
                <div class="position">{job['position']}</div>
                {description_html}
            </div>''')
        
        return ''.join(entries_html)
    
    def _generate_education(self):
        """Generate education section HTML"""
        if not self.data['education']:
            return ""
        
        entries_html = ["<div class='section'>", "<h2 class='section-title'>Education</h2>"]
        
        for edu in self.data['education']:
            details_html = ""
            if edu.get('details'):
                details_items = [f"<li>{item}</li>" for item in edu['details']]
                details_html = f"<ul>{''.join(details_items)}</ul>"
            
            entries_html.append(f'''<div class="entry">
                <div class="entry-header">
                    <div class="institution">{edu['institution']}</div>
                    <div class="period">{edu.get('period', '')}</div>
                </div>
                <div class="degree">{edu.get('degree', '')}</div>
                {details_html}
            </div>''')
        
        entries_html.append("</div>")
        return ''.join(entries_html)
    
    def _generate_certifications(self):
        """Generate certifications section HTML"""
        if not self.data['certifications']:
            return ""
        
        # Group certifications by provider
        providers = {}
        for cert in self.data['certifications']:
            provider = cert.get('provider', 'Other')
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(cert['certification'])
        
        html = ["<div class='section'>", "<h2 class='section-title'>Certifications</h2>"]
        
        for provider, certs in providers.items():
            cert_items = ''.join([f"<li>{cert}</li>" for cert in certs])
            html.append(f'''<div class="cert-group">
                <div class="cert-provider">{provider}</div>
                <ul>{cert_items}</ul>
            </div>''')
        
        html.append("</div>")
        return ''.join(html)
    
    def _generate_skills(self):
        """Generate skills section HTML"""
        if not self.data['skills']:
            return "<p>No skills provided</p>"
        
        skills_html = '<div class="skills-section">'
        
        for category, skill_list in self.data['skills'].items():
            if not skill_list:
                continue
                
            skill_items = ''.join([f'<div class="skill-item">{skill}</div>' for skill in skill_list])
            
            skills_html += f'''<div class="skill-category">
                <div class="skill-category-title">{category}</div>
                <div class="skill-list">
                    {skill_items}
                </div>
            </div>'''
        
        skills_html += '</div>'
        return skills_html
    
    def _generate_honors_awards(self):
        """Generate honors and awards section HTML"""
        if not self.data['honors_awards']:
            return ""
        
        # Group awards by organization
        orgs = {}
        for award in self.data['honors_awards']:
            org = award.get('organization', 'Other')
            if org not in orgs:
                orgs[org] = []
            orgs[org].append(award['award'])
        
        html = ["<div class='section'>", "<h2 class='section-title'>Honors and Awards</h2>"]
        
        for org, awards in orgs.items():
            award_items = ''.join([f"<li>{award}</li>" for award in awards])
            html.append(f'''<div class="award-group">
                <div class="award-org">{org}</div>
                <ul>{award_items}</ul>
            </div>''')
        
        html.append("</div>")
        return ''.join(html)


def generate_pdf(html_path, pdf_path):
    """Generate PDF from HTML file"""
    if not PDF_SUPPORT:
        logger.warning("PDF generation requires either pdfkit or weasyprint.")
        logger.warning("Install one of them with: pip install pdfkit or pip install weasyprint")
        return False
    
    try:
        # Try using pdfkit first (requires wkhtmltopdf installed)
        try:
            import pdfkit
            logger.info("Attempting to generate PDF using pdfkit...")
            pdfkit.from_file(html_path, pdf_path)
            return True
        except (ImportError, Exception) as e:
            logger.error(f"PDF generation failed using pdfkit: {str(e)}")
            
            # If pdfkit fails, try weasyprint
            try:
                from weasyprint import HTML
                logger.info("Attempting to generate PDF using weasyprint...")
                HTML(filename=html_path).write_pdf(pdf_path)
                return True
            except Exception as inner_e:
                logger.error(f"PDF generation failed using weasyprint: {str(inner_e)}")
                return False
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Parse plain text resume and generate pretty HTML and PDF')
    parser.add_argument('input_file', help='Path to plain text resume input file')
    parser.add_argument('-o', '--output', help='Output HTML file (default: resume.html)', default='resume.html')
    parser.add_argument('--pdf', help='Generate PDF output (requires pdfkit or weasyprint)', action='store_true')
    parser.add_argument('--pdf-output', help='Output PDF file (default: resume.pdf)', default='resume.pdf')
    parser.add_argument('-v', '--verbose', help='Show verbose output', action='store_true')
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Processing resume from: {args.input_file}")
    logger.info(f"Output HTML file: {args.output}")
    if args.pdf:
        logger.info(f"Will generate PDF: {args.pdf_output}")
    
    # Parse resume
    parser = ResumeParser(args.input_file)
    parser.load_content()
    resume_data = parser.parse()
    
    # Generate HTML
    generator = ResumeGenerator(resume_data)
    html = generator.generate_html()
    
    # Write HTML to file
    with open(args.output, 'w') as f:
        f.write(html)
    
    logger.info(f"Resume HTML generated successfully: {args.output}")
    
    # Generate PDF if requested
    if args.pdf:
        if generate_pdf(args.output, args.pdf_output):
            logger.info(f"Resume PDF generated successfully: {args.pdf_output}")
        else:
            logger.error("PDF generation failed. You can manually create a PDF by opening the HTML file in a browser and printing to PDF.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
