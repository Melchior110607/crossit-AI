-- Supabase (PostgreSQL) Schema for marketplace_connections
-- Run this in Supabase SQL Editor

-- Drop existing table if you want to recreate it
-- DROP TABLE IF EXISTS marketplace_connections CASCADE;

CREATE TABLE IF NOT EXISTS marketplace_connections (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    marketplace_id TEXT NOT NULL,
    marketplace_name TEXT NOT NULL,
    
    -- OAuth / API Credentials
    auth_type TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at BIGINT, -- Unix timestamp (INTEGER)
    api_key TEXT,
    api_secret TEXT,
    
    -- Marketplace specific data
    shop_id TEXT,
    shop_name TEXT,
    shop_url TEXT,
    seller_id TEXT,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'active',
    last_sync_at BIGINT, -- Unix timestamp
    last_error TEXT,
    
    -- Metadata
    created_at BIGINT NOT NULL, -- Unix timestamp
    updated_at BIGINT NOT NULL, -- Unix timestamp
    
    UNIQUE(user_id, marketplace_id)
);

CREATE INDEX IF NOT EXISTS idx_marketplace_connections_user ON marketplace_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_connections_status ON marketplace_connections(status);

