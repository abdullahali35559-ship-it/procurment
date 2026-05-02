"""
Cloud Storage Link Detector
Detects and extracts cloud storage links from email content
"""
import re
from typing import List, Dict, Optional
from enum import Enum


class CloudProvider(Enum):
    """Supported cloud storage providers"""
    ONEDRIVE = "onedrive"
    SHAREPOINT = "sharepoint"
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"
    UNKNOWN = "unknown"


class CloudLinkDetector:
    """Detect and classify cloud storage links in email bodies"""
    
    # OneDrive patterns
    ONEDRIVE_PATTERNS = [
        r'https://1drv\.ms/[a-zA-Z]/[^\s]+',
        r'https://onedrive\.live\.com/[^\s]+',
        r'https://[a-zA-Z0-9-]+\.sharepoint\.com/personal/[^\s]+'
    ]
    
    # SharePoint patterns (More inclusive)
    SHAREPOINT_PATTERNS = [
        r'https://[a-zA-Z0-9-]+\.sharepoint\.com/[^\s]+',
        r'https://[a-zA-Z0-9-]+-my\.sharepoint\.com/[^\s]+'
    ]
    
    # Google Drive patterns
    GOOGLE_DRIVE_PATTERNS = [
        r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)[^\s]*',
        r'https://drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)[^\s]*',
        r'https://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)[^\s]*',
        r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)[^\s]*',
        r'https://docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)[^\s]*'
    ]
    
    # Dropbox patterns
    DROPBOX_PATTERNS = [
        r'https://www\.dropbox\.com/[^\s]+',
        r'https://dl\.dropboxusercontent\.com/[^\s]+'
    ]
    
    def __init__(self):
        """Initialize detector"""
        pass
    
    def detect_links(self, email_body: str) -> List[Dict]:
        """
        Detect all cloud storage links in email body
        
        Args:
            email_body: Email body text
            
        Returns:
            List of dictionaries with link info:
            {
                'url': 'https://...',
                'provider': CloudProvider.ONEDRIVE,
                'type': 'shared_link',
                'file_id': '...' (for Google Drive)
            }
        """
        if not email_body:
            return []
        
        links = []
        
        # Detect OneDrive links
        links.extend(self._detect_onedrive_links(email_body))
        
        # Detect SharePoint links
        links.extend(self._detect_sharepoint_links(email_body))
        
        # Detect Google Drive links
        links.extend(self._detect_google_drive_links(email_body))
        
        # Detect Dropbox links
        links.extend(self._detect_dropbox_links(email_body))
        
        # Remove duplicates and clean up trailing punctuation
        unique_links = []
        seen_urls = set()
        for link in links:
            # Strip trailing punctuation (common when link is at end of sentence)
            link['url'] = link['url'].rstrip('.,!?;:')
            
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        return unique_links
    
    def _detect_onedrive_links(self, email_body: str) -> List[Dict]:
        """Detect OneDrive links"""
        links = []
        
        for pattern in self.ONEDRIVE_PATTERNS:
            matches = re.findall(pattern, email_body)
            for match in matches:
                # Clean up URL (remove trailing punctuation)
                url = match.rstrip('.,;:)')
                
                links.append({
                    'url': url,
                    'provider': CloudProvider.ONEDRIVE,
                    'type': 'shared_link'
                })
        
        return links
    
    def _detect_sharepoint_links(self, email_body: str) -> List[Dict]:
        """Detect SharePoint links"""
        links = []
        
        for pattern in self.SHAREPOINT_PATTERNS:
            matches = re.findall(pattern, email_body)
            for match in matches:
                # Clean up URL
                url = match.rstrip('.,;:)')
                
                links.append({
                    'url': url,
                    'provider': CloudProvider.SHAREPOINT,
                    'type': 'shared_link'
                })
        
        return links
    
    def _detect_google_drive_links(self, email_body: str) -> List[Dict]:
        """Detect Google Drive links"""
        links = []
        
        for pattern in self.GOOGLE_DRIVE_PATTERNS:
            for match in re.finditer(pattern, email_body):
                # Extract full match as URL and Group 1 as file_id
                url = match.group(0).rstrip('.,;:)')
                file_id = match.group(1) if match.groups() else None
                
                # Clean up URL if it has extra params that shouldn't be there
                # (though usually the regex handles this, we be careful)
                
                links.append({
                    'url': url,
                    'provider': CloudProvider.GOOGLE_DRIVE,
                    'type': 'shared_link',
                    'file_id': file_id
                })
        
        return links
    
    def _detect_dropbox_links(self, email_body: str) -> List[Dict]:
        """Detect Dropbox links"""
        links = []
        
        for pattern in self.DROPBOX_PATTERNS:
            matches = re.findall(pattern, email_body)
            for match in matches:
                url = match.rstrip('.,;:)')
                
                links.append({
                    'url': url,
                    'provider': CloudProvider.DROPBOX,
                    'type': 'shared_link'
                })
        
        return links
    
    def has_cloud_links(self, email_body: str) -> bool:
        """Check if email body contains any cloud storage links"""
        links = self.detect_links(email_body)
        return len(links) > 0

    def classify_link_safety(self, url: str) -> str:
        """
        Classify link safety: TRUSTED, VERIFIED, SUSPICIOUS
        """
        url_lower = url.lower()
        
        # Level 1: Trusted Tier-1 Cloud Providers
        trusted_domains = [
            'drive.google.com', 'docs.google.com', 'onedrive.live.com', 
            '1drv.ms', 'sharepoint.com', 'dropbox.com'
        ]
        if any(dom in url_lower for dom in trusted_domains):
            return "TRUSTED"
            
        # Level 2: Verified Transfer Services
        verified_domains = [
            'wetransfer.com', 'transfernow.net', 'iclouddot.com', 'box.com'
        ]
        if any(dom in url_lower for dom in verified_domains):
            return "VERIFIED"
            
        # Level 3: High Risk (Shorteners or unknown redirection)
        suspicious_domains = [
            'tinyurl.com', 'bit.ly', 'cutt.ly', 't.co', 'goo.gl', 'buff.ly'
        ]
        if any(dom in url_lower for dom in suspicious_domains):
            return "SUSPICIOUS"
            
        return "UNKNOWN"


# Test function
if __name__ == "__main__":
    print("Testing Cloud Link Detector...")
    
    detector = CloudLinkDetector()
    
    # Test email body
    test_email = """
    Dear Vendor,
    
    Please find tender documents at:
    https://1drv.ms/f/s!Abc123xyz456
    
    Additional files:
    https://drive.google.com/file/d/1234567890abcdef/view?usp=sharing
    
    Regards,
    Client
    """
    
    links = detector.detect_links(test_email)
    
    print(f"\nFound {len(links)} cloud links:")
    for link in links:
        print(f"\n  Provider: {link['provider'].value}")
        print(f"  URL: {link['url']}")
        if 'file_id' in link and link['file_id']:
            print(f"  File ID: {link['file_id']}")
    
    print("\nTest complete!")