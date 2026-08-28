import os
import re
import logging
from typing import Dict, Any
import httpx
from dotenv import load_dotenv
from app.ProfileParser import ProfileParser
from app.constants import APIHeader

load_dotenv()

logger = logging.getLogger(__name__)

class LinkedInScraperService:
    """Handles the HTTP communication with LinkedIn's internal Voyager API."""
    def __init__(self):
        self.li_at = os.getenv("LINKEDIN_LI_AT", "")
        self.jsessionid = os.getenv("LINKEDIN_JSESSIONID", "")
        
        if not self.li_at or not self.jsessionid:
            logger.critical("Missing LinkedIn credentials in .env file at startup.")
            raise ValueError("LinkedIn credentials are missing. Please set LINKEDIN_LI_AT and LINKEDIN_JSESSIONID in your .env file.")
        
        clean_jsessionid = self.jsessionid.strip('"')
        
        self.headers = {
            "User-Agent": APIHeader.USER_AGENT,
            "csrf-token": clean_jsessionid,
            "x-restli-protocol-version": APIHeader.X_RESTLI_PROTOCOL_VERSION,
            "Accept": APIHeader.ACCEPT,
            "Cookie": f'li_at={self.li_at}; JSESSIONID="{clean_jsessionid}";'
        }

    def extract_username(self, url: str) -> str:
        # Must be http or https
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("Invalid URL protocol. Ensure the URL starts with http:// or https://")
            
        # Must belong to linkedin.com, allowing for subdomains
        if "linkedin.com" not in url:
            raise ValueError("Invalid domain. Please provide a valid LinkedIn URL.")
            
        # Must contain /in/ followed by the username
        match = re.search(r"linkedin\.com/in/([^/?#\)]+)", url)
        if not match:
            raise ValueError("Invalid profile URL. Could not locate a valid username in the '/in/' path.")
            
        # Return the clean username
        username = match.group(1).strip("/").strip()
        logger.info(f"Successfully extracted username: {username}")
        return match.group(1).strip("/").strip()

    async def get_profile_data(self, profile_url: str) -> Dict[str, Any]:
        username = self.extract_username(profile_url)
        endpoint = f"https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={username}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-103"
        
        logger.info(f"Initiating HTTP GET request to LinkedIn Voyager API for user: {username}")
        
        async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
            response = await client.get(endpoint)
            logger.info(f"Received HTTP {response.status_code} from LinkedIn API")
            
            if response.status_code == 200:
                raw_json = response.json()
                logger.info("Successfully parsed JSON payload from LinkedIn. Handing off to ProfileParser.")
                parser = ProfileParser(raw_json, profile_url, username)
                return parser.extract_full_profile()
            
            if response.status_code in (302, 303, 401, 403, 999):
                logger.error(f"LinkedIn rejected the credentials. Status code: {response.status_code}")
                raise PermissionError("LinkedIn authentication failed. Check li_at and JSESSIONID.")
            
            elif response.status_code == 404:
                logger.warning(f"Profile not found or is private: {username}")
                raise ValueError("LinkedIn profile not found or private.")
            
            else:
                logger.error(f"Unexpected LinkedIn API error: {response.status_code} - {response.text}")
                raise RuntimeError(f"LinkedIn upstream API error: HTTP {response.status_code} - {response.text}")
            
            