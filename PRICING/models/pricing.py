from datetime import datetime
from enum import Enum
from typing import List, Union, Optional
from pydantic import BaseModel


class MonetaryAmount(BaseModel):
    value: Union[str, float, int]
    currency: str
    is_redacted: bool
    redaction_pattern: str


class ContractParty(BaseModel):
    entity_name: str
    entity_type: str
    role: str
    address: str
    jurisdiction: str
    

class PaymentTiming(BaseModel):
    due_date: str
    grace_period: str
    late_fees: str
    payment_method: str


class ContractMetadata(BaseModel):
    document_title: str
    contract_type: str
    effective_date: str
    end_date: str
    parties: List[ContractParty]
    total_pages: int
    governing_law: str
    jurisdiction: str


class BaseCompensation(BaseModel):
    description: str
    amount: MonetaryAmount
    payment_type: str
    frequency: str
    calculation_method: str
    conditions: str
    payment_timing: PaymentTiming


class RoyaltyTerm(BaseModel):
    description: str
    rate: str
    calculation_base: str
    minimum_amount: str
    maximum_amount: str
    product_scope: str
    territory: str
    special_terms: str


class FeeTerm(BaseModel):
    description: str
    fee_type: str
    amount: MonetaryAmount
    calculation_method: str
    frequency: str
    applies_to: str
    minimum_amount: MonetaryAmount
    maximum_amount: MonetaryAmount


class EquityTerm(BaseModel):
    description: str
    instrument_type: str
    quantity: Union[int, str]
    share_price: Union[float, str]
    vesting_terms: str
    conversion_rights: str


class ExpenseTerm(BaseModel):
    category: str
    coverage: str
    amount_limit: MonetaryAmount
    approval_required: bool
    reimbursement_terms: str


class FinancialTerms(BaseModel):
    base_compensation: List[BaseCompensation]
    royalties: List[RoyaltyTerm]
    fees: List[FeeTerm]
    equity_compensation: List[EquityTerm]
    expenses: List[ExpenseTerm]


class PricingRule(BaseModel):
    rule_name: str
    rule_description: str
    rule_type: str
    triggers: str
    calculation: str
    applies_to: str
    effective_period: str


class PricingRules(BaseModel):
    rules: List[PricingRule]


class ExtractionMetadata(BaseModel):
    extraction_timestamp: str
    model_used: str
    overall_confidence: float
    redacted_fields_count: int
    extraction_notes: str
    processing_warnings: List[str]


class ContractExtraction(BaseModel):
    contract_metadata: ContractMetadata
    financial_terms: FinancialTerms
    pricing_rules: PricingRules
    extraction_metadata: ExtractionMetadata
    
    class Config:
        extra = "forbid"


def get_json_schema() -> dict:
    return ContractExtraction.model_json_schema()


def create_openai_response_format() -> dict:
    schema = get_json_schema()
    
    def add_additional_properties_false(obj):
        if isinstance(obj, dict):
            if obj.get("type") == "object":
                obj["additionalProperties"] = False
            for value in obj.values():
                add_additional_properties_false(value)
        elif isinstance(obj, list):
            for item in obj:
                add_additional_properties_false(item)
    
    add_additional_properties_false(schema)
    
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "contract_extraction",
            "schema": schema,
            "strict": True
        }
    }