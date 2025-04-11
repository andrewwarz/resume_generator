# Resume Parser

A Python tool that converts a plain text resume into beautifully formatted HTML and PDF documents.

## Quick Start Guide

### Prerequisites

#### Windows

1. **Install Python**:
   - Download the installer from [python.org](https://www.python.org/downloads/)
   - Run the installer
   - Check "Add Python to PATH" during installation
   - Click "Install Now"

2. **Verify Installation**:
   - Open Command Prompt (search for "cmd" in Start menu)
   - Type `python --version` and press Enter
   - You should see the Python version displayed

#### Linux/Ubuntu

1. **Install Python**:
   ```
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Verify Installation**:
   ```
   python3 --version
   ```

### Setup

1. **Download the Resume Parser Script**:
   - Save the `resume_parser.py` script to a folder of your choice

2. **Create a Virtual Environment**:
   - Open Command Prompt/Terminal
   - Navigate to your folder: `cd path/to/your/folder`
   - Create virtual environment:
     - Windows: `python -m venv venv`
     - Linux: `python3 -m venv venv`

3. **Activate Virtual Environment**:
   - Windows: `venv\Scripts\activate`
   - Linux: `source venv/bin/activate`

4. **Install Dependencies**:
   
   For PDF generation, choose one of these options:
   
   **Option 1 - WeasyPrint** (recommended for better CSS rendering):
   ```
   pip install weasyprint
   ```
   
   **Option 2 - PDFKit** (requires additional steps):
   ```
   pip install pdfkit
   ```
   
   Additional steps for PDFKit:
   - Windows: Download and install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)
   - Linux: `sudo apt install wkhtmltopdf`

### Usage

1. **Create Your Resume Text File**:
   - Create a plain text file (e.g., `my_resume.txt`)
   - Format your resume with clear section headings (SUMMARY, EXPERIENCE, EDUCATION, etc.)
   - Use bullet points with • symbol for lists

2. **Run the Parser**:
   - Make sure your virtual environment is activated
   - Basic usage:
     ```
     python resume_parser.py my_resume.txt
     ```
   
   - Generate HTML with custom filename:
     ```
     python resume_parser.py my_resume.txt -o my_custom_resume.html
     ```
   
   - Generate PDF:
     ```
     python resume_parser.py my_resume.txt --pdf
     ```
   
   - Generate both with custom filenames:
     ```
     python resume_parser.py my_resume.txt -o my_custom_resume.html --pdf --pdf-output my_custom_resume.pdf
     ```

3. **View the Results**:
   - Open the generated HTML file in your web browser
   - Open the PDF file with your PDF viewer

## Troubleshooting

- **"Command not found" errors**: Make sure your virtual environment is activated
- **PDF generation fails**: Try the alternative PDF library, or open the HTML in a browser and print to PDF
- **Missing section in output**: Check your text file formatting - section headers should be clearly marked
- **Contact info issues**: Make sure your email, phone, and location are on separate lines near the top

## Example Resume Format

```
Your Name

City, Country
email@example.com | 555-123-4567

SUMMARY

Your professional summary goes here...

EXPERIENCE

Company Name
Your Title
MM/YYYY - Present
• Achievement 1
• Achievement 2

EDUCATION

Degree, Institution, Year

SKILLS

Category:
Skill 1, Skill 2, Skill 3

CERTIFICATIONS

Provider
• Certification Name

HONORS AND AWARDS

Organization
• Award Name
```

## Using AI to Generate Resume Content

You can use AI language models (like ChatGPT, Claude, or other LLMs) to help create resume content that works perfectly with this parser.

### Quick Resume Generation with AI

1. **Copy the example format** from the end of this README

2. **Ask an AI assistant** to fill it in based on your needs:
   ```
   Please tailor a resume for me using this exact format:
   
   [PASTE THE EXAMPLE FORMAT HERE]
   
   Target this job posting: [PASTE JOB DESCRIPTION]
   
   Include these details about my experience: [YOUR EXPERIENCE]
   ```

3. **Copy the AI's response** and save it as a text file

4. **Run the resume parser** on this file to generate your formatted HTML/PDF resume

### Tips for Better AI-Generated Content

- Provide specific achievements with numbers when possible
- Ask for bullet points that follow the "accomplished X by doing Y, resulting in Z" format
- Request revisions for specific sections as needed
- Ask the AI to "make all bullet points start with strong action verbs"
- Include keywords from the job posting you're targeting

### Example Prompt

```
Please create a resume for me in the exact format below. I'm applying for a Senior Software Engineer position at a fintech company.

My experience includes:
- 5 years at TechCorp as a Software Engineer (2018-2023)
- 2 years at StartupX as a Junior Developer (2016-2018)
- Computer Science degree from State University (2016)
- Skills in Python, JavaScript, React, and AWS
- Certifications in AWS Solutions Architect and Scrum Master

Use the format exactly as shown:

[PASTE EXAMPLE FORMAT HERE]
```

### Customizing AI-Generated Content

After getting the AI response, you can:
1. Edit any details to better match your experience
2. Add more specific metrics and achievements 
3. Ensure all information is accurate before generating the final document
