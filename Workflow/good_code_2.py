import http.client
import json
import os
import struct
import sys
import unicodedata
import time
import urllib.parse
import urllib.request
from http.cookies import SimpleCookie

# Third-party SVG conversion
cairosvg_installed = False
try:
    from cairosvg import svg2png
    cairosvg_installed = True
except ImportError:
    pass

from payload import Payload
from searchresult import SearchResult

# Constants
SEARCH_LIMIT = 9
REQUEST_TIMEOUT = 10  # seconds

# Configuration from environment variables
try:
    NOTION_SPACE_ID = os.environ['notionSpaceId']
    RAW_COOKIE = os.environ['cookie']
    USE_DESKTOP_CLIENT = os.environ.get('useDesktopClient', '0') == "1"
    IS_NAVIGABLE_ONLY = os.environ.get('isNavigableOnly', '0') == "1"
    ENABLE_ICONS = os.environ.get('enableIcons', '0') == "1"
    SHOW_RECENTLY_VIEWED = os.environ.get('showRecentlyViewedPages', '0') == "1"
    ICON_CACHE_DAYS = sorted([0, int(os.environ.get('iconCacheDays', '7')), 365])[1]
    # Get Alfred's cache directory for this workflow
    CACHE_DIR = os.environ.get('alfred_workflow_cache', './icons')
except KeyError as e:
    print(json.dumps({
        "items": [{
            "title": "Configuration Error",
            "subtitle": f"Missing required environment variable: {e}",
            "valid": False,
            "icon": {"path": "Empty.png"}
        }]
    }))
    sys.exit(1)

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True, mode=0o755)
# Create icons subdirectory within cache
ICONS_DIR = os.path.join(CACHE_DIR, 'icons')
os.makedirs(ICONS_DIR, exist_ok=True, mode=0o755)

# Extract essential cookies with fallbacks
def parse_essential_cookies(cookie_str):
    """Extract only necessary cookies (token_v2 and notion_user_id) from cookie string"""
    cookie = SimpleCookie()
    cookie.load(cookie_str)
    
    essential = {}
    
    token = cookie.get('token_v2')
    notion_id = cookie.get('notion_user_id')
    
    essential['token_v2'] = token.value if token else ''
    essential['notion_user_id'] = notion_id.value if notion_id else ''
    
    return essential

# Get essential cookies once at startup
ESSENTIAL_COOKIES = parse_essential_cookies(RAW_COOKIE)
missing_cookies = []
if not ESSENTIAL_COOKIES.get('token_v2'):
    missing_cookies.append("'token_v2'")
if not ESSENTIAL_COOKIES.get('notion_user_id'):
    missing_cookies.append("'notion_user_id'")

if missing_cookies:
    print(json.dumps({
        "items": [{
            "title": "Configuration Error",
            "subtitle": f"Missing required cookie(s): {', '.join(missing_cookies)}",
            "valid": False,
            "icon": {"path": "Empty.png"}
        }]
    }))
    sys.exit(1)

COOKIE_HEADER = f"token_v2={ESSENTIAL_COOKIES['token_v2']}; notion_user_id={ESSENTIAL_COOKIES['notion_user_id']}"

exception = ""

def build_notion_search_query_data(query_string):
    """Construct the search query payload for Notion API"""
    return json.dumps({
        "type": "BlocksInSpace",
        "query": query_string,
        "spaceId": NOTION_SPACE_ID,
        "limit": SEARCH_LIMIT,
        "filters": {
            "isDeletedOnly": False,
            "excludeTemplates": False,
            "isNavigableOnly": IS_NAVIGABLE_ONLY,
            "navigableBlockContentOnly": IS_NAVIGABLE_ONLY,
            "requireEditPermissions": False,
            "ancestors": [],
            "createdBy": [],
            "editedBy": [],
            "lastEditedTime": {},
            "createdTime": {}
        },
        "sort": {"field": "relevance"},
        "source": "quick_find_input_change"
    })

