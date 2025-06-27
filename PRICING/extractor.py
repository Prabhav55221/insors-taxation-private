#!/usr/bin/env python3
"""
Contract Financial Extraction API

Production-ready FastAPI service for extracting financial terms from PDF contracts
using OpenAI GPT-4o and storing results in PostgreSQL database.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
import json
import tempfile
import shutil
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, DECIMAL, ForeignKey, Date
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import JSONB
import psycopg2

from openai import OpenAI
from pydantic import ValidationError

from models.pricing import ContractExtraction, create_openai_response_format
from config import config


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for database models"""
    pass


class ContractExtractionDB(Base):
    """Main contract extraction table with metadata and full JSON storage"""
    __tablename__ = 'contract_extractions'
    __table_args__ = {'schema': 'pricing'}
    
    id = Column(Integer, primary_key=True)
    document_title = Column(String(500), nullable=False)
    contract_type = Column(String(100), nullable=False)
    effective_date = Column(Date)
    end_date = Column(Date)
    total_pages = Column(Integer)
    governing_law = Column(String(100))
    jurisdiction = Column(String(100))
    
    # Financial summary counts
    total_base_compensation_count = Column(Integer, default=0)
    total_fees_count = Column(Integer, default=0)
    total_royalties_count = Column(Integer, default=0)
    total_equity_count = Column(Integer, default=0)
    total_expenses_count = Column(Integer, default=0)
    total_pricing_rules_count = Column(Integer, default=0)
    
    # Financial characteristics for quick filtering
    has_tiered_structures = Column(Boolean, default=False)
    has_commissions = Column(Boolean, default=False)
    has_asset_based_fees = Column(Boolean, default=False)
    multi_currency_flag = Column(Boolean, default=False)
    primary_currency = Column(String(10))
    
    # Extraction quality metrics
    overall_confidence = Column(DECIMAL(3,2))
    redacted_fields_count = Column(Integer, default=0)
    processing_warnings_count = Column(Integer, default=0)
    model_used = Column(String(50))
    
    # Complete JSON preservation
    contract_metadata_json = Column(JSONB, nullable=False)
    financial_terms_json = Column(JSONB, nullable=False)
    pricing_rules_json = Column(JSONB, nullable=False)
    extraction_metadata_json = Column(JSONB, nullable=False)
    
    # File tracking
    source_file_path = Column(Text)
    source_file_name = Column(String(255))
    source_file_size = Column(Integer)
    file_hash = Column(String(64))
    
    # Timestamps
    extracted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parties = relationship("ContractPartyDB", back_populates="contract", cascade="all, delete-orphan")
    fees = relationship("ContractFeeDB", back_populates="contract", cascade="all, delete-orphan")
    pricing_rules = relationship("PricingRuleDB", back_populates="contract", cascade="all, delete-orphan")


class ContractPartyDB(Base):
    """Normalized contract party information for fast searches"""
    __tablename__ = 'contract_parties'
    __table_args__ = {'schema': 'pricing'}
    
    id = Column(Integer, primary_key=True)
    contract_extraction_id = Column(Integer, ForeignKey('pricing.contract_extractions.id'))
    entity_name = Column(String(300), nullable=False)
    entity_type = Column(String(100))
    role = Column(String(100))
    address = Column(Text)
    jurisdiction = Column(String(100))
    normalized_name = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("ContractExtractionDB", back_populates="parties")


class ContractFeeDB(Base):
    """Contract fee details with analysis flags"""
    __tablename__ = 'contract_fees'
    __table_args__ = {'schema': 'pricing'}
    
    id = Column(Integer, primary_key=True)
    contract_extraction_id = Column(Integer, ForeignKey('pricing.contract_extractions.id'))
    fee_description = Column(Text, nullable=False)
    fee_type = Column(String(100))
    amount_value = Column(Text)
    amount_currency = Column(String(10))
    calculation_method = Column(Text)
    frequency = Column(String(100))
    applies_to = Column(Text)
    
    # Fee characteristics for filtering
    is_tiered = Column(Boolean, default=False)
    is_asset_based = Column(Boolean, default=False)
    is_commission = Column(Boolean, default=False)
    has_minimum = Column(Boolean, default=False)
    has_maximum = Column(Boolean, default=False)
    
    confidence_score = Column(DECIMAL(3,2))
    is_redacted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("ContractExtractionDB", back_populates="fees")


