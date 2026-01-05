import boto3
import os
from PIL import Image
from dotenv import load_dotenv
import sys

# Load environment variables from .env.local file
load_dotenv('.env.local')

# Configuration from environment variables
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

# Validate required environment variables
required_vars = {
    "R2_ACCESS_KEY_ID": R2_ACCESS_KEY_ID,
    "R2_SECRET_ACCESS_KEY": R2_SECRET_ACCESS_KEY,
    "R2_ACCOUNT_ID": R2_ACCOUNT_ID,
    "R2_BUCKET_NAME": R2_BUCKET_NAME,
    "R2_PUBLIC_URL": R2_PUBLIC_URL,
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

def upload_blog_images(blog_slug, image_files, artifact_dir):
    """
    Upload blog images to R2 in Freepromptbase/{blog_slug}/ folder
    
    Args:
        blog_slug: The blog identifier (e.g., 'analyze_lead_generation_data_1')
        image_files: List of image filenames in artifact_dir
        artifact_dir: Directory containing the images
    
    Returns:
        List of public URLs for the uploaded images
    """
    print(f"Starting WebP conversion and upload for blog: {blog_slug}")
    
    uploaded_urls = []
    
    for idx, image_file in enumerate(image_files, start=1):
        file_path = os.path.join(artifact_dir, image_file)
        
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue
        
        # Generate R2 key with Freepromptbase folder structure
        r2_key = f"Freepromptbase/{blog_slug}/image_{idx}.webp"
        
        print(f"Processing {image_file}...")
        
        try:
            # Open image and convert to WebP
            with Image.open(file_path) as img:
                # Save as WebP in temp location
                webp_path = file_path.replace(".png", ".webp")
                img.save(webp_path, "WEBP", quality=85)
                
            print(f"Converted to WebP: {webp_path}")

            # Upload WebP to R2
            print(f"Uploading to {r2_key}...")
            with open(webp_path, "rb") as f:
                s3.upload_fileobj(
                    f, 
                    R2_BUCKET_NAME, 
                    r2_key,
                    ExtraArgs={'ContentType': "image/webp"}
                )
            
            public_url = f"{R2_PUBLIC_URL}/{r2_key}"
            print(f"✓ Success! URL: {public_url}")
            uploaded_urls.append(public_url)
            
            # Clean up local webp
            os.remove(webp_path)
            
        except Exception as e:
            print(f"✗ Failed to process/upload {image_file}: {e}")
    
    return uploaded_urls

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python upload_blog_images.py <blog_slug>")
        print("Example: python upload_blog_images.py analyze_lead_generation_data_1")
        sys.exit(1)
    
    blog_slug = sys.argv[1]
    artifact_dir = "/Users/bipulkumar/.gemini/antigravity/brain/2e735bf3-a300-4688-8a84-448f2e4f1a71"
    
    # Find all PNG files in artifact directory (sorted by name)
    image_files = sorted([f for f in os.listdir(artifact_dir) if f.endswith('.png')])
    
    if not image_files:
        print(f"No PNG images found in {artifact_dir}")
        sys.exit(1)
    
    print(f"Found {len(image_files)} images to upload")
    
    urls = upload_blog_images(blog_slug, image_files, artifact_dir)
    
    print("\n" + "="*60)
    print("UPLOAD COMPLETE")
    print("="*60)
    print(f"Blog: {blog_slug}")
    print(f"Uploaded: {len(urls)} images")
    print("\nGenerated URLs:")
    for i, url in enumerate(urls, start=1):
        print(f"  image_{i}: {url}")
