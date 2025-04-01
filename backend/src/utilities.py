import base64
import os
import asyncio
from PIL import Image as PILImage
from playwright.async_api import Page, async_playwright
import io

current_dir = os.path.dirname(os.path.abspath(__file__))
mark_page_path = os.path.join(current_dir, "static", "mark_page.js")


async def mark_page(page):

    """
    1. Wait for the page to be loaded using 'networkidle'.
    2. Attempt to run a 'mark_page_script' that presumably marks and returns bounding boxes.
    3. Retry up to 10 times if it fails.
    4. Capture a screenshot with retry logic (up to 3 tries) if the page is blank.
    5. Process screenshot (grayscale, resize, quantize, compress).
    6. Remove the markings before returning.
    """

    bboxes = []
    for attempt in range (3):
        try:
            with open(mark_page_path) as f:
                mark_page_script = f.read()
            await page.wait_for_load_state("domcontentloaded")
            await page.evaluate(mark_page_script)
            bboxes = await page.evaluate("markPage()")
            break
        except Exception as e:
            print(f"[mark_page] Attempt {attempt +1}/3 failed to mark page: {e}")
            await asyncio.sleep(3)
    # Get screenshot as bytes
    await page.wait_for_load_state("networkidle")
    screenshot_bytes = await capture_screenshot(page, max_retries=3)

    # Process screenshot if we have any bytes
    if screenshot_bytes:
        img = PILImage.open(io.BytesIO(screenshot_bytes))
        # Convert to grayscale
        img = img.convert('L')
        # Resize
        max_size = (600, 600)
        img.thumbnail(max_size, PILImage.Resampling.LANCZOS)
        # Quantize and convert back to grayscale
        img = img.quantize(colors=256).convert('RGB')

        # Compress
        buffer = io.BytesIO()
        img.save(
            buffer,
            format='JPEG',
            quality=50,      # Low quality -> smaller size
            optimize=True,
            progressive=True
        )
        compressed_bytes = buffer.getvalue()
    else:
        # If screenshot is empty or never taken, handle gracefully
        print("[mark_page] Using empty screenshot due to failure or blank screenshot.")
        compressed_bytes = b""

    await page.wait_for_load_state("networkidle")
    try:
        await page.evaluate("unmarkPage()")
    except Exception as e:
        print(f"[mark_page] Could not unmark page: {e}")

    # Build final result
    return {
        "image": base64.b64encode(compressed_bytes).decode("utf-8"),
        "bboxes": bboxes
    }


async def is_image_blank(image_bytes: bytes) -> bool:
    """Return True if the screenshot is fully blank (e.g. all white), else False."""
    if not image_bytes:
        return True
    img = PILImage.open(io.BytesIO(image_bytes)).convert("L")
    # If getbbox() returns None, the image is entirely one color
    return img.getbbox() is None


async def capture_screenshot(page: Page, max_retries=3, wait_seconds=2) -> bytes:
    """Take a screenshot, retry if blank (completely white)."""
    screenshot_bytes = b""
    for attempt in range(max_retries):
        # Wait for the page to be fully loaded
        await page.wait_for_load_state("networkidle")

        # Take screenshot
        screenshot_bytes = await page.screenshot(path="screenshot.jpg", type="jpeg", quality=60, scale="device")

        # Check if it's blank
        if not await is_image_blank(screenshot_bytes):
            return screenshot_bytes

        # If blank, wait a bit and retry
        print(f"[capture_screenshot] Screenshot is blank (attempt {attempt + 1}/{max_retries}). Retrying...")
        await asyncio.sleep(wait_seconds)

    # If we get here, all attempts yielded a blank screenshot
    print("[capture_screenshot] All screenshot attempts were blank.")
    return screenshot_bytes  # Return whatever we got last


async def setup_browser_2(go_to_page: str):
    playwright = await async_playwright().start()

    # Add browser arguments to appear more human-like
    browser_args = [
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled',  # Hide automation
        '--no-sandbox',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        # Use a common user agent
    ]

    # Add browser context options
    context_options = {
        # "viewport": {"width": 1076, "height": 1076},  # Standard desktop resolution
        "viewport": {"width": 1280, "height": 720},
        "user_agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        "permissions": ['geolocation'],
        "geolocation": {"latitude": 37.7749, "longitude": -122.4194},  # Set a fixed location
        "locale": 'en-US',
        "timezone_id": 'America/Los_Angeles',
    }

    browser = await playwright.chromium.launch(
        headless=True,
        args=browser_args
    )

    # Create context with the specified options
    context = await browser.new_context(**context_options)

    # Enable JavaScript and cookies
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    page = await context.new_page()

    try:
        await page.goto(go_to_page, timeout=80000, wait_until="domcontentloaded")
    except Exception as e:
        print(f"Error loading page: {e}")
        # Fallback to Google if the original page fails to load
        await page.goto("https://www.google.com", timeout=60000, wait_until="domcontentloaded")

    return playwright, browser, page
