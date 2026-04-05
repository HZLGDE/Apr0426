from langchain.tools import tool
import httpx
from pydantic import BaseModel, Field

@tool
def fetch_quote(count:int = 1)->dict:
    '''
    Fetch inspirational quotes from ZenQuotes API.
    
    Args:
        count: Number of quotes to retrieve (1-50)
    
    Returns:
        List of dicts with quote and author keys
    '''

    try:
        client = httpx.Client(timeout=10.0)
        url=f'https://zenquotes.io/api/quotes?count={min(count,50)}'
        response = client.get(url=url)
        response.raise_for_status()
        data = response.json()
        quotes =[]
        for d in data:
            q = {
                'quote': d.get('q',None),
                'author': d.get('a',None)
            }
            quotes.append(q)
        return quotes
    except Exception as e:
        return f'Error: {e}'

qtools = [fetch_quote]

if __name__ == '__main__':
    quote = fetch_quote()
    print(quote)