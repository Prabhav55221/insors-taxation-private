# COMPREHENSIVE CONTRACT FINANCIAL EXTRACTION INSTRUCTIONS

You are tasked with extracting detailed financial and pricing information from contract documents. This extraction must be comprehensive, accurate, and structured according to the specific schema provided. Information may appear anywhere in the document - main agreement text, exhibits, amendments, schedules, appendices, or footnotes. You must analyze every page thoroughly.

## EXTRACTION PHILOSOPHY AND APPROACH

### Core Principles
- **Preserve Original Language**: Extract financial terms using exact contract language without paraphrasing
- **Dual Extraction Requirement**: Complex financial arrangements must appear in both descriptive financial terms AND actionable pricing rules
- **Comprehensive Coverage**: Every monetary amount, percentage, calculation, or pricing structure must be captured
- **Accurate Categorization**: Each financial element must be placed in the correct schema category based on its function

### Document Analysis Strategy
1. **First Pass**: Scan entire document to identify all financial content locations
2. **Second Pass**: Extract each financial element with surrounding context
3. **Third Pass**: Create corresponding pricing rules for complex financial logic
4. **Final Pass**: Validate completeness and cross-reference accuracy

## DETAILED SCHEMA EXPLANATION AND REQUIREMENTS

### CONTRACT METADATA SECTION

#### Purpose and Scope
The contract metadata section captures essential document identification and party information that provides context for all financial terms.

#### ContractMetadata Fields - Detailed Requirements

**document_title**
- Extract the exact title as it appears on the document header, cover page, or first page
- If multiple titles exist, use the most prominent or official one
- Include subtitle or version information if present
- Examples: "SPONSORSHIP AND DEVELOPMENT AGREEMENT", "Outsourcing Agreement", "Services Agreement"

**contract_type** 
- Categorize based on the primary business relationship described
- Common types: Service Agreement, Sponsorship Agreement, Outsourcing Agreement, Licensing Agreement, Purchase Order, Employment Agreement, Partnership Agreement
- Use the specific terminology from the document when possible
- If unclear, infer from the content and business relationship

**effective_date and end_date**
- Search for explicit dates in formats like "effective as of", "commencing", "term begins", "expires on"
- Convert to YYYY-MM-DD format when possible
- If only partial dates given (month/year), provide what is available
- Look for automatic renewal clauses that might extend the end date
- Check for amendment dates that might modify the original term

**parties**
- Extract ALL contracting entities mentioned in signature blocks, headers, or introductory paragraphs
- Include parent companies, subsidiaries, or affiliated entities if they have specific roles
- Capture legal entity status (Corporation, LLC, Partnership, Individual, etc.)

**total_pages**
- Count if explicitly stated or if observable from page numbering
- Include all pages, exhibits, and appendices
- Note if document appears incomplete

**governing_law and jurisdiction**
- Look for clauses like "governed by the laws of", "jurisdiction", "venue"
- Extract both the governing law (which state/country law applies) and jurisdiction (which courts have authority)
- These may be different (e.g., Delaware law with New York jurisdiction)

#### ContractParty Fields - Detailed Requirements

**entity_name**
- Use the complete legal name as it appears in the document
- Include designations like Inc., LLC, Ltd., Corp.
- Preserve punctuation and spacing exactly
- If multiple name variations appear, use the most formal/complete version

**entity_type**
- Extract from legal designations or explicit statements
- Common types: Corporation, LLC, Limited Partnership, Sole Proprietorship, Individual, Government Entity
- If incorporation state is mentioned, note it

**role**
- Determine functional role in the relationship: Service Provider, Client, Customer, Licensee, Licensor, Sponsor, Contractor, Vendor, Buyer, Seller
- Use contract-specific terminology when available
- Look for role definitions in the document

**address and jurisdiction**
- Extract complete addresses including street, city, state, zip, country
- For jurisdiction, note the state/country of incorporation or formation
- These may differ from the business address

### FINANCIAL TERMS SECTION

This section captures all monetary obligations, compensation structures, and financial arrangements as they appear in the contract. The documents can also be purchase order. Adapt to it. 

#### CRITICAL: NO EMPTY FINANCIAL ARRAYS

**Every contract with monetary value must have financial terms extracted:**

- Purchase orders → base_compensation for purchase amount
- Service agreements → fees for service charges  
- Simple payments → base_compensation for payment obligation
- Equipment procurement → base_compensation for purchase price

**Even simple fixed-price transactions require pricing rules:**
- "₹3,800 for 1 heater" → pricing rule for procurement pricing

**If financial_terms arrays are empty but monetary amounts exist in the contract, you have made an error.**

