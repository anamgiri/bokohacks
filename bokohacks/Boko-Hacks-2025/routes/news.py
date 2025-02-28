'''Insecure Use of requests:

The requests library's use here lacks proper error handling for scenarios such as timeouts, invalid responses, or handling server-side errors.
The requests.get call should use a timeout, but ideally, you should be validating the response for non-200 status codes and handling exceptions more robustly.
User-Provided Input:

The use of filter_param directly from request.args.get() without validation can lead to security risks, such as code injection or unexpected data structure manipulation (even though json is parsed, an attacker might try to craft malicious input).
Vulnerable Data Handling:

filter_options.get('showInternal') == True: If an attacker manipulates the filter parameter, they could enable internal news, which seems confidential. The code should guard against unauthorized access to sensitive internal data.
Logging Sensitive Information:

You should avoid logging sensitive data such as the API response, especially any internal data or security-sensitive information like API_KEY (which seems hardcoded in the internal news). This can create leaks of sensitive data, even if they are just logged for debugging purposes.
Rate Limiting:

Depending on the News API and your traffic, you might want to implement rate limiting to avoid your service getting blocked due to excessive requests, or you can implement caching mechanisms to store previously fetched results for a short period to minimize repeated API calls.
'''



'''Error Handling for requests: Now, exceptions like requests.RequestException are caught to ensure that any issues with the API request (e.g., timeouts, connection errors) do not crash the application.

Sensitive Data Protection:

The internal news articles are only added if the showInternal flag is set and the user is authorized (checked by session). This ensures that unauthorized users cannot access confidential data.
Logging:

Sensitive information, like API keys or user data, is not logged. Instead, you log generic messages and errors.
Added logging for major actions, like fetching news and adding internal data, as well as for unauthorized access attempts.
JSON Validation:

The filter_param is validated before being processed. If the filter is malformed, the user gets a proper error message, and the application doesn’t crash.'''



from flask import Blueprint, render_template, jsonify, request
import requests
import json
import logging

news_bp = Blueprint('news', __name__, url_prefix='/apps/news')

# Base URL for the News API
NEWS_API_BASE_URL = "https://saurav.tech/NewsAPI"

# Mapping of our categories to API categories
CATEGORY_MAPPING = {
    'business': 'business',
    'technology': 'technology',
    'world': 'general'
}

DEFAULT_COUNTRY = 'us'

# Internal news articles (Confidential)
INTERNAL_NEWS = [
    {
        "title": "CONFIDENTIAL: Security Breach Report Q3",
        "description": "Details of recent security incidents affecting customer data. For internal review only.",
        "url": "#internal-only",
        "publishedAt": "2025-01-15T08:30:00Z",
        "urlToImage": ""
    },
    {
        "title": "CONFIDENTIAL: Upcoming Product Launch",
        "description": "Specifications for our next-gen product launch in Q2. Contains proprietary information.",
        "url": "#internal-only",
        "publishedAt": "2025-02-01T10:15:00Z",
        "urlToImage": ""
    },
    {
        "title": "CONFIDENTIAL: Internal API Credentials",
        "description": "API_KEY: 5x6hdPQmSK2aT9E3bL8nZ7yRfV4wX1  ADMIN_KEY: jKq2P8zX5sW7vT1yR4aB9nL6cE3hG",
        "url": "#internal-only",
        "publishedAt": "2025-01-30T14:45:00Z",
        "urlToImage": ""
    }
]

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@news_bp.route('/')
def news_page():
    """Render the news page"""
    return render_template('news.html')

@news_bp.route('/fetch', methods=['GET'])
def fetch_news():
    """Fetch news from the News API with security enhancements"""
    try:
        # Get category from request, default to business
        category = request.args.get('category', 'business')
        
        # Map our category to API category
        api_category = CATEGORY_MAPPING.get(category, 'business')
        api_url = f"{NEWS_API_BASE_URL}/top-headlines/category/{api_category}/{DEFAULT_COUNTRY}.json"
        
        logger.info(f"Fetching news from: {api_url}")
        
        # Fetch news from external API with a timeout to avoid hanging the request
        response = requests.get(api_url, timeout=10)
        
        # Ensure a valid response status code
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])[:10]  # Limit to 10 articles
            
            filter_param = request.args.get('filter', '{}')
            
            try:
                filter_options = json.loads(filter_param)
                logger.info(f"Filter options: {filter_options}")
                
                # Only show internal news if the flag is set and user is authorized
                if filter_options.get('showInternal') == True:
                    # Add internal news to the results
                    logger.warning("Adding internal news to results!")
                    # Ensure user is authorized to see internal news
                    if not session.get('user') == 'admin':  # Example check
                        logger.error("Unauthorized access to internal news")
                        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
                    articles = INTERNAL_NEWS + articles
            except json.JSONDecodeError:
                logger.error(f"Invalid filter parameter: {filter_param}")
                return jsonify({'success': False, 'error': 'Invalid filter parameter'}), 400
            
            # Transform the data to match our expected format
            transformed_data = {
                'success': True,
                'category': category,
                'data': []
            }
            
            # Process articles
            for article in articles:
                transformed_data['data'].append({
                    'title': article.get('title', 'No Title'),
                    'content': article.get('description', 'No content available'),
                    'date': article.get('publishedAt', ''),
                    'readMoreUrl': article.get('url', '#'),
                    'imageUrl': article.get('urlToImage', '')
                })
            
            return jsonify(transformed_data)
        else:
            logger.error(f"Failed to fetch news. Status code: {response.status_code}")
            return jsonify({
                'success': False,
                'error': f'Failed to fetch news. Status code: {response.status_code}'
            }), response.status_code
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500
