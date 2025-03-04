# Grocery-Price-Aggregator

Every week, I found myself hopping between Woolworths Supermarkets, Coles Group, and IGA Supermarkets tabs just to get the best grocery deals. It was tedious.

My Grocery Price Aggregator scrapes multiple Australian supermarket websites, compares prices, and even emails me a summary of the cheapest options: no more juggling tabs or missing sales.

Python + FastAPI: Manages data collection and external API calls.
Cookie Management: Some supermarkets block scrapers easily. I handle session cookies so I can fetch real-time data without constant captchas.
Deepseek (via Ollama): This is the AI “brain” that interprets my CSV data and figures out which store offers the best value, factoring in weight-based cost (like price per 100g). Model: “deepseek-r1, 7b” specialized in reasoning tasks. It doesn’t just do a simple numeric sort, it understands product descriptions to handle near-matches or ambiguous entries.

Why Use an LLM?
I needed more than simple numeric sorting. If multiple product entries are similar (e.g., “milk” with different packaging sizes), the LLM uses natural language understanding to detect near-matches. It also computes price-per-unit (when weights are provided) so you can really see where you’re getting the best deal.

Why Ollama?
I can run LLMs on my own machine, data never leaves my local environment. This is huge for data privacy and cost control. No giant cloud fees or sending sensitive user queries off to a remote service.

I’m not just sorting numeric fields, I’m getting contextual intelligence about each grocery item. That transforms a basic “lowest price” script into a more human-like decision-maker, which is especially helpful when dealing with ambiguous product listings.
