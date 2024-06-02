import requests
import app
from linebot.models import *
import urllib.parse

def get_googledata(latitude, longitude, google_maps_apikey, activity):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=1000&type={activity}&language=zh-TW&key={google_maps_apikey}"
    response = requests.get(url)
    results = response.json().get('results', [])

    columns = []
    places_data = []
    for result in results[:10]:  # Show up to 10 results
        name = result.get('name')
        if len(name) > 40:
            name = name[:37] + '...'
        address = result.get('vicinity')
        rating = result.get('rating', 'N/A')
        place_id = result.get('place_id')
        places_data.append({
            'name': name,
            'address': address,
            'rating': rating,
            'place_id': place_id,
            'photos': result.get('photos', [{}])
        })

    gpt_input = "請幫我查月以下地點的評論，並返回10個最好的地點：\n"
    for place in places_data:
        gpt_input += f"名稱: {place['name']}, 地址: {place['address']}, 評分: {place['rating']}\n"
    
    gpt_reply = app.gpt35_message(gpt_input)

    sorted_places_data = parse_gpt_reply(gpt_reply, places_data)

    for place in sorted_places_data:
        name = place['name']
        address = place['address']
        rating = place['rating']
        photos = place['photos']

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

def parse_gpt_reply(gpt_reply, places_data):
    # 解析 GPT-4 的回复并排序 places_data
    # 假设 GPT-4 的回复格式为按顺序的地点名称列表
    place_names = gpt_reply.split('\n')
    sorted_places_data = []
    for name in place_names:
        for place in places_data:
            if place['name'] in name:
                sorted_places_data.append(place)
                break
    return sorted_places_data