class PricingRuleDB(Base):
    """Business logic pricing rules linked to contracts"""
    __tablename__ = 'pricing_rules'
    __table_args__ = {'schema': 'pricing'}
    
    id = Column(Integer, primary_key=True)
    contract_extraction_id = Column(Integer, ForeignKey('pricing.contract_extractions.id'))
    applies_to_fee_id = Column(Integer, ForeignKey('pricing.contract_fees.id'))
    
    rule_name = Column(String(200), nullable=False)
    rule_description = Column(Text)
    rule_type = Column(String(100))
    triggers = Column(Text)
    calculation_summary = Column(Text)
    applies_to = Column(Text)
    effective_period = Column(String(200))
    
    system_implementable = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    priority = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    contract = relationship("ContractExtractionDB", back_populates="pricing_rules")


from urllib.parse import quote_plus

DATABASE_URL = f"postgresql://{config.db_user}:{quote_plus(config.db_password)}@{config.db_host}:{config.db_port}/{config.db_name}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_database_session():
    """Database session context manager with proper cleanup"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content for deduplication"""
    return hashlib.sha256(file_content).hexdigest()


def normalize_name(name: str) -> str:
    """Normalize entity name for fuzzy matching"""
    return name.lower().strip().replace(',', '').replace('.', '')


def safe_date_parse(date_string: str) -> Optional[datetime.date]:
    """Safely parse date string with error handling"""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        try:
            # Try alternative format
            return datetime.strptime(date_string, '%Y/%m/%d').date()
        except (ValueError, TypeError):
            return None


def analyze_financial_characteristics(financial_terms: dict) -> dict:
    """Analyze financial terms to identify key characteristics for filtering"""
    characteristics = {
        'has_tiered_structures': False,
        'has_commissions': False,
        'has_asset_based_fees': False,
        'multi_currency_flag': False,
        'primary_currency': None
    }
    
    currencies = set()
    
    # Analyze fees for characteristics
    for fee in financial_terms.get('fees', []):
        fee_type = fee.get('fee_type', '').lower()
        calculation = fee.get('calculation_method', '').lower()
        
        if 'tiered' in fee_type or 'tier' in calculation or '%' in calculation:
            characteristics['has_tiered_structures'] = True
        
        if 'commission' in fee_type:
            characteristics['has_commissions'] = True
            
        if 'asset' in fee_type or 'asset' in calculation:
            characteristics['has_asset_based_fees'] = True
            
        currency = fee.get('amount', {}).get('currency')
        if currency:
            currencies.add(currency)
    
    # Check base compensation currencies
    for comp in financial_terms.get('base_compensation', []):
        currency = comp.get('amount', {}).get('currency')
        if currency:
            currencies.add(currency)
    
    if len(currencies) > 1:
        characteristics['multi_currency_flag'] = True
    
    if currencies:
        characteristics['primary_currency'] = list(currencies)[0]
    
    return characteristics


