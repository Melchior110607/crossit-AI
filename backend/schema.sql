-- CrossIt AI - SQLite Schema
-- Base de données pour stocker les connexions marketplaces, produits, listings, et analytics

-- ============================================
-- 1. USERS (déjà géré par better-auth)
-- ============================================
-- Les tables users sont gérées par better-auth dans auth.db

-- ============================================
-- 2. MARKETPLACE CONNECTIONS
-- ============================================

CREATE TABLE IF NOT EXISTS marketplace_connections (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    marketplace_id TEXT NOT NULL, -- amazon, ebay, etsy, etc.
    marketplace_name TEXT NOT NULL,
    
    -- OAuth / API Credentials
    auth_type TEXT NOT NULL, -- 'oauth2', 'api_key', 'bearer_token'
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at INTEGER, -- Unix timestamp
    api_key TEXT,
    api_secret TEXT,
    
    -- Marketplace specific data
    shop_id TEXT,
    shop_name TEXT,
    shop_url TEXT,
    seller_id TEXT,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'active', -- 'active', 'expired', 'error', 'disconnected'
    last_sync_at INTEGER, -- Unix timestamp
    last_error TEXT,
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    
    UNIQUE(user_id, marketplace_id)
);

CREATE INDEX idx_marketplace_connections_user ON marketplace_connections(user_id);
CREATE INDEX idx_marketplace_connections_status ON marketplace_connections(status);

-- ============================================
-- 3. PRODUCTS (Produits maîtres)
-- ============================================

CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    
    -- Product Info
    name TEXT NOT NULL,
    description TEXT,
    sku TEXT NOT NULL,
    
    -- Pricing
    base_price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    cost REAL, -- Coût d'achat
    
    -- Inventory
    total_stock INTEGER NOT NULL DEFAULT 0,
    reserved_stock INTEGER NOT NULL DEFAULT 0, -- Stock réservé pour commandes
    available_stock INTEGER GENERATED ALWAYS AS (total_stock - reserved_stock) STORED,
    
    -- Product Details
    category TEXT,
    brand TEXT,
    weight REAL, -- kg
    dimensions_length REAL, -- cm
    dimensions_width REAL,
    dimensions_height REAL,
    
    -- Images (JSON array of URLs)
    images TEXT, -- JSON: ["url1", "url2", ...]
    
    -- Status
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'active', 'archived'
    
    -- Analytics
    total_sales INTEGER NOT NULL DEFAULT 0,
    total_revenue REAL NOT NULL DEFAULT 0,
    average_rating REAL,
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    
    UNIQUE(user_id, sku)
);

