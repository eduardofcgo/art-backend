"""
Controller for popular artworks endpoint.
"""

import logging
from typing import List, Dict, Any
from litestar import Response, get
from litestar.status_codes import HTTP_200_OK
from litestar.params import Dependency
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PopularArtwork:
    """Data structure for popular artwork information."""
    
    title: str
    description: str
    image_url: str
    style: str
    artist: str
    year: str


@get("/popular-artworks", name="get_popular_artworks")
async def get_popular_artworks() -> Response:
    """
    Endpoint to retrieve a list of popular artworks from various art styles.
    
    Returns: JSON array with popular artwork metadata including title, description, and image_url
    """
    logger.info("Received popular artworks request")
    
    # Predefined list of popular artworks from different styles
    popular_artworks = [
        PopularArtwork(
            title="The Starry Night",
            description="A famous painting by Vincent van Gogh depicting a swirling night sky over a village. This masterpiece showcases van Gogh's unique post-impressionist style with bold brushstrokes and vibrant colors.",
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
            style="Post-Impressionism",
            artist="Vincent van Gogh",
            year="1889"
        ),
        PopularArtwork(
            title="Mona Lisa",
            description="The world's most famous portrait by Leonardo da Vinci, known for her enigmatic smile. This Renaissance masterpiece demonstrates da Vinci's mastery of sfumato technique and psychological depth.",
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/687px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
            style="Renaissance",
            artist="Leonardo da Vinci",
            year="1503-1519"
        ),
        PopularArtwork(
            title="The Scream",
            description="An iconic expressionist painting by Edvard Munch depicting a figure with an agonized expression against a blood-red sky. This work represents the anxiety of modern life and is one of the most recognizable images in art history.",
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/1280px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
            style="Expressionism",
            artist="Edvard Munch",
            year="1893"
        ),
        PopularArtwork(
            title="Guernica",
            description="A powerful anti-war painting by Pablo Picasso depicting the bombing of Guernica during the Spanish Civil War. This cubist masterpiece uses monochromatic colors and fragmented forms to convey the horrors of war.",
            image_url="https://upload.wikimedia.org/wikipedia/en/thumb/7/74/PicassoGuernica.jpg/1280px-PicassoGuernica.jpg",
            style="Cubism",
            artist="Pablo Picasso",
            year="1937"
        ),
        PopularArtwork(
            title="Water Lilies",
            description="A series of impressionist paintings by Claude Monet depicting his water lily pond at Giverny. These works represent Monet's fascination with light, reflection, and the changing effects of nature.",
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Claude_Monet_-_Water_Lilies_-_1919%2C_Metropolitan_Museum_of_Art.jpg/1280px-Claude_Monet_-_Water_Lilies_-_1919%2C_Metropolitan_Museum_of_Art.jpg",
            style="Impressionism",
            artist="Claude Monet",
            year="1919"
        ),
        PopularArtwork(
            title="The Persistence of Memory",
            description="A surrealist masterpiece by Salvador Dalí featuring melting clocks in a dreamlike landscape. This painting explores themes of time, memory, and the subconscious mind through Dalí's unique surrealist vision.",
            image_url="https://upload.wikimedia.org/wikipedia/en/thumb/d/dd/The_Persistence_of_Memory.jpg/1280px-The_Persistence_of_Memory.jpg",
            style="Surrealism",
            artist="Salvador Dalí",
            year="1931"
        ),
        PopularArtwork(
            title="The Birth of Venus",
            description="A Renaissance masterpiece by Sandro Botticelli depicting the goddess Venus emerging from the sea. This painting exemplifies the classical beauty and mythological themes characteristic of the Italian Renaissance.",
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg/1280px-Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg",
            style="Renaissance",
            artist="Sandro Botticelli",
            year="1485"
        ),
        PopularArtwork(
            title="Composition VII",
            description="An abstract painting by Wassily Kandinsky that represents a breakthrough in non-representational art. This work demonstrates Kandinsky's theory of spiritual art and the power of color and form to express emotion.",
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Vassily_Kandinsky%2C_1913_-_Composition_7.jpg/1280px-Vassily_Kandinsky%2C_1913_-_Composition_7.jpg",
            style="Abstract Art",
            artist="Wassily Kandinsky",
            year="1913"
        )
    ]
    
    # Convert to response format
    artworks_data = []
    for artwork in popular_artworks:
        artworks_data.append({
            "title": artwork.title,
            "description": artwork.description,
            "image_url": artwork.image_url,
            "style": artwork.style,
            "artist": artwork.artist,
            "year": artwork.year
        })
    
    logger.info(f"Successfully retrieved {len(artworks_data)} popular artworks")
    return Response(
        content=artworks_data,
        media_type="application/json",
        status_code=HTTP_200_OK,
    )
