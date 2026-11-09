import requests

url = "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/80/Anggota_DPR_Puti_Guntur_Soekarno_%28cropped%29_%28cropped%29.jpg/250px-Anggota_DPR_Puti_Guntur_Soekarno_%28cropped%29_%28cropped%29.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail"

# Fetch the image from the URL
# resp = requests.get(
#             url,
#             timeout=15,
#             headers={"User-Agent": "spider/1.0 (learning project)"},
#         )
# resp.raise_for_status()  # Make sure the request didn't fail

# Save the image bytes to disk
# (fetch the whole image into memory at once)
# with open("image.jpg", "wb") as f:
#     f.write(resp.content)

# Alternative approach: streaming
# (useful for larger images)
resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "spider/1.0 (learning project)"},
        )
with resp:
    resp.raise_for_status()

    with open("large-image.jpg", "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)