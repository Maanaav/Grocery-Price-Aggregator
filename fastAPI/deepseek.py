from ollama import chat, ChatResponse
import re

import csv


def extract_error_info_from_csv(filename):
    """
    Reads a CSV file and accumulates rows where the 'price' column contains
    'not found ERROR'. Returns a string with store and product information.
    """
    all_info = ""
    try:
        with open(filename, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'Not found ERROR' in row['price']:
                    store = row.get('store_name', 'Unknown Store')
                    product = row.get('product_name', 'Unknown Product')
                    all_info += f"Could search for: store name: {store}, product names: {product}\n"
    except Exception as e:
        print("error in extract_error_info_from_csv")
        print(e)

    return all_info


def ollama_deepseek(grocery_list: list[str]):
    filename = 'grocery_prices.csv'

    # Read the CSV file containing grocery store data
    with open(filename, 'r') as file:
        csv_content = file.read()

    print("CSV Content:")
    print(csv_content)

    # Construct the prompt to instruct Deepseek
    prompt = f"""
    Below is CSV data with grocery store information. The CSV columns are:
    store_name, product_name, price
    
    CSV data:
    {csv_content}
    
    I have the following grocery items to buy today:
    {', '.join(grocery_list)}
    
    For each item, please perform the following steps:
    1. Search for rows where the product_name contains the search item (case-insensitive) doesn't have to be exact.
    2. If multiple matches exist, compare the prices (ignoring any rows where the price is missing or invalid). Additionally, if the product name includes weight information, extract the weight, convert it to a common unit (grams), and compute the price per unit weight. Choose the option with the lowest price per unit weight if weight details are available.
    3. If an exact match is found, label it as "Exact match". If not but a similar product is available, label it as "Similar match".
    4. If no matching or similar product is found, indicate that the item is not available.
    
    For each grocery item, provide:
    - The item name.
    - The match type ("Exact match", "Similar match", or "Not available").
    - The store name.
    - The price, and if applicable, the computed price per unit weight.
    
    Please format the output as a neat, human-readable grocery list.
    
    Double-check the CSV data and ensure that you pick the cheapest valid option for each item.
    """

    # Send the prompt to Deepseek and get the response
    response: ChatResponse = chat(model='deepseek-r1', messages=[{'role': 'user', 'content': prompt}])

    # Extract everything inside <think>...</think>
    think_texts = re.findall(r'<think>(.*?)</think>', response.message.content, flags=re.DOTALL)
    # Join extracted sections (optional, if multiple <think> sections exist)
    think_texts = "\n\n".join(think_texts).strip()
    print(think_texts)

    # Exclude the Deep Think, and return the response
    clean_response = re.sub(r'<think>.*?</think>', '', response.message.content, flags=re.DOTALL).strip()
    # Always remove the last line
    clean_response_lines = clean_response.split('\n')
    if clean_response_lines:
        clean_response_lines = clean_response_lines[:-1]
    clean_response = "\n".join(clean_response_lines)

    error_response = extract_error_info_from_csv(filename)

    final_result = clean_response + "\n\n" + error_response

    # Print the formatted grocery list from Deepseek
    print("\nGrocery List:")
    print(final_result)
    return final_result
