import sys
import os
sys.path.append('.')

from agents.procurement_agent.cloud_link_detector import CloudLinkDetector, CloudProvider
from agents.procurement_agent.cloud_file_downloader import CloudFileDownloader
import argparse

def test_links(target_url=None):
    print("=" * 60)
    print("Cloud Link Integration Test")
    print("=" * 60)
    
    detector = CloudLinkDetector()
    downloader = CloudFileDownloader()
    
    # Use provided URL or test default
    if target_url:
        test_body = f"Please find the documents here: {target_url}"
    else:
        test_body = """
        Hello, 
        Here are the project files:
        OneDrive: https://1drv.ms/f/s!Ap_Example_Link
        Google Drive: https://drive.google.com/drive/folders/1wExampleFolderID
        """
        print("Using sample email body (since no URL provided)...")
    
    # 1. Detection
    print("\nPhase 1: Detection")
    links = detector.detect_links(test_body)
    
    if not links:
        print("❌ No cloud links detected in the input.")
        return
    
    print(f"✅ Found {len(links)} link(s):")
    for i, link in enumerate(links, 1):
        print(f"   {i}. Provider: {link['provider'].value}")
        print(f"      URL: {link['url']}")
    
    # 2. Download (Only if real URL provided)
    if target_url:
        print("\nPhase 2: Downloading...")
        save_dir = "./storage/test_downloads"
        os.makedirs(save_dir, exist_ok=True)
        
        for link in links:
            provider = link['provider']
            url = link['url']
            
            try:
                if provider in [CloudProvider.ONEDRIVE, CloudProvider.SHAREPOINT]:
                    files = downloader.download_from_onedrive(url, save_dir)
                elif provider == CloudProvider.GOOGLE_DRIVE:
                    file_id = link.get('file_id')
                    if file_id:
                        files = downloader.download_from_google_drive(url, file_id, save_dir)
                    else:
                        print(f"❌ Could not extract file ID for Google Drive link")
                        files = []
                else:
                    print(f"⚠️  Provider {provider.value} not supported for direct download yet.")
                    files = []
                
                if files:
                    print(f"✅ Successfully downloaded {len(files)} file(s) to {save_dir}")
                    for f in files:
                        print(f"   [+] {os.path.basename(f)}")
                else:
                    print(f"❌ Download failed for {url}")
                    print("   Note: Ensure you have run the relevant OAuth script first (scripts/run_outlook_oauth.py or scripts/run_gmail_oauth.py)")
            
            except Exception as e:
                print(f"❌ Error during download: {e}")
    else:
        print("\nPhase 2 skipped (no target URL provided for actual download test).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Cloud Link Integration")
    parser.add_argument("--url", help="URL to test detection and download")
    args = parser.parse_args()
    
    test_links(args.url)
