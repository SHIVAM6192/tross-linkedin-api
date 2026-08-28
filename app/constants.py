class EntityType:
    # Entity types
    COMPANY = "com.linkedin.voyager.dash.organization.Company"
    SKILL = "com.linkedin.voyager.dash.identity.profile.Skill"
    PROFILE = "com.linkedin.voyager.dash.identity.profile.Profile"
    INDUSTRY = "com.linkedin.voyager.dash.common.Industry"
    TREASURY_MEDIA = "com.linkedin.voyager.dash.identity.profile.treasury.TreasuryMedia"
    POSITION = "com.linkedin.voyager.dash.identity.profile.Position"
    EDUCATION = "com.linkedin.voyager.dash.identity.profile.Education"
    CERTIFICATION = "com.linkedin.voyager.dash.identity.profile.Certification"
    PROJECT = "com.linkedin.voyager.dash.identity.profile.Project"
    LANGUAGE = "com.linkedin.voyager.dash.identity.profile.Language"
    
class APIHeader:
    # Header keys
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    X_RESTLI_PROTOCOL_VERSION = "2.0.0"
    ACCEPT = "application/vnd.linkedin.normalized+json+2.1"