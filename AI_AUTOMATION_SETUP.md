# AI Product Automation - Setup Guide

## Overview

The AI Product Automation feature uses GPT-4 Vision and GPT-4 to automatically:
1. Analyze product images
2. Research prices across marketplaces
3. Generate optimized listings
4. Recommend best marketplaces
5. Publish with one click

---

## Requirements

### 1. OpenAI API Key

You need an OpenAI API key with access to GPT-4 Vision.

**Get your API key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

**Add to `.env` file:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_VISION_MODEL=gpt-4o  # or gpt-4-vision-preview
OPENAI_TEXT_MODEL=gpt-4o     # or gpt-4-turbo-preview
```

### 2. Supabase Database Schema

Apply the automation schema to your Supabase database.

**Using Supabase Dashboard:**
1. Go to https://app.supabase.com
2. Select your project
3. Go to SQL Editor
4. Copy the contents of `backend/supabase_automation_schema.sql`
5. Paste and run the SQL script

**Or using Supabase CLI:**
```bash
supabase db push backend/supabase_automation_schema.sql
```

**Tables created:**
- `product_analyses` - Stores AI analysis results
- `price_researches` - Stores price research data
- `generated_listings` - Stores generated listings before publishing

### 3. eBay Finding API (Optional - for better price research)

For better price research, configure eBay Finding API:

**Add to `.env`:**
```bash
EBAY_FINDING_APP_ID=your-ebay-app-id  # Same as EBAY_APP_ID or separate
```

**Note:** If not configured, the system will still work but with limited price research capabilities.

---

## Installation

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `openai>=1.12.0` - OpenAI Python SDK
- `aiohttp>=3.9.0` - Async HTTP client

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

New dependencies added:
- `framer-motion` - Animation library

### 3. Restart Docker Services

```bash
docker-compose down
docker-compose up -d --build
```

---

## Usage

### 1. Navigate to Smart Product Creation

Go to: http://localhost:3000/dashboard/products/new

### 2. Upload Product Images

- Drag & drop or browse to select images
- **Important:** Include photos from all angles
  - Front, back, sides, top, bottom
  - Any defects or wear
  - Original box and accessories (if available)
  - Brand labels, tags, serial numbers

### 3. AI Analysis (Automatic)

The system will:
- ✅ Analyze images with GPT-4 Vision
- ✅ Identify product, brand, category, condition
- ✅ Extract details (color, size, model, etc.)
- ✅ Flag missing information

### 4. Price Research (Automatic)

The system will:
- ✅ Search user's connected marketplaces
- ✅ Search all available marketplaces
- ✅ Perform web search if needed
- ✅ AI estimation as fallback
- ✅ Calculate recommended price

### 5. Marketplace Recommendations (Automatic)

The system will:
- ✅ Analyze product category
- ✅ Match with marketplace specialties
- ✅ Score each marketplace (0-1.0)
- ✅ Filter by compatibility
- ✅ Prioritize connected marketplaces

### 6. Content Generation (Automatic)

For each recommended marketplace:
- ✅ SEO-optimized title
- ✅ Compelling description
- ✅ Relevant tags/keywords
- ✅ Structured specifications
- ✅ Marketplace-specific formatting

### 7. Review & Approve

- View generated listings for each marketplace
- Edit titles, descriptions, prices
- Approve or skip marketplaces
- Preview before publishing

### 8. Publish

- Click "Publish to X Marketplaces"
- Listings are created in database
- (Future: Actual API publishing to marketplaces)

---

## API Endpoints

### Product Analysis
```http
POST /api/products/analyze
Content-Type: application/json

{
  "images": ["https://...", "https://..."]
}
```

### Price Research
```http
POST /api/products/research-prices
Content-Type: application/json

{
  "analysis_id": "uuid",
  "product_info": {...}
}
```

### Generate Listings
```http
POST /api/products/generate-listings
Content-Type: application/json

{
  "analysis_id": "uuid",
  "product_info": {...},
  "price_data": {...},
  "selected_marketplaces": ["ebay", "shopify"]
}
```

### Publish Listings
```http
POST /api/products/publish-listings
Content-Type: application/json

{
  "analysis_id": "uuid",
  "listings": {
    "ebay": {...},
    "shopify": {...}
  }
}
```

---

## Configuration

### Marketplace Categories

Defined in `backend/app/services/marketplace_recommender.py`:

```python
MARKETPLACE_CATEGORIES = {
    "stockx": {
        "primary": ["sneakers", "streetwear", "collectibles", "watches"],
        "excluded": ["handmade", "vintage"]
    },
    "ebay": {
        "primary": ["all"]  # Accepts everything
    },
    "etsy": {
        "primary": ["handmade", "vintage", "crafts"],
        "excluded": ["mass_produced", "resale"]
    },
    ...
}
```

### OpenAI Models

You can use different models:

**GPT-4 Vision (Recommended):**
- `gpt-4o` - Latest, fastest, most accurate
- `gpt-4-vision-preview` - Older version

**GPT-4 Text (Recommended):**
- `gpt-4o` - Latest, fastest
- `gpt-4-turbo-preview` - Alternative

---

## Troubleshooting

### "OpenAI API key not configured"

**Solution:** Add `OPENAI_API_KEY` to your `.env` file and restart:
```bash
docker-compose restart backend
```

### "Analysis failed"

**Possible causes:**
1. Invalid image URLs
2. Images not accessible
3. OpenAI API rate limit
4. Invalid API key

**Check logs:**
```bash
docker logs crossit-backend --tail 100
```

### "Price research found no results"

**This is normal** - the system will:
1. Try marketplace APIs
2. Perform web search
3. Use AI estimation as fallback

### Database errors

**Verify schema is applied:**
```sql
-- In Supabase SQL Editor
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('product_analyses', 'price_researches', 'generated_listings');
```

---

## Cost Considerations

### OpenAI API Costs (approximate)

**GPT-4 Vision (per analysis):**
- Input: ~1,000-3,000 tokens per image
- Output: ~500-1,000 tokens
- Cost: **$0.01 - $0.05 per analysis**

**GPT-4 Text (per listing):**
- Input: ~500-1,000 tokens
- Output: ~300-500 tokens per marketplace
- Cost: **$0.001 - $0.01 per listing**

**Total per product:** $0.02 - $0.15 depending on:
- Number of images
- Number of marketplaces
- Detail level requested

### eBay Finding API

- **Free** up to 5,000 calls/day
- Additional calls may incur charges

---

## Future Enhancements

### Planned Features

1. **Real Marketplace Publishing**
   - Direct API integration with eBay, Shopify, etc.
   - Automatic listing creation
   - Inventory synchronization

2. **Image Enhancement**
   - Background removal
   - Image upscaling
   - Watermark addition

3. **Advanced Pricing**
   - Machine learning price predictions
   - Historical price trends
   - Competitor analysis

4. **Multi-language Support**
   - Auto-translate listings
   - Locale-specific content

5. **Batch Processing**
   - Upload multiple products at once
   - Queue management
   - Progress tracking

---

## Support

For issues or questions:
1. Check logs: `docker logs crossit-backend`
2. Review Supabase tables for data
3. Test OpenAI API key manually
4. Verify all environment variables are set

---

**Status:** ✅ Ready for testing (OpenAI key required)

