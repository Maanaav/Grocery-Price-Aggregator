from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from config import settings
import csv
import smtplib
from email.message import EmailMessage

from deepseek import ollama_deepseek
from scrape import search_woolworths_api, search_coles_api, search_iga_api

app = FastAPI()

origins = ["*"] # Allow cross-origin from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
def search(term: str):
    """
    Forward the search term to Woolworths' suggestions API
    and return the response to our frontend.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/133.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.woolworths.com.au/",
        # "Cookie": user_cookie,
    }

    # Woolworths suggestion URL
    url = (
        "https://www.woolworths.com.au/apis/ui/search-suggestions/"
        f"suggestionsb2c?searchTerm={term}"
    )

    try:
        response = requests.get(url, headers=headers)

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            return {
                "error": "Failed to fetch suggestions from Woolworths",
                "status_code": response.status_code,
                "details": response.text,
            }

        return response.json()

    except requests.RequestException as e:
        return {
            "error": "An exception occurred while trying to fetch suggestions",
            "details": str(e),
        }


@app.post("/submit")
def submit_grocery_list(grocery_list: list[str]):
    print("Received Grocery List:", grocery_list)
    output_file = "grocery_prices.csv"
    fieldnames = ["store_name", "product_name", "price"]

    # Load cookies from configuration
    woolworths_cookie = settings.woolworths_cookie
    coles_cookie = settings.coles_cookie
    iga_cookie = settings.iga_cookie

    # Open CSV file for writing
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in grocery_list:
            woolworths_results = search_woolworths_api(item, woolworths_cookie)
            coles_results = search_coles_api(item, coles_cookie)
            iga_results = search_iga_api(item, iga_cookie)

            # Write results to CSV
            for result in (woolworths_results + coles_results + iga_results):
                writer.writerow(result)

    call_llm(grocery_list)

    return {f"Scraping completed. Data saved in {output_file}"}


@app.post("/deepseek")
def call_llm(grocery_list: list[str]):
    result = ollama_deepseek(grocery_list)

    # Compose the email.
    msg = EmailMessage()
    msg.set_content(result)
    msg['Subject'] = 'Your Grocery List'
    msg['From'] = "your_email@gmail.com"  # Replace with your Gmail address.
    msg['To'] = settings.receiver_email  # Replace with the recipient's email address.

    try:
        # Connect to Gmail's SMTP server using SSL.
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            # Login to your Gmail account.
            smtp.login(settings.sender_email, settings.sender_password)
            # Send the email.
            smtp.send_message(msg)
    except Exception as e:
        print(f"error: {str(e)}")
        # Handle any errors that occur during the email sending.
        return {"error": str(e)}

    return {"message": "Email sent successfully."}
