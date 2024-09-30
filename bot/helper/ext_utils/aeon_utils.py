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
            # Search for the movie/TV show using the multi-search endpoint
            async with session.get(tmdb_search_url) as search_response:
                search_data = await search_response.json()

                if search_data['results']:
                    # Filter results based on release year and first air date
                    matching_results = [
                        result for result in search_data['results']
                        if ('release_date' in result and result['release_date'][:4] == str(release_year)) or
                           ('first_air_date' in result and result['first_air_date'][:4] == str(release_year))
                    ]

                    if matching_results:
                        result = matching_results[0]
                        #movie_id = result['id']
                        #media_type = result['media_type']

                        # Fetch images from the movie/TV show using the /images endpoint
                        # Include no language poster by passing 'null' in include_image_language
                        #tmdb_movie_image_url = f'https://api.themoviedb.org/3/{media_type}/{movie_id}/images?api_key={TMDB_API_KEY}&include_image_language=null'

                        #async with session.get(tmdb_movie_image_url) as movie_response:
                            #movie_images = await movie_response.json()

                            # Check if posters exist in the image results
                            #if 'posters' in movie_images and movie_images['posters']:
                                # Use the first available poster (including no-language posters)
                                #poster_path = movie_images['posters'][0]['file_path']
                                #poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
                                #return poster_url

                        # Fallback: Use the poster_path from the search result
                        if 'poster_path' in result and result['poster_path']:
                            poster_path = result['poster_path']
                            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
                            return poster_url
                        else:
                            LOGGER.info("No Poster Found")
                    else:
                        LOGGER.info(f"No matching results found for {movie_name} ({release_year}).")

    except aiohttp.ClientError as e:
        print(f"Network error while fetching TMDB data: {e}")
    except Exception as e:
        print(f"Error fetching TMDB data: {e}")

    return None
