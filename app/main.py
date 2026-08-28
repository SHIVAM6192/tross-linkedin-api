import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import ProfileResponse
from app.services import LinkedInScraperService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tross LinkedIn Reverse Engineering Challenge",
    description="An API that retrieves structured LinkedIn profile data via direct Voyager API requests."
)

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
async def fetch_profile(url: str = Query(..., description="The full LinkedIn profile URL")):
    """
    Main endpoint to fetch profile data.
    The 'response_model' decorator automatically validates the return dictionary 
    against our Pydantic schema and generates interactive documentation.
    """
    logger.info(f"Received request to fetch profile for URL: {url}")
    
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