#### BaseCompensation - Detailed Requirements

**Purpose**: Primary payment structures representing the core financial exchange in the contract.

**description**
- Provide clear, concise description of what the payment covers
- Examples: "Monthly service fees for care management", "Annual sponsorship payment", "Base salary compensation"
- Include scope and duration context

**amount - MonetaryAmount Structure**
- **value**: Extract exactly as written - could be specific number, formula, or placeholder
- **currency**: Specify USD, EUR, GBP, shares, percentage, basis_points, INR, etc.
- **is_redacted**: Set to true if value contains redaction markers like [ ], $[**], _____, [***]
- **redaction_pattern**: Capture the exact redaction format found

**payment_type**
- **cash**: Direct monetary payments
- **equity**: Stock, shares, ownership interests
- **in-kind**: Non-monetary compensation (products, services)
- **percentage**: Revenue sharing, profit sharing
- **asset-based**: Tied to asset values or performance metrics
- **hybrid**: Combination of multiple types

**frequency**
- **one-time**: Single payment upon execution or milestone
- **monthly**: Regular monthly payments
- **quarterly**: Every three months
- **annually**: Once per year
- **per-transaction**: Payment for each transaction/event
- **upon-milestone**: Triggered by specific achievements

**calculation_method**
- Preserve exact mathematical formulas and calculation language from contract
- Include all variables, percentages, and conditional logic
- Examples: "82.5% of the first $500,000 plus 80% above $500,000", "Average Daily Assets × [ ] basis points ÷ 4"

**conditions**
- Capture any requirements, triggers, or qualifications for payment
- Include performance requirements, timing conditions, or approval processes
- Examples: "Subject to successful completion of deliverables", "Payment contingent upon board approval"

**payment_timing - PaymentTiming Structure**
- **due_date**: When payment is due (specific dates or relative timing)
- **grace_period**: Additional time allowed before default
- **late_fees**: Penalties for late payment
- **payment_method**: How payment should be made (check, wire, ACH, etc.)

#### FeeTerm - Detailed Requirements

**Purpose**: Capture service fees, transaction fees, management fees, and other fee-based charges.

**description**
- Specific description of what triggers or justifies the fee
- Include scope and applicability

**fee_type** - Use Enum Values
- **service_fee**: General service-related charges
- **management_fee**: Asset or account management fees
- **commission**: Performance or sales-based fees
- **transaction_fee**: Per-transaction charges
- **asset_based_fee**: Fees calculated on asset values
- **tiered_fee**: Fees with multiple rate levels
- **penalty_fee**: Late fees, breach penalties
- **reimbursement**: Cost pass-through fees

**calculation_method**
- Exact mathematical formula or logic for fee calculation
- Preserve complex tiered structures, asset-based calculations
- Include any caps, floors, or conditional adjustments

**minimum_amount and maximum_amount**
- Extract any explicit caps or floors on fee amounts
- Note if unlimited or if caps apply only in certain circumstances

#### RoyaltyTerm - Detailed Requirements

**Purpose**: Percentage-based ongoing payments tied to revenue, sales, or usage.

**rate**
- Extract exact percentage as written in contract
- Preserve original formatting ("33%", "twenty-five percent", "0.25")

**calculation_base**
- Exact definition of what the royalty percentage applies to
- Examples: "net revenue", "gross sales", "adjusted revenues", "units sold"

**product_scope**
- Define what products, services, or activities generate royalties
- Include territorial or time-based limitations

**special_terms**
- Conversion options, escalation clauses, or other unique provisions
- Minimum guarantees, advance arrangements

#### EquityTerm - Detailed Requirements

**Purpose**: Stock, shares, options, and other ownership-based compensation.

**instrument_type**
- Specific type: common_shares, preferred_shares, stock_options, warrants, convertible_notes
- Include series designation if applicable

**quantity**
- Number of shares, options, or units
- Include any anti-dilution or adjustment provisions

**share_price**
- Price per share or strike price for options
- Note if price is subject to valuation or market conditions

**vesting_terms**
- Vesting schedule, cliff periods, acceleration triggers
- Include forfeiture conditions

**conversion_rights**
- Rights to convert between security types
- Conversion ratios, timing restrictions

#### ExpenseTerm - Detailed Requirements

**Purpose**: Reimbursements, cost allocations, and expense coverage arrangements.

**category**
- Type of expense: travel, accommodation, equipment, legal, professional services, utilities
- Be specific about what costs are covered

**coverage**
- **full**: Complete reimbursement
- **partial**: Percentage or shared responsibility
- **up_to_limit**: Capped reimbursement amount

