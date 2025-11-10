-- Supabase Schema for Product Automation
-- Tables for AI-powered product analysis, price research, and listing generation

-- Table for storing product analyses (GPT-4 Vision results)
CREATE TABLE IF NOT EXISTS product_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    images TEXT[] NOT NULL,
    analysis_result JSONB,  -- Complete GPT-4 Vision analysis result
    status TEXT DEFAULT 'analyzing',  -- analyzing, completed, failed
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL
);

-- Table for storing price research results
CREATE TABLE IF NOT EXISTS price_researches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_analysis_id UUID REFERENCES product_analyses(id) ON DELETE CASCADE,
    marketplace_prices JSONB,  -- Price data by marketplace
    recommended_price NUMERIC(10, 2),
    confidence TEXT,  -- high, medium, low, estimated
    created_at BIGINT NOT NULL
);

-- Table for storing generated listings (before publishing)
CREATE TABLE IF NOT EXISTS generated_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_analysis_id UUID REFERENCES product_analyses(id) ON DELETE CASCADE,
    marketplace_id TEXT NOT NULL,
    listing_data JSONB,  -- Complete listing content (title, description, etc.)
    status TEXT DEFAULT 'draft',  -- draft, approved, published, failed
    created_at BIGINT NOT NULL,
    updated_at BIGINT NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_product_analyses_user ON product_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_product_analyses_status ON product_analyses(status);
CREATE INDEX IF NOT EXISTS idx_product_analyses_created ON product_analyses(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_price_researches_analysis ON price_researches(product_analysis_id);

CREATE INDEX IF NOT EXISTS idx_generated_listings_analysis ON generated_listings(product_analysis_id);
CREATE INDEX IF NOT EXISTS idx_generated_listings_marketplace ON generated_listings(marketplace_id);
CREATE INDEX IF NOT EXISTS idx_generated_listings_status ON generated_listings(status);

-- Comments for documentation
COMMENT ON TABLE product_analyses IS 'Stores AI analysis results from GPT-4 Vision for product images';
COMMENT ON TABLE price_researches IS 'Stores price research data across multiple marketplaces';
COMMENT ON TABLE generated_listings IS 'Stores AI-generated marketplace listings before publishing';

COMMENT ON COLUMN product_analyses.analysis_result IS 'JSON containing product_name, brand, category, condition, details, confidence, etc.';
COMMENT ON COLUMN price_researches.marketplace_prices IS 'JSON with price data per marketplace: {marketplace_id: {min, max, avg, found, count}}';
COMMENT ON COLUMN generated_listings.listing_data IS 'JSON with marketplace-specific content: title, description, tags, specifications, price';

