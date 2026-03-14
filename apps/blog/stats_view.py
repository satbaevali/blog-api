import asyncio
import logging 
import httpx
from asgiref.sync import async_to_sync


from .models import Post,Category,Tag,Comment
from .serializers import PostSerializer,CategorySerializer,TagSerializer,CommentSerializer
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample  
from rest_framework import status  



logger = logging.getLogger('__name__')
@extend_schema(
    tags=['stats'],
    summary="Get blog statistics",
    description="Endpoint to retrieve statistics about the blog, including total posts, categories, tags, and comments.",
    responses={
        200: OpenApiResponse(
            description="Statistics retrieved successfully",
            examples=[
                OpenApiExample(
                    "Example Response",
                    value={
                        "total_posts": 100,
                        "total_categories": 10,
                        "total_tags": 20,
                        "total_comments": 50
                    }
                )
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def stats_view(request):
    logger.info("Stats view accessed")

    blog_stats = {
        "total_posts": Post.objects.count(),
        "total_categories": Category.objects.count(),
        "total_tags": Tag.objects.count(),
        "total_comments": Comment.objects.count()
    }
    async def fetch_external_data():
        async with httpx.AsyncClient(timeout=10.0) as client:
            return await asyncio.gather(
                fetch_external_rate(client),
                fetch_external_time(client),
                return_exceptions=True
            )
    try:
        exchange_data,time_data = async_to_sync(fetch_external_data)()

        if isinstance(exchange_data, Exception):
            logger.error(f"Error fetching exchange rate: {exchange_data}")
            exchange_data = None
        if isinstance(time_data, Exception):
            logger.error(f"Error fetching time: {time_data}")
            time_data = None

            response_data = {
                "blog": blog_stats,
                "external_rates": exchange_data,
                time_data: None
            }
            logger.info("Stats view response: %s", response_data)
            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in stats view: {e}")
        return Response({"error": "Failed to retrieve statistics"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
async def fetch_exchange_rate(client: httpx.AsyncClient):
    logger.info
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = await client.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get("rates", {}).get("EUR")

    result = {
        'KZT': data.get("rates", {}).get("KZT"),
        'USD': data.get("rates", {}).get("USD"),
        'EUR': data.get("rates", {}).get("EUR"),
    }
    logger.info(f"Fetched exchange rates: {result}")
    return result

async def fetch_almaty_time(client: httpx.AsyncClient):
    logger.info("Fetching Almaty time")
    url = "http://worldtimeapi.org/api/timezone/Asia/Almaty"

    response = await client.get(url)
    response.raise_for_status()
    data = response.json()
    almaty_time = data.get("datetime")
    logger.info(f"Fetched Almaty time: {almaty_time}")
    return almaty_time