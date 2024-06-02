import requests
import app
from linebot.models import *
import urllib.parse

def get_googledata(latitude, longitude, google_maps_apikey, activity):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1000&type={activity}&language=zh-TW&key={google_maps_apikey}"
    response = requests.get(url)
    results = response.json().get('results', [])

    columns = []
    for result in results[:10]:  # Show up to 10 results
        name = result.get('name')
        address = result.get('vicinity')
        rating = result.get('rating', 'N/A')
        place_id = result.get('place_id')

        encoded_name = urllib.parse.quote(name)
        maps_url = f"https://www.google.com/maps/place/?q={encoded_name}"
        
        photo_reference = result.get('photos', [{}])[0].get('photo_reference')
        if photo_reference:
            thumbnail_image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={google_maps_apikey}"
        else:
            thumbnail_image_url = "https://via.placeholder.com/800x400?text=No+Image"

        column = CarouselColumn(
            thumbnail_image_url=thumbnail_image_url,
            title=name,
            text=f"評分: {rating}\n地址：{address}",
            actions=[
                {
                    "type": "uri",
                    "label": "View on Map",
                    "uri": maps_url
                }
            ]
        )
        columns.append(column)
    
    carousel_template = CarouselTemplate(columns=columns)
    template_message = TemplateSendMessage(alt_text=f'Nearby {activity}', template = carousel_template)

    return template_message