def build_notion_recent_visits_query(user_id):
    """Construct the recent page visits query payload"""
    return json.dumps({
        "userId": user_id,
        "spaceId": NOTION_SPACE_ID,
        "limit": SEARCH_LIMIT
    })

def get_notion_url():
    """Return the appropriate Notion URL based on configuration"""
    return "notion://www.notion.so/" if USE_DESKTOP_CLIENT else "https://www.notion.so/"

def decode_emoji(emoji):
    """Convert emoji to hexadecimal codepoints for icon matching"""
    if not emoji:
        return None
    
    try:
        b = emoji.encode('utf_32_le')
        count = len(b) // 4
        if count > 10:  # Sanity check for valid emoji
            return None
        cp = struct.unpack(f'<{count}I', b)
        return [hex(x)[2:] for x in cp]
    except UnicodeEncodeError:
        return None

def download_icon(search_result_id, image_url):
    """
    Download and cache icon from Notion
    Returns path to cached file or None if unavailable
    """
    if not image_url:
        return None
        
    # Construct proper download URL
    if not image_url.startswith("https://www.notion.so"):
        image_url = f"https://www.notion.so/image/{urllib.parse.quote(image_url, safe='')}?table=block&id={search_result_id}&width=120&cache=v2"
    
    # Extract filename from URL
    parsed_url = urllib.parse.urlparse(image_url)
    filename = os.path.basename(parsed_url.path)
    file_ext = os.path.splitext(filename)[1][1:] if os.path.splitext(filename)[1] else "png"  # Without dot
    cache_file = os.path.join(ICONS_DIR, f"{search_result_id}_{filename}")

    # Check cache validity
    if os.path.isfile(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < ICON_CACHE_DAYS * 86400:
            return convert_svg_to_png(cache_file) if file_ext == "svg" else cache_file

    # Download fresh icon using urllib to handle redirects
    try:
        # Create opener with cookies
        opener = urllib.request.build_opener()
        opener.addheaders = [('Cookie', COOKIE_HEADER)]
        urllib.request.install_opener(opener)
        
        # Download with redirect handling
        response = urllib.request.urlopen(image_url, timeout=REQUEST_TIMEOUT)
        
        # urllib.request.urlopen returns a response with getcode() method instead of status attribute
        with open(cache_file, 'wb') as f:
            f.write(response.read())
        return convert_svg_to_png(cache_file) if file_ext == "svg" else cache_file
    except Exception as e:
        return None

def convert_svg_to_png(svg_path):
    """Convert SVG to PNG using cairosvg if available"""
    if not cairosvg_installed:
        return svg_path  # Return SVG path as fallback if conversion not available
    
    png_path = svg_path.rsplit('.', 1)[0] + '.png'
    try:
        svg2png(url=svg_path, write_to=png_path, output_width=200, output_height=200)
        return png_path
    except Exception:
        return svg_path  # Return original SVG path on error

def get_icon_path(search_result_id, notion_icon):
    """Resolve icon path from Notion's icon representation"""
    if not notion_icon:
        return None
        
    # Handle emoji icons
    hex_codes = decode_emoji(notion_icon)
    if hex_codes:
        codepoints = '_'.join(hex_codes)
        emoji_path = f"emojiicons/{codepoints}.png"
        if os.path.isfile(emoji_path):
            return emoji_path
        # Try simplified versions for compound emojis
        while '_' in codepoints:
            codepoints = codepoints.rsplit('_', 1)[0]
            emoji_path = f"emojiicons/{codepoints}.png"
            if os.path.isfile(emoji_path):
                return emoji_path
        return None
    
    # Handle URL-based icons
    return download_icon(search_result_id, notion_icon)

def create_subtitle_chain(record_map, block_id):
    """Create breadcrumb-style subtitle from parent hierarchy"""
    hierarchy = []
    current_id = block_id
    
    for _ in range(10):  # Prevent infinite loops
        block = record_map.get('block', {}).get(current_id, {}).get('value', {})
        if not block:
            break
        
        # Add current level title
        if block.get('parent_table') == 'block':
            hierarchy.append(block.get('properties', {}).get('title', [['Untitled']])[0][0])
        
        # Move up hierarchy
        current_id = block.get('parent_id')
        if block.get('parent_table') != 'block':
            break
    
    return ' / '.join(reversed(hierarchy)) if hierarchy else ''

def make_notion_request(endpoint, payload):
    """Make a request to the Notion API with error handling"""
    try:
        conn = http.client.HTTPSConnection("www.notion.so", timeout=REQUEST_TIMEOUT)
        conn.request("POST", endpoint,
                    payload,
                    headers={"Content-Type": "application/json", "Cookie": COOKIE_HEADER})
        
        response = conn.getresponse()
        if response.status != 200:
            return None, f"HTTP Error {response.status}: {response.reason}"
        
        return Payload(response.read()), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)}"