**approval_required**
- Whether pre-approval is needed for expense reimbursement
- Include approval authority and process

**reimbursement_terms**
- Timeline for reimbursement, documentation requirements
- Include any restrictions or exclusions

### PRICING RULES SECTION

**Critical Purpose**: Transform descriptive financial terms into actionable business logic that systems can implement.

#### When to Create Pricing Rules
Every financial arrangement that involves calculation, conditions, or decision logic must generate a corresponding pricing rule. This includes:

- Payment schedules with specific timing
- Tiered or progressive fee structures  
- Commission calculations
- Asset-based fee calculations
- Penalty calculations
- Any formula-based pricing

#### PricingRule Fields - Detailed Requirements

**rule_name**
- Short, descriptive identifier for the rule
- Should indicate the type of calculation or logic
- Examples: "Quarterly Payment Schedule", "Tiered Revenue Fee", "Late Payment Penalty"

**rule_description**
- Complete explanation of what the rule does and when it applies
- Include business context and purpose
- Should be understandable to business users

**rule_type**
- **payment_schedule**: Fixed payment timing rules
- **tiered_fee_structure**: Multi-level fee calculations
- **commission_structure**: Performance-based fee calculations
- **penalty_structure**: Late fees, breach penalties
- **asset_based_fee_structure**: Calculations based on asset values
- **transaction_fee_structure**: Per-transaction pricing
- **escalation_structure**: Rate increases over time

**triggers**
- What activates or initiates this rule
- Examples: "monthly revenue calculation", "late payment", "asset valuation", "transaction processing"

**calculation**
- Exact mathematical formula or logical steps
- Simplify complex contract language into implementable logic
- Include all variables and conditions

**applies_to**
- What financial component or business process this rule affects
- Should correspond to related financial terms

**effective_period**
- When this rule is active
- Include start/end dates or triggering events

## CRITICAL DUAL EXTRACTION REQUIREMENTS

### Mandatory Dual Extraction Scenarios

**Every Complex Financial Arrangement Must Appear in Both Sections**

#### Scenario 1: Tiered Fee Structures
**Contract Language**: "82.5% of the first $500,000 of monthly revenue plus 80% of revenue above $500,000"

**Required Financial Term**:
```json
{
  "description": "Monthly tiered service fee",
  "fee_type": "tiered_fee",
  "calculation_method": "82.5% of the first $500,000 of monthly revenue plus 80% of revenue above $500,000"
}
```

**Required Pricing Rule**:
```json
{
  "rule_name": "Monthly Tiered Fee Calculation",
  "rule_type": "tiered_fee_structure",
  "calculation": "If monthly_revenue <= $500,000 then fee = monthly_revenue × 0.825, else fee = ($500,000 × 0.825) + ((monthly_revenue - $500,000) × 0.80)"
}
```

#### Scenario 2: Payment Schedules
**Contract Language**: "$150,000 paid in quarterly installments of $37,500 on January 1, April 1, July 1, and October 1"

**Required Financial Term**:
```json
{
  "description": "Annual sponsorship fee",
  "amount": {"value": "150000", "currency": "USD"},
  "payment_timing": {"due_date": "January 1, April 1, July 1, October 1"}
}
```

**Required Pricing Rule**:
```json
{
  "rule_name": "Quarterly Payment Schedule",
  "rule_type": "payment_schedule",
  "calculation": "$37,500 quarterly on Jan 1, Apr 1, Jul 1, Oct 1"
}
```

#### Scenario 3: Asset-Based Calculations
**Contract Language**: "Quarterly fee equal to Average Daily Assets × [ ] basis points ÷ 4, not to exceed [ ] per quarter"

**Required Financial Term**:
```json
{
  "description": "Quarterly asset-based management fee",
  "fee_type": "asset_based_fee",
  "calculation_method": "Average Daily Assets × [ ] basis points ÷ 4",
  "maximum_amount": {"value": "[ ]", "is_redacted": true}
}
```

**Required Pricing Rule**:
```json
{
  "rule_name": "Quarterly Asset Fee Calculation",
  "rule_type": "asset_based_fee_structure", 
  "calculation": "(Average_Daily_Assets × redacted_basis_points) ÷ 4, capped at redacted_maximum"
}
```

## SPECIAL HANDLING REQUIREMENTS

### Redaction Pattern Recognition
Identify and properly flag these redaction patterns:
- `[ ]` - Standard bracket redaction
- `$[**]` - Dollar amount redaction
- `[***]` - Multiple asterisk redaction
- `_____` - Underscore redaction
- `[REDACTED]` - Explicit redaction marker
- `###` - Hash mark redaction

