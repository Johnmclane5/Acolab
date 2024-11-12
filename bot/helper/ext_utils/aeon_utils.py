import re
import aiohttp
import pyshorteners
from bot import LOGGER, config_dict

def tinyfy(long_url):
    s = pyshorteners.Shortener()
    try:
        short_url = s.clckru.short(long_url)
        LOGGER.info(f'tinyfied {long_url} to {short_url}')
        return short_url
    except Exception:
        LOGGER.error(f'Failed to shorten URL: {long_url}')
        return long_url

async def extract_movie_info(caption):
    try:
        regex = re.compile(r'(.+?)(\d{4})')
        match = regex.search(caption)

        if match:
             movie_name = match.group(1).replace('.', ' ').strip()
             release_year = match.group(2)
             return movie_name, release_year
    except Exception as e:
        print(e)
    return None, None
    
async def get_movie_poster(movie_name, release_year):
    TMDB_API_KEY = config_dict['TMDB_API_KEY']
    tmdb_search_url = f'https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={movie_name}'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(tmdb_search_url) as search_response:
                search_data = await search_response.json()

                if search_data['results']:
                    # Filter results based on release year and first air date
                    matching_results = [
                        result for result in search_data['results']
                        if ('release_date' in result and result['release_date'][:4] == str(release_year)) or
                        ('first_air_date' in result and result['first_air_date'][:4] == str(
                            release_year))
                    ]

                    if matching_results:
                        result = matching_results[0]

                        # Fetch additional details using movie ID
                        movie_id = result['id']
                        media_type = result['media_type']

                        tmdb_movie_image_url = f'https://api.themoviedb.org/3/{media_type}/{movie_id}/images?api_key={TMDB_API_KEY}&language=en-US&include_image_language=en,hi'

                        async with session.get(tmdb_movie_image_url) as movie_response:
                            movie_images = await movie_response.json()
 
                        # Use the backdrop_path or poster_path
                            poster_path = None                                                        
                            if 'backdrop_path' in result and result['backdrop_path']:
                                poster_path = result['backdrop_path']

                            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
                            return poster_url

    except Exception as e:
        print(f"Error fetching TMDB data: {e}")

    return None