# Main execution flow
if __name__ == "__main__":
    # Normalize and parse input query
    alfred_query = unicodedata.normalize('NFC', sys.argv[1]) if len(sys.argv) > 1 else ""
    search_results = []
    notion_url = get_notion_url()

    try:
        if not alfred_query.strip() and SHOW_RECENTLY_VIEWED and ESSENTIAL_COOKIES['notion_user_id']:
            # Fetch recently visited pages
            result, error = make_notion_request(
                "/api/v3/getRecentPageVisits", 
                build_notion_recent_visits_query(ESSENTIAL_COOKIES['notion_user_id'])
            )
            
            if error:
                exception = error
            elif result and hasattr(result, 'pages'):
                for page in result.pages:
                    sr = SearchResult(page['id'])
                    sr.title = page.get('name', 'Untitled')
                    sr.subtitle = create_subtitle_chain(result.recordMap, sr.id)
                    sr.link = f"{notion_url}{sr.id.replace('-', '')}"
                    
                    if ENABLE_ICONS:
                        sr.icon = get_icon_path(sr.id, page.get('iconEmoji') or page.get('fullIconUrl'))
                    
                    search_results.append(sr)
        else:
            # Perform regular search
            result, error = make_notion_request(
                "/api/v3/search",
                build_notion_search_query_data(alfred_query)
            )
            
            if error:
                exception = error
            elif result and hasattr(result, 'results'):
                for item in result.results:
                    sr = SearchResult(item['id'])
                    block_data = result.recordMap.get('block', {}).get(sr.id, {}).get('value', {})
                    if not block_data:
                        continue
                    
                    # Determine title
                    collection_id = block_data.get('collection_id')
                    if collection_id and 'collection' in result.recordMap and collection_id in result.recordMap['collection']:
                        collection = result.recordMap['collection'][collection_id]
                        sr.title = collection['value']['name'][0][0]
                    else:
                        sr.title = block_data.get('properties', {}).get('title', [['Untitled']])[0][0]
                    
                    sr.subtitle = create_subtitle_chain(result.recordMap, sr.id)
                    sr.link = f"{notion_url}{sr.id.replace('-', '')}"
                    
                    if ENABLE_ICONS and 'format' in block_data:
                        icon = block_data['format'].get('page_icon')
                        sr.icon = get_icon_path(sr.id, icon) if icon else None
                    
                    search_results.append(sr)
                
    except Exception as e:
        exception = f"{type(e).__name__}: {str(e)}"

    # Build Alfred output
    output_items = []
    for result in search_results:
        output_items.append({
            "title": result.title,
            "subtitle": result.subtitle,
            "arg": result.link,
            "icon": {"path": result.icon} if result.icon else {"path": "Empty.png"},
            "autocomplete": result.title
        })

    if exception:
        output_items.insert(0, {
            "title": "Error occurred",
            "subtitle": exception,
            "valid": False,
            "icon": {"path": "Empty.png"}
        })

    if not output_items:
        output_items.append({
            "title": "Open Notion",
            "subtitle": "No results found or empty query",
            "arg": notion_url
        })

    print(json.dumps({"items": output_items}))