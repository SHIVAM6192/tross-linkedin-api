import logging
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.schemas import ProfileResponse
from app.services import LinkedInScraperService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Extract client IP
def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

# Limiter to track requests per IP
limiter = Limiter(key_func=get_client_ip)

app = FastAPI(
    title="Tross LinkedIn Reverse Engineering Challenge",
    description="An API that retrieves structured LinkedIn profile data via direct Voyager API requests."
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate our scraper service
scraper = LinkedInScraperService()

@app.get("/", tags=["Health"])
def root():
    """Simple health check endpoint."""
    return {"message": "API is running. Visit /docs for Swagger UI."}

@app.get("/api/profile", response_model=ProfileResponse, tags=["Scraper"])
@limiter.limit("6/minute")
async def fetch_profile(request : Request, url: str = Query(..., description="The full LinkedIn profile URL")):
    """
    Main endpoint to fetch profile data.
    The 'response_model' decorator automatically validates the return dictionary 
    against our Pydantic schema and generates interactive documentation.
    """
    
    client_ip = get_client_ip(request)
    logger.info(f"Incoming request from IP [{client_ip}] for URL: {url}")
    
    try:
        # Await the async service method
        data = await scraper.get_profile_data(url)
        logger.info(f"Successfully retrieved and parsed profile data for URL: {url}")
        return data
    
    except ValueError as e:
        logger.warning(f"Validation Error for URL {url}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except PermissionError as e:
        logger.error(f"Authentication Error for URL {url}: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    
    except Exception as e:
        logger.exception(f"Unexpected Internal Server Error for URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")