from typing import Dict, Any, List, Optional
from app.constants import EntityType

class ProfileParser:
    """Handles the extraction and normalization of LinkedIn's heavily nested JSON."""
    def __init__(self, raw_json: Dict[str, Any], url: str, username: str):
        self.elements = raw_json.get("included", [])
        self.url = url
        self.username = username
        self.company_map = self._build_company_map()
        self.skill_map = self._build_skill_map()

    def _build_company_map(self) -> Dict[str, str]:
        cmap = {}
        for item in self.elements:
            if item.get("$type") == EntityType.COMPANY:
                urn = item.get("entityUrn")
                name = item.get("name")
                if urn and name:
                    cmap[urn] = name
        return cmap

    def _build_skill_map(self) -> Dict[str, str]:
        smap = {}
        for item in self.elements:
            if item.get("$type") == EntityType.SKILL:
                urn = item.get("entityUrn")
                name = item.get("name")
                if urn and name:
                    smap[urn] = name
        return smap

    @staticmethod
    def extract_date(date_obj: Optional[Dict[str, Any]]) -> Optional[str]:
        if not date_obj:
            return None
        year = date_obj.get("year")
        month = date_obj.get("month")
        if year and month:
            return f"{month:02d}/{year}"
        if year:
            return str(year)
        return None

    # This will image from profile
    @staticmethod
    def extract_image_url(image_data: Dict[str, Any]) -> Optional[str]:
        try:
            vector = image_data.get("displayImageReference", {}).get("vectorImage", {})
            if not vector:
                vector = image_data.get("originalImageReference", {}).get("vectorImage", {}) or image_data.get("vectorImage", {})
            
            root_url = vector.get("rootUrl", "")
            artifacts = vector.get("artifacts", [])
            
            if not root_url or not artifacts:
                return None
                
            largest_artifact = artifacts[-1].get("fileIdentifyingUrlPathSegment", "")
            return f"{root_url}{largest_artifact}"
        except Exception:
            return None

    # This will parse the core profile information
    def parse_core_profile(self) -> Dict[str, Any]:
        profile = next((i for i in self.elements if i.get("$type") == EntityType.PROFILE), {})
        industry = next((i.get("name") for i in self.elements if i.get("$type") == EntityType.INDUSTRY), None)
        return {
            "public_identifier": self.username,
            "profile_urn": profile.get("entityUrn"),
            "industry": industry,
            "full_name": f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip(),
            "headline": profile.get("headline"),
            "about": profile.get("summary"),
            "location": profile.get("locationName") or profile.get("geoLocationName"),
            "profile_picture_url": self.extract_image_url(profile.get("profilePicture", {})),
            "background_picture_url": self.extract_image_url(profile.get("backgroundPicture", {}))
        }

    # This will parse featured media
    def parse_featured_media(self) -> List[Dict[str, Any]]:
        media = []
        for item in self.elements:
            if item.get("$type") == EntityType.TREASURY_MEDIA:
                data = item.get("data", {})
                doc = data.get("NativeDocument", {})
                doc_url = doc.get("transcribedDocumentUrl")
                ext_url = data.get("Url")

                media.append({
                    "title": item.get("title") or doc.get("title"),
                    "description": item.get("description"),
                    "url": doc_url or ext_url,
                    "media_type": "Document" if doc_url else "Link",
                    "thumbnail_url": self.extract_image_url(item.get("previewImage", {}).get("attributes", [{}])[0].get("detailDataUnion", {}))
                })
        return media

    # This will parse experiences
    def parse_experiences(self) -> List[Dict[str, Any]]:
        experiences = []
        for item in self.elements:
            if item.get("$type") == EntityType.POSITION:
                company_urn = item.get("*company")
                company_name = self.company_map.get(company_urn) or item.get("companyName", "")
                experiences.append({
                    "title": item.get("title", ""),
                    "company_name": company_name,
                    "location": item.get("locationName"),
                    "description": item.get("description"),
                    "start_date": self.extract_date(item.get("dateRange", {}).get("start")),
                    "end_date": self.extract_date(item.get("dateRange", {}).get("end"))
                })
        return experiences

    # This will parse educations
    def parse_educations(self) -> List[Dict[str, Any]]:
        educations = []
        for item in self.elements:
            if item.get("$type") == EntityType.EDUCATION:
                educations.append({
                    "school_name": item.get("schoolName", ""),
                    "degree_name": item.get("degreeName"),
                    "field_of_study": item.get("fieldOfStudy"),
                    "grade": item.get("grade"),
                    "start_date": self.extract_date(item.get("dateRange", {}).get("start")),
                    "end_date": self.extract_date(item.get("dateRange", {}).get("end"))
                })
        return educations

    # This will parse certifications
    def parse_certifications(self) -> List[Dict[str, Any]]:
        certifications = []
        for item in self.elements:
            if item.get("$type") == EntityType.CERTIFICATION:
                certifications.append({
                    "name": item.get("name", ""),
                    "authority": item.get("authority"),
                    "url": item.get("url"),
                    "license_number": item.get("licenseNumber"),
                    "start_date": self.extract_date(item.get("dateRange", {}).get("start")),
                    "end_date": self.extract_date(item.get("dateRange", {}).get("end"))
                })
        return certifications

    # This will parse projects
    def parse_projects(self) -> List[Dict[str, Any]]:
        projects = []
        for item in self.elements:
            if item.get("$type") == EntityType.PROJECT:
                projects.append({
                    "title": item.get("title", ""),
                    "description": item.get("description"),
                    "url": item.get("url"),
                    "start_date": self.extract_date(item.get("dateRange", {}).get("start")),
                    "end_date": self.extract_date(item.get("dateRange", {}).get("end"))
                })
        return projects

    # This will parse skills and languages
    def parse_skills_and_languages(self) -> tuple[List[str], List[str]]:
        skills = list(self.skill_map.values())
        languages = []
        for item in self.elements:
            if item.get("$type") == EntityType.LANGUAGE:
                languages.append(item.get("name", ""))
        return skills, languages

    # This will extract the full profile data
    def extract_full_profile(self) -> Dict[str, Any]:
        core = self.parse_core_profile()
        skills, languages = self.parse_skills_and_languages()
        
        return {
            **core,
            "featured_media": self.parse_featured_media(),
            "experiences": self.parse_experiences(),
            "educations": self.parse_educations(),
            "certifications": self.parse_certifications(),
            "projects": self.parse_projects(),
            "skills": skills,
            "languages": languages
        }