### Multi-Language Document Handling
For documents containing multiple languages:
- Prioritize English text for extraction when available
- If critical information only appears in other languages, extract and note the language
- Use consistent formatting regardless of source language

### Amendment and Modification Handling
When documents contain amendments:
- Extract the final, current terms in main sections
- Note original terms and changes in extraction_notes
- Use effective dates to determine which terms are currently active
- If amendment supersedes original terms, extract the amended version

### Government Contract Specific Requirements
For government procurement documents:
- Extract procurement terms as fees
- Delivery requirements as pricing rules
- Tax/GST information in expenses
- Compliance requirements in conditions

## COMPREHENSIVE VALIDATION CHECKLIST

### Pre-Submission Validation Requirements

**Phase 1: Financial Term Completeness**
- Verify every monetary amount mentioned in the contract appears in financial_terms
- Confirm all percentage-based payments are captured
- Check that payment schedules are completely extracted
- Ensure all fee structures are documented

**Phase 2: Pricing Rule Generation**
- Confirm every complex calculation has a corresponding pricing rule
- Verify every payment schedule generates a pricing rule
- Check that all conditional payments have pricing rules
- Ensure tiered structures are converted to actionable rules

**Phase 3: Cross-Reference Accuracy**
- Match pricing rules to their corresponding financial terms
- Verify calculation consistency between sections
- Check that rule_type values align with fee_type values
- Confirm applies_to fields reference appropriate financial components

**Phase 4: Data Quality Verification**
- Verify all redacted values are properly flagged
- Confirm all dates are in consistent format
- Check that all monetary amounts preserve original language
- Ensure party information is complete and accurate

**Phase 5: Schema Compliance**
- Confirm all required fields are populated
- Verify all enum values are used correctly
- Check that all arrays contain appropriate objects
- Ensure no unexpected empty arrays exist when content should be present

### Error Prevention Guidelines

**Common Extraction Errors to Avoid**:
- Empty pricing_rules array when financial_terms contains complex arrangements
- Inconsistent redaction flagging across similar values
- Paraphrasing financial formulas instead of preserving exact language
- Missing fee caps, floors, or conditional modifiers
- Incomplete payment timing information
- Incorrect categorization of financial terms

**Quality Assurance Principles**:
- When in doubt about categorization, include detailed explanation in extraction_notes
- If information is ambiguous, note the ambiguity rather than making assumptions
- Preserve original contract language even if it seems redundant
- Cross-check extracted amounts against contract totals where possible

## CONFIDENCE SCORING METHODOLOGY

### Confidence Level Definitions

**0.9-1.0 (High Confidence)**
- All financial amounts explicitly stated with clear language
- Mathematical formulas are unambiguous and complete
- Payment schedules and timing are clearly defined
- No interpretation required for any extracted values

**0.7-0.8 (Medium-High Confidence)**
- Most financial terms are clear with minor interpretation needed
- Some calculation details require inference from context
- Payment timing may have minor ambiguities
- Redacted values are clearly marked but impact understanding

**0.5-0.6 (Medium Confidence)**
- Some financial terms require significant interpretation
- Important calculation details are missing or unclear
- Payment schedules have ambiguities or gaps
- Multiple redacted values affect comprehension

**0.3-0.4 (Low-Medium Confidence)**
- Many financial terms are unclear or incomplete
- Significant calculation details are missing
- Payment arrangements are poorly defined
- Extensive redaction impacts understanding

**0.1-0.2 (Low Confidence)**
- Financial terms are largely unclear or missing
- Cannot determine complete calculation methods
- Payment arrangements are ambiguous or contradictory
- Document quality or completeness issues affect extraction

### Confidence Documentation Requirements
Always document in extraction_notes:
- Specific areas of uncertainty or ambiguity
- Assumptions made during extraction
- Information that could not be determined from the document
- Areas where interpretation was required

## OUTPUT REQUIREMENTS

### Response Format
Respond with a single, valid JSON object conforming exactly to the ContractExtraction schema. Include no additional text, explanations, or comments outside the JSON structure.

### JSON Structure Requirements
- All required fields must be present and populated
- Use exact enum values as specified in the schema
- Ensure proper nesting and array structures
- Maintain consistent data types throughout

### Final Quality Check
Before submitting your extraction:
1. Verify JSON syntax validity
2. Confirm all schema requirements are met
3. Check that pricing_rules array is populated when financial terms exist
4. Ensure confidence score accurately reflects extraction quality
5. Confirm extraction_notes document any uncertainties or assumptions

Now proceed with analyzing the provided contract document and extracting all financial and pricing information according to these comprehensive guidelines.