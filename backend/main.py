from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import openai
from typing import Optional, List

app = FastAPI()

# Set OpenAI API Key directly (use environment variable in production)
openai.api_key = ''

# SMTP configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'sheyamg2003@gmail.com'
SMTP_PASSWORD = ''

class ProspectInfo(BaseModel):
    name: str
    company: str
    additional_info: Optional[str] = None

class EmailContent(BaseModel):
    prospect_summary: str
    product_catalog: str  
    draft_email: Optional[str] = None

email_temp = "Subject: Unlock Amazing Discounts Just for You! Hi Customer, I hope this message finds you well! I wanted to reach out because we have amazing discounts on our premium products such as the Premium Running Shoes and the Smart Fitness Tracker, which I think you would love. We observed that the Smart Fitness Tracker suits your fitness goals perfectly, providing real-time tracking of your activities. Our products not only promise quality but also ensure you get the best value for your investment. I’d love to discuss how our offerings can fit into your lifestyle. Would you be available for a quick chat this week? Let me know what time works for you!Best regards"

@app.post("/research_prospect/")
async def research_prospect(prospect: ProspectInfo):
    try:
        search_query = f"{prospect.name} {prospect.company}"
        url = f"https://www.google.com/search?q={search_query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = [result.get_text() for result in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd')]
        return {"search_results": search_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {e}")

def read_product_catalog(filename):
    products = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split(":")
            if len(parts) == 2:
                product_name = parts[0].strip()
                short_description = parts[1].strip()
                products.append({"Name": product_name, "Short description": short_description})
    return products

# Load product catalog (update path as needed)
products = read_product_catalog("C:/Users/sakth/Downloads/sdr_ai_system/data/product_catalog.txt")

def generate_email_prompt(info: dict) -> str:
    prompt = """Your goal is to write a personalized outbound email from {sales_rep}, a sales rep at {company} to {prospect}.
A good email is personalized and informs the customer on how your product can help the customer.
Be sure to use value selling: A sales methodology that focuses on how your product or service will provide value to the customer instead of focusing on price or solution.
% INFORMATION ABOUT {company}:
A fashion and apparel company
products list:
{products_info}

% INFORMATION ABOUT {prospect}:
{text}

% INCLUDE THE FOLLOWING PIECES IN YOUR RESPONSE:
- Start the email with the sentence: "We have amazing discounts on our premium products such as ..." then insert the description of the product.
- The sentence: "We observed that XYZ product suits your taste." Replace XYZ with one of the products.
- A 1-2 sentence description about the products; be brief.
- End your email with a call-to-action, such as asking them to set up time to talk more.

% YOUR RESPONSE:"""

    for key in info.keys():
        prompt = prompt.replace("{" + key + "}", info[key])
    return prompt

@app.post("/generate_email/")
async def generate_email(content: EmailContent):
    try:
        info = {
            'company': "XYZ",
            'sales_rep': "ABC",
            'prospect': content.prospect_summary,
            'text': "Your role or title here",
            'products_info': "\n".join(
                [f"{i+1}. {product['Name']}: {product['Short description']}" for i, product in enumerate(products[:5])]
            )
        }
        prompt = generate_email_prompt(info)

        return {"email": email_temp}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {e}")


@app.post("/send_email/")
async def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        return {"status": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")

@app.post("/monitor_replies/")
async def monitor_replies():
    # This function can be implemented to check for replies and generate contextual responses
    pass
