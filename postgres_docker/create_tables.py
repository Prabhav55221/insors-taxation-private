#!/usr/bin/env python3

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from PRICING.config import config


CREATE_SCHEMA_SQL = """
-- Create pricing schema for our tables
CREATE SCHEMA IF NOT EXISTS pricing;
SET search_path TO pricing;
"""

CREATE_TABLES_SQL = """
-- Main contract extractions table
CREATE TABLE IF NOT EXISTS contract_extractions (
    id SERIAL PRIMARY KEY,
    
    -- Searchable metadata fields
    document_title VARCHAR(500) NOT NULL,
    contract_type VARCHAR(100) NOT NULL,
    effective_date DATE,
    end_date DATE,
    total_pages INTEGER,
    governing_law VARCHAR(100),
    jurisdiction VARCHAR(100),
    
    -- Financial summary (derived fields for quick queries)
    total_base_compensation_count INTEGER DEFAULT 0,
    total_fees_count INTEGER DEFAULT 0,
    total_royalties_count INTEGER DEFAULT 0,
    total_equity_count INTEGER DEFAULT 0,
    total_expenses_count INTEGER DEFAULT 0,
    total_pricing_rules_count INTEGER DEFAULT 0,
    
    -- Financial flags for quick filtering
    has_tiered_structures BOOLEAN DEFAULT FALSE,
    has_commissions BOOLEAN DEFAULT FALSE,
    has_asset_based_fees BOOLEAN DEFAULT FALSE,
    multi_currency_flag BOOLEAN DEFAULT FALSE,
    primary_currency VARCHAR(10),
    
    -- Extraction quality metrics
    overall_confidence DECIMAL(3,2) CHECK (overall_confidence >= 0 AND overall_confidence <= 1),
    redacted_fields_count INTEGER DEFAULT 0,
    processing_warnings_count INTEGER DEFAULT 0,
    model_used VARCHAR(50),
    
    -- Full JSON data preservation
    contract_metadata_json JSONB NOT NULL,
    financial_terms_json JSONB NOT NULL,
    pricing_rules_json JSONB NOT NULL,
    extraction_metadata_json JSONB NOT NULL,
    
    -- File and processing info
    source_file_path TEXT,
    source_file_name VARCHAR(255),
    source_file_size BIGINT,
    file_hash VARCHAR(64),
    
    -- Timestamps
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contract parties (normalized for easy searching)
CREATE TABLE IF NOT EXISTS contract_parties (
    id SERIAL PRIMARY KEY,
    contract_extraction_id INTEGER REFERENCES contract_extractions(id) ON DELETE CASCADE,
    
    entity_name VARCHAR(300) NOT NULL,
    entity_type VARCHAR(100),
    role VARCHAR(100),
    address TEXT,
    jurisdiction VARCHAR(100),
    
    -- Normalized name for fuzzy matching
    normalized_name VARCHAR(300),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Contract fees (most frequently queried financial data)
CREATE TABLE IF NOT EXISTS contract_fees (
    id SERIAL PRIMARY KEY,
    contract_extraction_id INTEGER REFERENCES contract_extractions(id) ON DELETE CASCADE,
    
    fee_description TEXT NOT NULL,
    fee_type VARCHAR(100),
    amount_value TEXT,
    amount_currency VARCHAR(10),
    calculation_method TEXT,
    frequency VARCHAR(100),
    applies_to TEXT,
    
    -- Fee characteristics for filtering
    is_tiered BOOLEAN DEFAULT FALSE,
    is_asset_based BOOLEAN DEFAULT FALSE,
    is_commission BOOLEAN DEFAULT FALSE,
    has_minimum BOOLEAN DEFAULT FALSE,
    has_maximum BOOLEAN DEFAULT FALSE,
    
    -- Quality metrics
    confidence_score DECIMAL(3,2),
    is_redacted BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pricing rules (business logic implementation tracking)
CREATE TABLE IF NOT EXISTS pricing_rules (
    id SERIAL PRIMARY KEY,
    contract_extraction_id INTEGER REFERENCES contract_extractions(id) ON DELETE CASCADE,
    applies_to_fee_id INTEGER REFERENCES contract_fees(id) ON DELETE SET NULL,
    
    rule_name VARCHAR(200) NOT NULL,
    rule_description TEXT,
    rule_type VARCHAR(100),
    triggers TEXT,
    calculation_summary TEXT,
    applies_to TEXT,
    effective_period VARCHAR(200),
    
    -- Implementation flags
    system_implementable BOOLEAN DEFAULT TRUE,
    requires_approval BOOLEAN DEFAULT FALSE,
    priority INTEGER CHECK (priority >= 1 AND priority <= 10),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- File processing tracking
CREATE TABLE IF NOT EXISTS extraction_jobs (
    id SERIAL PRIMARY KEY,
    contract_extraction_id INTEGER REFERENCES contract_extractions(id) ON DELETE SET NULL,
    
    file_path TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT,
    file_hash VARCHAR(64),
    
    -- Processing status
    processing_status VARCHAR(50) DEFAULT 'pending',
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_error TEXT,
    processing_time_seconds DECIMAL(10,3),
    
    -- OpenAI tracking
    openai_file_id VARCHAR(100),
    model_used VARCHAR(50),
    retry_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_INDEXES_SQL = """