class ContractExtractor:
    """Main contract extraction service using OpenAI GPT-4o"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize extractor with OpenAI client"""
        self.client = OpenAI(api_key=api_key or config.openai_api_key)
        self.model = config.openai_model
        
    def load_prompt(self, prompt_path: str) -> str:
        """Load prompt file with error handling"""
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        except Exception as e:
            raise Exception(f"Error loading prompt from {prompt_path}: {e}")
    
    def extract_from_file(self, 
                         file_content: bytes,
                         filename: str,
                         max_retries: int = None) -> ContractExtraction:
        """Extract financial terms from PDF file using OpenAI GPT-4o"""
        
        max_retries = max_retries or config.max_retries
        
        print(f"Starting extraction for: {filename}")
        
        # Load prompts
        print("Loading prompts...")
        system_prompt = self.load_prompt(config.system_prompt_path)
        user_prompt = self.load_prompt(config.user_prompt_path)
        
        # Upload file to OpenAI
        print("Uploading file to OpenAI...")
        temp_path = None
        try:
            if not filename.lower().endswith('.pdf'):
                raise Exception(f"File must have .pdf extension: {filename}")
            
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, filename)
            
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            
            with open(temp_path, 'rb') as f:
                file_response = self.client.files.create(
                    file=f,
                    purpose='assistants'
                )
            
        finally:
            if temp_path and os.path.exists(temp_path):
                shutil.rmtree(os.path.dirname(temp_path))
        
        file_id = file_response.id
        response_format = create_openai_response_format()
        
        # Prepare messages for GPT-4o
        messages = [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "file",
                        "file": {
                            "file_id": file_id
                        }
                    }
                ]
            }
        ]
        
        # Call OpenAI with retries
        for attempt in range(max_retries):
            try:
                print(f"Calling OpenAI GPT-4o (attempt {attempt + 1}/{max_retries})...")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format=response_format,
                    temperature=0.1,
                    max_tokens=8192
                )
                
                content = response.choices[0].message.content
                
                if not content:
                    raise Exception("Empty response from OpenAI")
                
                # Parse and validate response
                extraction_data = json.loads(content)
                extraction = ContractExtraction(**extraction_data)
                
                print("Extraction completed successfully!")
                
                # Cleanup OpenAI file
                try:
                    self.client.files.delete(file_id)
                except:
                    pass
                    
                return extraction
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to parse OpenAI response as JSON after {max_retries} attempts")
                    
            except ValidationError as e:
                print(f"Schema validation error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"OpenAI response doesn't match schema after {max_retries} attempts")
                    
            except Exception as e:
                print(f"API error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    try:
                        self.client.files.delete(file_id)
                    except:
                        pass
                    raise Exception(f"API call failed after {max_retries} attempts: {e}")
        
        raise Exception("Extraction failed after all retry attempts")
        
    def save_results(self, extraction: ContractExtraction, output_path: str) -> None:
        """Save extraction results to JSON file"""
        try:
            output_data = extraction.model_dump()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
            print(f"JSON results saved to: {output_path}")
            
        except Exception as e:
            raise Exception(f"Error saving results to {output_path}: {e}")
    
    def save_to_database(self, extraction: ContractExtraction, filename: str, file_content: bytes) -> int:
        """Save extraction results to PostgreSQL database"""
        
        with get_database_session() as db:
            try:
                file_hash = calculate_file_hash(file_content)
                file_size = len(file_content)
                
                # Convert to dictionaries for processing
                metadata = extraction.contract_metadata.model_dump()
                financial_terms = extraction.financial_terms.model_dump()
                pricing_rules = extraction.pricing_rules.model_dump()
                extraction_metadata = extraction.extraction_metadata.model_dump()
                
                # Analyze financial characteristics
                characteristics = analyze_financial_characteristics(financial_terms)
                
                # Parse dates safely
                effective_date = safe_date_parse(metadata.get('effective_date'))
                end_date = safe_date_parse(metadata.get('end_date'))
                
                # Create main contract record
                contract_db = ContractExtractionDB(
                    document_title=metadata.get('document_title', ''),
                    contract_type=metadata.get('contract_type', ''),
                    effective_date=effective_date,
                    end_date=end_date,
                    total_pages=metadata.get('total_pages', 0),
                    governing_law=metadata.get('governing_law', ''),
                    jurisdiction=metadata.get('jurisdiction', ''),
                    
                    # Financial summary counts
                    total_base_compensation_count=len(financial_terms.get('base_compensation', [])),
                    total_fees_count=len(financial_terms.get('fees', [])),
                    total_royalties_count=len(financial_terms.get('royalties', [])),
                    total_equity_count=len(financial_terms.get('equity_compensation', [])),
                    total_expenses_count=len(financial_terms.get('expenses', [])),
                    total_pricing_rules_count=len(pricing_rules.get('rules', [])),
                    
                    # Financial characteristics
                    has_tiered_structures=characteristics['has_tiered_structures'],
                    has_commissions=characteristics['has_commissions'],
                    has_asset_based_fees=characteristics['has_asset_based_fees'],
                    multi_currency_flag=characteristics['multi_currency_flag'],
                    primary_currency=characteristics['primary_currency'],
                    
                    # Quality metrics
                    overall_confidence=extraction_metadata.get('overall_confidence', 0.0),
                    redacted_fields_count=extraction_metadata.get('redacted_fields_count', 0),
                    processing_warnings_count=len(extraction_metadata.get('processing_warnings', [])),
                    model_used=extraction_metadata.get('model_used', ''),
                    
                    # Full JSON preservation
                    contract_metadata_json=metadata,
                    financial_terms_json=financial_terms,
                    pricing_rules_json=pricing_rules,
                    extraction_metadata_json=extraction_metadata,
                    
                    # File information
                    source_file_name=filename,
                    source_file_size=file_size,
                    file_hash=file_hash
                )
                
                db.add(contract_db)
                db.flush()  # Get the ID
                
                # Save contract parties
                for party in metadata.get('parties', []):
                    party_db = ContractPartyDB(
                        contract_extraction_id=contract_db.id,
                        entity_name=party.get('entity_name', ''),
                        entity_type=party.get('entity_type', ''),
                        role=party.get('role', ''),
                        address=party.get('address', ''),
                        jurisdiction=party.get('jurisdiction', ''),
                        normalized_name=normalize_name(party.get('entity_name', ''))
                    )
                    db.add(party_db)
                
                # Save fee details
                for fee in financial_terms.get('fees', []):
                    fee_type = fee.get('fee_type', '').lower()
                    calculation = fee.get('calculation_method', '').lower()
                    
                    fee_db = ContractFeeDB(
                        contract_extraction_id=contract_db.id,
                        fee_description=fee.get('description', ''),
                        fee_type=fee.get('fee_type', ''),
                        amount_value=str(fee.get('amount', {}).get('value', '')),
                        amount_currency=fee.get('amount', {}).get('currency', ''),
                        calculation_method=fee.get('calculation_method', ''),
                        frequency=fee.get('frequency', ''),
                        applies_to=fee.get('applies_to', ''),
                        
                        # Analysis flags
                        is_tiered='tiered' in fee_type or 'tier' in calculation,
                        is_asset_based='asset' in fee_type or 'asset' in calculation,
                        is_commission='commission' in fee_type,
                        has_minimum=bool(fee.get('minimum_amount', {}).get('value')),
                        has_maximum=bool(fee.get('maximum_amount', {}).get('value')),
                        is_redacted=fee.get('amount', {}).get('is_redacted', False)
                    )
                    db.add(fee_db)
                
                # Save pricing rules
                for rule in pricing_rules.get('rules', []):
                    rule_db = PricingRuleDB(
                        contract_extraction_id=contract_db.id,
                        rule_name=rule.get('rule_name', ''),
                        rule_description=rule.get('rule_description', ''),
                        rule_type=rule.get('rule_type', ''),
                        triggers=rule.get('triggers', ''),
                        calculation_summary=rule.get('calculation', ''),
                        applies_to=rule.get('applies_to', ''),
                        effective_period=rule.get('effective_period', '')
                    )
                    db.add(rule_db)
                
                db.commit()
                print(f"Database save completed with ID: {contract_db.id}")
                return contract_db.id
                
            except Exception as e:
                db.rollback()
                raise Exception(f"Database save failed: {e}")


# Initialize FastAPI app and extractor
app = FastAPI(title="Contract Financial Extraction API", version="1.0.0")
extractor = ContractExtractor()


@app.post("/extract/single")
async def extract_single_contract(file: UploadFile = File(...)):
    """Extract financial terms from a single PDF contract"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        file_content = await file.read()
        
        # Extract using OpenAI
        extraction = extractor.extract_from_file(file_content, file.filename)
        
        # Save to database first
        db_id = extractor.save_to_database(extraction, file.filename, file_content)
        
        # Save JSON file with database ID in filename
        filename_stem = Path(file.filename).stem
        output_filename = f"{db_id}_{filename_stem}_extraction.json"
        output_path = os.path.join(config.default_output_dir, output_filename)
        extractor.save_results(extraction, output_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "database_id": db_id,
            "output_path": output_path,
            "extraction": extraction.model_dump()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.post("/extract/multiple")
async def extract_multiple_contracts(files: List[UploadFile] = File(...)):
    """Extract financial terms from multiple PDF contracts"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    errors = []
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            errors.append(f"{file.filename}: Only PDF files are supported")
            continue
            
        try:
            file_content = await file.read()
            
            # Extract using OpenAI
            extraction = extractor.extract_from_file(file_content, file.filename)
            
            # Save to database
            db_id = extractor.save_to_database(extraction, file.filename, file_content)
            
            # Save JSON file
            filename_stem = Path(file.filename).stem
            output_filename = f"{db_id}_{filename_stem}_extraction.json"
            output_path = os.path.join(config.default_output_dir, output_filename)
            extractor.save_results(extraction, output_path)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "database_id": db_id,
                "output_path": output_path,
                "extraction": extraction.model_dump()
            })
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total_files": len(files),
        "successful": len([r for r in results if r.get("status") == "success"]),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity test"""
    try:
        with get_database_session() as db:
            db.execute("SELECT 1")
        return {
            "status": "healthy", 
            "service": "contract-extraction-api",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "contract-extraction-api", 
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/config")
async def get_config():
    """Get current configuration settings"""
    return {
        "model": config.openai_model,
        "max_retries": config.max_retries,
        "output_dir": config.default_output_dir,
        "api_key_configured": bool(config.openai_api_key),
        "database_url": f"{config.db_host}:{config.db_port}/{config.db_name}"
    }


@app.get("/extractions/{extraction_id}")
async def get_extraction(extraction_id: int):
    """Get specific extraction by database ID"""
    with get_database_session() as db:
        extraction = db.query(ContractExtractionDB).filter(ContractExtractionDB.id == extraction_id).first()
        if not extraction:
            raise HTTPException(status_code=404, detail="Extraction not found")
        
        return {
            "id": extraction.id,
            "document_title": extraction.document_title,
            "contract_type": extraction.contract_type,
            "confidence": float(extraction.overall_confidence),
            "file_name": extraction.source_file_name,
            "extracted_at": extraction.extracted_at,
            "metadata": extraction.contract_metadata_json,
            "financial_terms": extraction.financial_terms_json,
            "pricing_rules": extraction.pricing_rules_json
        }


@app.get("/extractions")
async def list_extractions(limit: int = 10, offset: int = 0):
    """List recent extractions with pagination"""
    with get_database_session() as db:
        extractions = db.query(ContractExtractionDB).order_by(ContractExtractionDB.created_at.desc()).offset(offset).limit(limit).all()
        return {
            "extractions": [
                {
                    "id": e.id,
                    "document_title": e.document_title,
                    "contract_type": e.contract_type,
                    "confidence": float(e.overall_confidence),
                    "extracted_at": e.extracted_at,
                    "file_name": e.source_file_name
                }
                for e in extractions
            ]
        }


if __name__ == "__main__":
    if not config.openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    
    # Ensure output directory exists
    os.makedirs(config.default_output_dir, exist_ok=True)
    
    print(f"Starting Contract Extraction API on port 8000")
    print(f"Database: {config.db_host}:{config.db_port}/{config.db_name}")
    print(f"Output directory: {config.default_output_dir}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)