CREATE INDEX idx_products_user ON products(user_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_sku ON products(sku);

-- ============================================
-- 4. LISTINGS (Produits listés sur marketplaces)
-- ============================================

CREATE TABLE IF NOT EXISTS listings (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    marketplace_connection_id TEXT NOT NULL,
    
    -- Marketplace specific IDs
    marketplace_listing_id TEXT, -- ID du produit sur le marketplace
    marketplace_sku TEXT,
    
    -- Pricing (peut différer du produit maître)
    price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    
    -- Inventory
    stock INTEGER NOT NULL DEFAULT 0,
    
    -- Listing customization
    title TEXT,
    description TEXT,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'active', 'paused', 'sold_out', 'error'
    sync_status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'synced', 'error'
    last_sync_at INTEGER,
    last_error TEXT,
    
    -- Analytics
    views INTEGER NOT NULL DEFAULT 0,
    sales INTEGER NOT NULL DEFAULT 0,
    revenue REAL NOT NULL DEFAULT 0,
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (marketplace_connection_id) REFERENCES marketplace_connections(id) ON DELETE CASCADE,
    UNIQUE(product_id, marketplace_connection_id)
);

CREATE INDEX idx_listings_user ON listings(user_id);
CREATE INDEX idx_listings_product ON listings(product_id);
CREATE INDEX idx_listings_marketplace ON listings(marketplace_connection_id);
CREATE INDEX idx_listings_status ON listings(status);

-- ============================================
-- 5. ORDERS (Commandes)
-- ============================================

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    marketplace_connection_id TEXT NOT NULL,
    
    -- Order Info
    marketplace_order_id TEXT NOT NULL,
    order_number TEXT,
    
    -- Amounts
    total_amount REAL NOT NULL,
    tax_amount REAL NOT NULL DEFAULT 0,
    shipping_amount REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'EUR',
    
    -- Customer Info (peut être limité selon marketplace)
    customer_name TEXT,
    customer_email TEXT,
    
    -- Shipping Address
    shipping_address_line1 TEXT,
    shipping_address_line2 TEXT,
    shipping_city TEXT,
    shipping_postal_code TEXT,
    shipping_country TEXT,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled', 'refunded'
    payment_status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'paid', 'failed', 'refunded'
    fulfillment_status TEXT NOT NULL DEFAULT 'unfulfilled', -- 'unfulfilled', 'fulfilled', 'partially_fulfilled'
    
    -- Tracking
    tracking_number TEXT,
    tracking_url TEXT,
    carrier TEXT,
    
    -- Dates
    ordered_at INTEGER NOT NULL,
    confirmed_at INTEGER,
    shipped_at INTEGER,
    delivered_at INTEGER,
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    
    FOREIGN KEY (marketplace_connection_id) REFERENCES marketplace_connections(id) ON DELETE CASCADE
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_marketplace ON orders(marketplace_connection_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_ordered_at ON orders(ordered_at);

-- ============================================
-- 6. ORDER ITEMS (Lignes de commande)
-- ============================================

CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    listing_id TEXT,
    
    -- Product Info (snapshot au moment de la commande)
    product_name TEXT NOT NULL,
    sku TEXT,
    
    -- Pricing
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(id) ON DELETE SET NULL
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_listing ON order_items(listing_id);

-- ============================================
-- 7. WEBHOOK EVENTS (pour traçabilité)
-- ============================================

CREATE TABLE IF NOT EXISTS webhook_events (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    marketplace_connection_id TEXT,
    
    -- Event Info
    event_type TEXT NOT NULL, -- 'order.created', 'inventory.updated', etc.
    event_source TEXT NOT NULL, -- marketplace_id
    
    -- Payload
    payload TEXT NOT NULL, -- JSON du webhook
    
    -- Processing
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'processed', 'failed'
    processed_at INTEGER,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    
    FOREIGN KEY (marketplace_connection_id) REFERENCES marketplace_connections(id) ON DELETE SET NULL
);

CREATE INDEX idx_webhook_events_status ON webhook_events(status);
CREATE INDEX idx_webhook_events_marketplace ON webhook_events(marketplace_connection_id);
CREATE INDEX idx_webhook_events_created_at ON webhook_events(created_at);

-- ============================================
-- 8. SYNC LOGS (Logs de synchronisation)
-- ============================================

CREATE TABLE IF NOT EXISTS sync_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    marketplace_connection_id TEXT,
    
    -- Sync Info
    sync_type TEXT NOT NULL, -- 'products', 'inventory', 'orders', 'full'
    direction TEXT NOT NULL, -- 'pull' (from marketplace), 'push' (to marketplace)
    
    -- Results
    status TEXT NOT NULL, -- 'started', 'completed', 'failed', 'partial'
    items_processed INTEGER NOT NULL DEFAULT 0,
    items_success INTEGER NOT NULL DEFAULT 0,
    items_failed INTEGER NOT NULL DEFAULT 0,
    
    -- Timing
    started_at INTEGER NOT NULL,
    completed_at INTEGER,
    duration_ms INTEGER, -- durée en millisecondes
    
    -- Details
    error_message TEXT,
    details TEXT, -- JSON avec plus d'infos si nécessaire
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    
    FOREIGN KEY (marketplace_connection_id) REFERENCES marketplace_connections(id) ON DELETE CASCADE
);

CREATE INDEX idx_sync_logs_user ON sync_logs(user_id);
CREATE INDEX idx_sync_logs_marketplace ON sync_logs(marketplace_connection_id);
CREATE INDEX idx_sync_logs_started_at ON sync_logs(started_at);

-- ============================================
-- 9. ANALYTICS DAILY (Agrégations quotidiennes)
-- ============================================

CREATE TABLE IF NOT EXISTS analytics_daily (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    marketplace_connection_id TEXT,
    product_id TEXT,
    
    -- Date
    date TEXT NOT NULL, -- YYYY-MM-DD
    
    -- Metrics
    views INTEGER NOT NULL DEFAULT 0,
    orders INTEGER NOT NULL DEFAULT 0,
    revenue REAL NOT NULL DEFAULT 0,
    units_sold INTEGER NOT NULL DEFAULT 0,
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    
    UNIQUE(user_id, marketplace_connection_id, product_id, date)
);

CREATE INDEX idx_analytics_daily_user ON analytics_daily(user_id);
CREATE INDEX idx_analytics_daily_date ON analytics_daily(date);

-- ============================================
-- TRIGGERS pour updated_at
-- ============================================

CREATE TRIGGER update_marketplace_connections_timestamp 
AFTER UPDATE ON marketplace_connections
BEGIN
    UPDATE marketplace_connections SET updated_at = strftime('%s', 'now')
    WHERE id = NEW.id;
END;

CREATE TRIGGER update_products_timestamp 
AFTER UPDATE ON products
BEGIN
    UPDATE products SET updated_at = strftime('%s', 'now')
    WHERE id = NEW.id;
END;

CREATE TRIGGER update_listings_timestamp 
AFTER UPDATE ON listings
BEGIN
    UPDATE listings SET updated_at = strftime('%s', 'now')
    WHERE id = NEW.id;
END;

CREATE TRIGGER update_orders_timestamp 
AFTER UPDATE ON orders
BEGIN
    UPDATE orders SET updated_at = strftime('%s', 'now')
    WHERE id = NEW.id;
END;