-- Performance indexes for contract_extractions
CREATE INDEX IF NOT EXISTS idx_contract_extractions_type ON contract_extractions(contract_type);
CREATE INDEX IF NOT EXISTS idx_contract_extractions_dates ON contract_extractions(effective_date, end_date);
CREATE INDEX IF NOT EXISTS idx_contract_extractions_confidence ON contract_extractions(overall_confidence);
CREATE INDEX IF NOT EXISTS idx_contract_extractions_created ON contract_extractions(created_at);
CREATE INDEX IF NOT EXISTS idx_contract_extractions_file_hash ON contract_extractions(file_hash);

-- Financial flags for quick filtering
CREATE INDEX IF NOT EXISTS idx_contract_extractions_tiered ON contract_extractions(has_tiered_structures);
CREATE INDEX IF NOT EXISTS idx_contract_extractions_commissions ON contract_extractions(has_commissions);
CREATE INDEX IF NOT EXISTS idx_contract_extractions_currency ON contract_extractions(primary_currency);

-- Party search indexes
CREATE INDEX IF NOT EXISTS idx_contract_parties_name ON contract_parties(entity_name);
CREATE INDEX IF NOT EXISTS idx_contract_parties_normalized ON contract_parties(normalized_name);
CREATE INDEX IF NOT EXISTS idx_contract_parties_role ON contract_parties(role);
CREATE INDEX IF NOT EXISTS idx_contract_parties_contract ON contract_parties(contract_extraction_id);

-- Fee analysis indexes
CREATE INDEX IF NOT EXISTS idx_contract_fees_type ON contract_fees(fee_type);
CREATE INDEX IF NOT EXISTS idx_contract_fees_currency ON contract_fees(amount_currency);
CREATE INDEX IF NOT EXISTS idx_contract_fees_characteristics ON contract_fees(is_tiered, is_asset_based, is_commission);
CREATE INDEX IF NOT EXISTS idx_contract_fees_contract ON contract_fees(contract_extraction_id);

-- Pricing rules indexes
CREATE INDEX IF NOT EXISTS idx_pricing_rules_type ON pricing_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_pricing_rules_contract ON pricing_rules(contract_extraction_id);
CREATE INDEX IF NOT EXISTS idx_pricing_rules_fee ON pricing_rules(applies_to_fee_id);

-- Job processing indexes
CREATE INDEX IF NOT EXISTS idx_extraction_jobs_hash ON extraction_jobs(file_hash);
CREATE INDEX IF NOT EXISTS idx_extraction_jobs_status ON extraction_jobs(processing_status);
CREATE INDEX IF NOT EXISTS idx_extraction_jobs_created ON extraction_jobs(created_at);

-- JSON indexes for complex queries
CREATE INDEX IF NOT EXISTS idx_contract_extractions_metadata_gin ON contract_extractions USING GIN (contract_metadata_json);
CREATE INDEX IF NOT EXISTS idx_contract_extractions_financial_gin ON contract_extractions USING GIN (financial_terms_json);
CREATE INDEX IF NOT EXISTS idx_contract_extractions_pricing_gin ON contract_extractions USING GIN (pricing_rules_json);
"""

CREATE_VIEWS_SQL = """
-- Contract summary view for analytics
CREATE OR REPLACE VIEW contract_summary AS
SELECT 
    contract_type,
    COUNT(*) as total_contracts,
    AVG(overall_confidence) as avg_confidence,
    SUM(total_fees_count) as total_fee_structures,
    SUM(total_pricing_rules_count) as total_pricing_rules,
    COUNT(*) FILTER (WHERE has_tiered_structures = true) as contracts_with_tiers,
    COUNT(*) FILTER (WHERE has_commissions = true) as contracts_with_commissions,
    COUNT(*) FILTER (WHERE multi_currency_flag = true) as multi_currency_contracts
FROM contract_extractions 
GROUP BY contract_type
ORDER BY total_contracts DESC;

-- Fee type analysis view
CREATE OR REPLACE VIEW fee_type_analysis AS  
SELECT 
    fee_type,
    COUNT(*) as frequency,
    AVG(confidence_score) as avg_confidence,
    COUNT(*) FILTER (WHERE is_tiered = true) as tiered_count,
    COUNT(*) FILTER (WHERE is_asset_based = true) as asset_based_count,
    COUNT(*) FILTER (WHERE is_commission = true) as commission_count
FROM contract_fees
WHERE fee_type IS NOT NULL
GROUP BY fee_type
ORDER BY frequency DESC;

-- Processing stats view
CREATE OR REPLACE VIEW processing_stats AS
SELECT 
    processing_status,
    COUNT(*) as job_count,
    AVG(processing_time_seconds) as avg_processing_time,
    AVG(file_size) as avg_file_size,
    COUNT(*) FILTER (WHERE retry_count > 0) as jobs_with_retries
FROM extraction_jobs
GROUP BY processing_status;

-- Recent extractions view
CREATE OR REPLACE VIEW recent_extractions AS
SELECT 
    ce.id,
    ce.document_title,
    ce.contract_type,
    ce.overall_confidence,
    ce.total_fees_count,
    ce.total_pricing_rules_count,
    ce.extracted_at,
    ej.processing_time_seconds
FROM contract_extractions ce
LEFT JOIN extraction_jobs ej ON ce.id = ej.contract_extraction_id
ORDER BY ce.extracted_at DESC
LIMIT 50;
"""

GRANT_PERMISSIONS_SQL = """
-- Grant permissions to the application user
GRANT USAGE ON SCHEMA pricing TO insors_demo;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA pricing TO insors_demo;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA pricing TO insors_demo;
GRANT SELECT ON ALL TABLES IN SCHEMA pricing TO insors_demo;
"""


def create_database_schema():
    """Create the complete database schema for contract extractions"""
    
    connection_params = {
        'host': config.db_host,
        'port': config.db_port,
        'database': config.db_name,
        'user': config.db_user,
        'password': config.db_password
    }
    
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**connection_params)
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            print("Creating schema...")
            cursor.execute(CREATE_SCHEMA_SQL)
            
            print("Creating tables...")
            cursor.execute(CREATE_TABLES_SQL)
            
            print("Creating indexes...")
            cursor.execute(CREATE_INDEXES_SQL)
            
            print("Creating views...")
            cursor.execute(CREATE_VIEWS_SQL)
            
            print("Setting permissions...")
            cursor.execute(GRANT_PERMISSIONS_SQL)
        
        print("Database schema created successfully!")
        
        # Test the setup
        print("\nTesting schema...")
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'pricing'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"Created tables: {[t['table_name'] for t in tables]}")
            
            cursor.execute("""
                SELECT viewname 
                FROM pg_views 
                WHERE schemaname = 'pricing'
                ORDER BY viewname
            """)
            views = cursor.fetchall()
            print(f"Created views: {[v['viewname'] for v in views]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating database schema: {e}")
        return False


if __name__ == "__main__":
    print("Setting up Contract Extraction Database Schema...")
    print(f"Database: {config.db_host}:{config.db_port}/{config.db_name}")
    
    success = create_database_schema()
    
    if success:
        print("\nDatabase setup completed successfully!")
    else:
        print("\nDatabase setup failed!")
        sys.exit(1)