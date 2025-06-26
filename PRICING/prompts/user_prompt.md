# COMPREHENSIVE CONTRACT FINANCIAL EXTRACTION INSTRUCTIONS

You are tasked with extracting detailed financial and pricing information from contract documents with the highest level of precision and completeness. This extraction must be comprehensive, accurate, and structured according to the specific schema provided. Information may appear anywhere in the document - main agreement text, exhibits, amendments, schedules, appendices, or footnotes. You must analyze every page thoroughly and extract all monetary obligations, compensation structures, and pricing mechanisms.

## EXTRACTION METHODOLOGY

### Mandatory Step-by-Step Analysis Process
1. **Document Classification**: Identify the contract type and primary business relationship
2. **Complete Document Scan**: Read every page, section, exhibit, and appendix for financial content - count pages accurately
3. **Comprehensive Financial Discovery**: Locate ALL monetary amounts, percentages, calculations, payment obligations, service rates, and financial arrangements - no matter how minor
4. **Multiple-Pass Analysis**: Make at least 3 passes through the document to ensure nothing is missed
5. **Contextual Analysis**: Understand the business purpose and legal framework of each financial element
6. **Schema Mapping**: Categorize each financial element into the appropriate schema field - split complex arrangements appropriately
7. **Mandatory Pricing Rule Generation**: Create pricing rules for EVERY calculation, percentage, or conditional payment
8. **Payment Timing Extraction**: Extract detailed payment terms, due dates, and timing for ALL financial arrangements
9. **Granular Categorization**: Split expense categories, fee types, and service structures into detailed components
10. **Quality Validation**: Cross-reference extractions for consistency and completeness - verify all amounts are captured
11. **Confidence Scoring**: Assess extraction quality and note any uncertainties

### Core Extraction Principles
- **Preserve Original Language**: Extract financial terms using exact contract language without paraphrasing
- **Absolute Completeness**: Every monetary amount, percentage, calculation, or pricing structure must be captured - no exceptions
- **Aggressive Discovery**: Look for financial arrangements in schedules, exhibits, fine print, and appendices
- **Granular Categorization**: Split complex arrangements into detailed components rather than combining them
- **Mandatory Payment Timing**: Extract payment terms, due dates, and timing for ALL financial arrangements
- **Universal Pricing Rules**: Generate pricing rules for every calculation, percentage, commission, or conditional payment
- **Context Preservation**: Include surrounding business context and conditions for each financial term
- **Multi-Currency Awareness**: Handle all currencies naturally using their standard abbreviations or symbols

## MANDATORY EXTRACTION REQUIREMENTS

### CRITICAL: NO FINANCIAL ELEMENT CAN BE MISSED
You must extract every single financial arrangement mentioned in the contract, including:
- **All base compensation amounts** - salaries, payments, purchase prices, fees
- **All percentage-based arrangements** - commissions, royalties, asset-based fees
- **All conditional payments** - bonuses, penalties, milestone payments
- **All service rates** - hourly rates, per-transaction fees, subscription fees
- **All reimbursements** - expenses, cost allocations, direct charges
- **All payment timing details** - due dates, grace periods, late fees
- **All minimum/maximum amounts** - caps, floors, guaranteed minimums

### MANDATORY PRICING RULE GENERATION
Create pricing rules for EVERY financial calculation or conditional payment:
- **All percentage calculations** - even simple ones like "5% commission"
- **All tiered structures** - progressive rates, threshold-based pricing
- **All conditional payments** - performance bonuses, penalty calculations
- **All asset-based calculations** - percentage of assets, revenue sharing
- **All time-based calculations** - hourly rates, daily accruals
- **All volume-based pricing** - quantity discounts, bulk pricing

### MANDATORY PAYMENT TIMING EXTRACTION
For every fee, compensation, or payment, you MUST extract:
- **due_date**: Specific timing requirements ("within 15 days", "monthly", "upon completion")
- **grace_period**: Any additional time allowed before penalties
- **late_fees**: Penalties for delayed payment (even if just mentioned)
- **payment_method**: How payment should be made (wire, check, ACH, etc.)

### MANDATORY GRANULAR CATEGORIZATION
Split complex arrangements instead of combining them:
- **Separate expense categories** when different rules apply
- **Split fee structures** when multiple fee types are combined
- **Separate service rates** when different rates apply to different services
- **Individual commission structures** when multiple commission types exist

## DETAILED SCHEMA FIELD EXPLANATIONS

### CONTRACT METADATA SECTION

**document_title**
- Extract the exact title as it appears on the document header, cover page, or first page
- Include subtitle, version information, or amendment designations if present
- Use the most prominent or official title if multiple titles exist
- Examples: "OUTSOURCING AGREEMENT", "Master Services Agreement", "Purchase Order No. 12345"

**contract_type**
- Identify the primary legal and business relationship described in the contract
- Use descriptive terms that capture the essence of the agreement
- Examples: "Service Agreement", "Outsourcing Agreement", "Purchase Order", "Sponsorship Agreement", "Employment Agreement", "Licensing Agreement", "Partnership Agreement", "Consulting Agreement"
- If multiple agreement types are present, use the dominant or primary type

**effective_date and end_date**
- Search for explicit dates in clauses like "effective as of", "commencing", "term begins", "expires on"
- Convert to YYYY-MM-DD format when specific dates are available
- Include partial dates (month/year) when complete dates are not specified
- Look for automatic renewal clauses that might extend the end date
- Check for amendment dates that might modify the original term
- If dates are unclear or multiple dates exist, use the dates that govern the financial obligations

**parties**
- Extract ALL contracting entities mentioned in signature blocks, headers, or introductory paragraphs
- Include parent companies, subsidiaries, or affiliated entities if they have specific roles in the financial arrangements

**entity_name**: Complete legal name as it appears, including designations like Inc., LLC, Ltd., Corp.
**entity_type**: Business structure - Corporation, LLC, Partnership, Individual, Government Entity, Non-Profit, Trust, etc.
**role**: Functional role in the relationship - Service Provider, Client, Customer, Buyer, Seller, Sponsor, Contractor, Vendor, etc.
**address**: Complete address including street, city, state, zip, country
**jurisdiction**: State/country of incorporation or formation (may differ from business address)

**total_pages**: Count all pages including exhibits and appendices if explicitly stated or observable

**governing_law and jurisdiction**
- governing_law: Which state/country law applies to interpret the contract
- jurisdiction: Which courts have authority over disputes (may be different from governing law)

### FINANCIAL TERMS SECTION

This section captures all monetary obligations, compensation structures, and financial arrangements. Think carefully about the business purpose of each financial element to categorize it correctly.

#### BASE COMPENSATION
Primary payment structures representing the core financial exchange in the contract.

**description**: Clear, business-focused description of what the payment covers
- Examples: "Monthly salary for consulting services", "Annual sponsorship payment", "Purchase price for equipment"

**amount (MonetaryAmount)**:
- **value**: Extract exactly as written - specific number, formula, or descriptive amount
- **currency**: Use standard currency codes (USD, EUR, GBP, INR) or symbols (₹, $, €) as they appear
- **is_redacted**: true if value contains redaction markers like [ ], $[**], _____, [***]
- **redaction_pattern**: Exact redaction format found in document

**payment_type**: Describe the nature of the payment mechanism
- Examples: "cash payment", "wire transfer", "check payment", "equity shares", "in-kind services", "percentage of revenue", "asset-based calculation", "cryptocurrency", "credit terms"

**frequency**: Exact timing language from the contract
- Examples: "one-time", "monthly", "quarterly", "annually", "upon completion", "within 30 days", "accrued daily and payable monthly", "net 15 payment terms", "upon milestone achievement"

**calculation_method**: Mathematical formulas and calculation logic exactly as written
- Preserve complex tiered structures, asset-based calculations, percentage formulas
- Include all variables, conditions, and modifiers
- Examples: "Fixed amount per unit", "0.50% of average daily net assets", "82.5% of first $500,000 plus 80% above $500,000"

**conditions**: Requirements, triggers, or qualifications for payment
- Include performance requirements, approval processes, completion criteria
- Examples: "Subject to board approval", "Contingent upon delivery", "Performance bonus upon exceeding targets"

**payment_timing**: Detailed payment schedule and terms
- **due_date**: When payment is due (specific dates or relative timing)
- **grace_period**: Additional time allowed before penalties
- **late_fees**: Penalties for delayed payment
- **payment_method**: How payment should be made (wire, check, ACH, etc.)

#### FEES
Service fees, transaction fees, management fees, and other fee-based charges.

**description**: Specific description of what triggers or justifies the fee
**fee_type**: Nature and category of the fee
- Examples: "management fee", "service fee", "transaction fee", "commission", "penalty fee", "setup fee", "maintenance fee", "licensing fee", "tiered fee structure", "asset-based fee"

**amount**: Same structure as base compensation amount
**calculation_method**: Exact fee calculation logic and formulas
**frequency**: Payment timing using exact contract language
**applies_to**: What the fee is calculated against or applies to
**minimum_amount and maximum_amount**: Any caps or floors on fee amounts

#### ROYALTIES
Percentage-based ongoing payments tied to revenue, sales, usage, or performance.

**description**: Business purpose and scope of the royalty
**rate**: Exact percentage or rate structure as written in contract
**calculation_base**: Precise definition of what the royalty percentage applies to
- Examples: "net revenue", "gross sales", "adjusted revenues", "units sold", "licensing revenue"
**minimum_amount and maximum_amount**: Guaranteed minimums or caps
**product_scope**: What products, services, or activities generate royalties
**territory**: Geographic limitations or scope
**special_terms**: Conversion options, escalation clauses, advance arrangements

#### EQUITY COMPENSATION
Stock, shares, options, and other ownership-based compensation.

**description**: Type and purpose of equity arrangement
**instrument_type**: Specific equity instrument
- Examples: "common shares", "preferred shares", "stock options", "warrants", "convertible notes", "phantom stock"
**quantity**: Number of shares, options, or units
**share_price**: Price per share, strike price, or valuation method
**vesting_terms**: Vesting schedule, cliff periods, acceleration triggers
**conversion_rights**: Rights to convert between security types

#### EXPENSES
Reimbursements, cost allocations, and expense coverage arrangements.

**category**: Type of expense covered
- Examples: "travel expenses", "legal fees", "equipment costs", "utilities", "office space", "telecommunications"
**coverage**: Extent of reimbursement
- Examples: "full reimbursement", "50% cost sharing", "up to $10,000 annually", "direct costs only"
**amount_limit**: Maximum reimbursement amount if specified
**approval_required**: Whether pre-approval is needed
**reimbursement_terms**: Timeline, documentation requirements, restrictions

### PRICING RULES SECTION

Transform descriptive financial terms into actionable business logic that systems can implement. **MANDATORY**: Create pricing rules for every calculation, percentage, or conditional payment mentioned in the contract.

#### Mandatory Pricing Rule Creation
Generate pricing rules for ALL of the following:
- **ANY percentage calculation** - including simple "5% commission" or "3% fee"
- **Tiered or progressive structures** - multiple rates based on thresholds
- **Conditional payments** - bonuses, penalties, milestone-based payments
- **Asset-based calculations** - percentages of revenue, assets, or performance metrics
- **Time-based calculations** - daily accruals, monthly calculations, annual fees
- **Volume-based pricing** - quantity discounts, usage-based pricing
- **Payment schedules with formulas** - any calculation beyond fixed amounts
- **Commission structures** - all sales-based or performance-based payments
- **Penalty calculations** - late fees, breach penalties, liquidated damages
- **Escalation formulas** - annual increases, inflation adjustments

#### Examples of Mandatory Pricing Rules

**Simple Commission (5% of new client revenue)**
```json
{
  "rule_name": "New Client Commission Calculation",
  "rule_description": "Commission paid on revenue from new clients acquired during the contract term",
  "rule_type": "commission_structure",
  "triggers": "new client revenue collection",
  "calculation": "Commission = New_Client_Revenue × 0.05",
  "applies_to": "New Client Commission Fees",
  "effective_period": "During contract term"
}
```

**Asset-Based Fee (0.50% of assets)**
```json
{
  "rule_name": "Asset-Based Management Fee",
  "rule_type": "asset_based_fee_structure", 
  "calculation": "Monthly_Fee = (Average_Daily_Assets × 0.005) ÷ 12",
  "triggers": "monthly fee calculation based on average daily assets"
}
```

**Payment Timing Rule**
```json
{
  "rule_name": "Monthly Payment Schedule",
  "rule_type": "payment_schedule",
  "calculation": "Payment due within 15 days following month end",
  "triggers": "end of each calendar month"
}
```

Do NOT create pricing rules ONLY for:
- Simple fixed-amount purchases with no calculations ("Buy 1 heater for $3,800")
- One-time payments with no formulas or conditions

#### PricingRule Fields

**rule_name**: Short, descriptive identifier for the rule
- Examples: "Monthly Tiered Fee Calculation", "Performance Bonus Structure", "Late Payment Penalty"

**rule_description**: Complete explanation of what the rule does and when it applies
- Include business context and purpose
- Should be understandable to business users implementing the rule

**rule_type**: Category of pricing logic
- Examples: "tiered_fee_structure", "commission_structure", "penalty_structure", "asset_based_fee_structure", "payment_schedule", "escalation_structure", "volume_pricing"

**triggers**: What activates or initiates this rule
- Examples: "monthly revenue calculation", "contract milestone completion", "late payment occurrence", "annual asset valuation"

**calculation**: Exact mathematical formula or logical steps
- Convert complex contract language into implementable logic
- Include all variables, conditions, and decision points
- Examples: "If monthly_revenue <= $500,000 then fee = monthly_revenue × 0.825, else fee = ($500,000 × 0.825) + ((monthly_revenue - $500,000) × 0.80)"

**applies_to**: What financial component or business process this rule affects
- Should correspond to related financial terms
- Examples: "Monthly Management Fees", "Commission Payments", "Base Compensation"

**effective_period**: When this rule is active
- Include start/end dates or triggering events
- Examples: "During contract term", "January 1, 2024 through December 31, 2024", "Upon contract execution"

## CONTRACT TYPE SPECIFIC GUIDELINES

### Simple Procurement Contracts and Purchase Orders
- Focus on base_compensation for purchase amounts
- Include delivery terms and payment schedules in payment_timing
- Generate pricing rules only if complex calculations exist (volume discounts, tiered pricing)
- Emphasize payment terms and delivery requirements
- Use contract_type like "Purchase Order" or "Procurement Contract"

### Service Agreements and Outsourcing Contracts
- Capture complex fee structures in the fees array
- Generate detailed pricing rules for tiered, conditional, or performance-based payments
- Include service scope and performance metrics in conditions
- Document renewal and escalation terms
- Use contract_type like "Service Agreement" or "Outsourcing Agreement"

### Sponsorship and Partnership Agreements
- Extract sponsorship amounts in base_compensation
- Document deliverables and performance requirements in conditions
- Include territorial and scope limitations
- Capture renewal and escalation terms
- Use contract_type like "Sponsorship Agreement" or "Partnership Agreement"

### Asset-Based and Management Agreements
- Use fees array for percentage-based management fees
- Include detailed calculation_method for asset-based calculations
- Distinguish between accrual frequency and payment frequency
- Document asset calculation methodologies precisely
- Generate pricing rules for complex asset-based calculations

## COMMONLY MISSED FINANCIAL ELEMENTS

### Payment Timing Details (CRITICAL)
Contracts often contain payment timing that is overlooked. Look for:
- **"within X days of month end"** - extract as due_date
- **"payable monthly"** vs **"accrued daily"** - capture both frequencies
- **"net 30 terms"** - extract as payment terms
- **Grace periods** before penalties apply
- **Late fee calculations** and penalty structures
- **Payment methods** (wire transfer, check, ACH, etc.)

Example: "payable within fifteen days following the end of the applicable month"
Must capture: `"due_date": "within 15 days following month end"`

### Additional Service Rates
Look for schedules or sections mentioning:
- **Hourly rates** for additional services
- **Per-transaction fees** for extra processing
- **Setup fees** or **maintenance fees**
- **Consulting rates** or **professional services fees**
- **Overtime rates** or **expedited service charges**

### Multiple Commission Structures
Contracts often have multiple commission types:
- **Base commission** on regular business
- **New client commission** on new acquisitions
- **Performance bonuses** above targets
- **Renewal commissions** on contract extensions

### Granular Expense Categories
Split expenses when different terms apply:
- **"Allocable portion"** expenses vs **"direct cost"** expenses
- **Reimbursable** vs **non-reimbursable** expense categories
- **Pre-approval required** vs **automatic reimbursement**
- **Capped** vs **unlimited** expense categories

Example: Split these into separate ExpenseTerm objects:
- "Depreciation, systems, rent, utilities" (allocable portion)
- "Postage and telecommunications" (direct costs, full reimbursement)

### Service Level Tiers
Look for different pricing based on:
- **Service levels** (basic, premium, enterprise)
- **Volume tiers** (different rates for different quantities)
- **Time periods** (different rates over time)
- **Geographic regions** (different rates by location)

Complex financial arrangements that involve calculations, conditions, or decision logic must appear in BOTH financial_terms AND pricing_rules sections.

### Mandatory Dual Extraction Scenarios

**Tiered Fee Structures**
Contract Language: "82.5% of the first $500,000 plus 80% above $500,000"

Financial Term (in fees):
```json
{
  "description": "Monthly tiered service fee for care management",
  "fee_type": "tiered management fee", 
  "calculation_method": "82.5% of the first $500,000 of monthly revenue plus 80% of revenue above $500,000"
}
```

Pricing Rule:
```json
{
  "rule_name": "Monthly Tiered Fee Calculation",
  "rule_type": "tiered_fee_structure",
  "calculation": "If monthly_revenue <= $500,000 then fee = monthly_revenue × 0.825, else fee = ($500,000 × 0.825) + ((monthly_revenue - $500,000) × 0.80)"
}
```

**Asset-Based Calculations**
Contract Language: "0.50% of average daily net assets"

Financial Term (in fees):
```json
{
  "description": "Annual management fee based on fund assets",
  "fee_type": "asset-based management fee",
  "calculation_method": "0.50% of the Trust's average daily net assets"
}
```

Pricing Rule:
```json
{
  "rule_name": "Asset-Based Fee Calculation", 
  "rule_type": "asset_based_fee_structure",
  "calculation": "Annual fee = (sum of daily net asset values / days in year) × 0.005"
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

Set is_redacted: true and capture the exact redaction_pattern found.

### Multi-Currency Handling
For contracts containing multiple currencies:
- Use the currency as it appears in the document (USD, INR, €, £, ¥, etc.)
- Preserve original currency symbols and abbreviations
- Don't attempt currency conversion
- Note currency differences in extraction_notes if significant

### Overlapping Field Scenarios
Some financial arrangements may legitimately appear in multiple categories:

**Commission that is also Base Compensation**: If a commission represents the primary payment mechanism, include in both base_compensation and fees arrays with different descriptions focusing on the different aspects.

**Fees with Equity Components**: Performance fees paid partially in cash and partially in equity should be split appropriately.

**Expenses that are Reimbursable Fees**: Direct pass-through costs may appear in both expenses and fees depending on the business arrangement.

### Amendment and Modification Handling
When documents contain amendments:
- Extract the final, current terms in main sections
- Note original terms and changes in extraction_notes
- Use effective dates to determine which terms are currently active
- If amendment supersedes original terms, extract the amended version

## CONFIDENCE SCORING AND QUALITY ASSESSMENT

### Confidence Level Guidelines

**0.9-1.0 (Very High Confidence)**
- All financial amounts explicitly stated with clear language
- Mathematical formulas are unambiguous and complete
- Payment schedules and timing are clearly defined
- No interpretation required for any extracted values

**0.7-0.8 (High Confidence)**  
- Most financial terms are clear with minor interpretation needed
- Some calculation details require inference from context
- Payment timing may have minor ambiguities
- Redacted values are clearly marked but don't significantly impact understanding

**0.5-0.6 (Medium Confidence)**
- Some financial terms require significant interpretation
- Important calculation details are missing or unclear
- Payment schedules have ambiguities or gaps
- Multiple redacted values affect comprehension

**0.3-0.4 (Low Confidence)**
- Many financial terms are unclear or incomplete
- Significant calculation details are missing
- Payment arrangements are poorly defined
- Extensive redaction impacts understanding

**0.1-0.2 (Very Low Confidence)**
- Financial terms are largely unclear or missing
- Cannot determine complete calculation methods
- Payment arrangements are ambiguous or contradictory
- Document quality or completeness issues affect extraction

### Extraction Notes Requirements
Always document in extraction_notes:
- Specific areas of uncertainty or ambiguity
- Assumptions made during extraction
- Information that could not be determined from the document
- Areas where interpretation was required
- Cross-references between different document sections

## VALIDATION AND QUALITY CHECKS

Before finalizing your extraction, verify using this mandatory checklist:

### Completeness Verification
1. **Page Count Accuracy**: Count actual pages including exhibits - verify total_pages is correct
2. **Every Financial Amount**: Scan document again to ensure no monetary amounts are missed
3. **All Percentages Captured**: Every percentage mentioned has corresponding fee or royalty
4. **Payment Timing Complete**: Every fee/compensation has payment_timing details filled
5. **Pricing Rules Generated**: Every calculation, percentage, or conditional payment has a pricing rule
6. **Expense Categories Split**: Different expense types are separated into individual ExpenseTerm objects
7. **Service Rates Included**: All hourly rates, per-transaction fees, or service charges captured

### Specific Sykes-Type Contract Checklist
For outsourcing and service agreements, ensure you captured:
- **Main service fees** with tiered calculations
- **New client commissions** or bonuses (separate from main fees)
- **Additional service rates** (hourly, consulting, extra services)
- **Multiple expense categories** (split by reimbursement terms)
- **Payment timing details** for all fees ("within X days", "monthly", etc.)
- **Pricing rules for each** calculation including simple percentages

### Pricing Rules Completeness
Verify every financial calculation has a corresponding pricing rule:
- **Main tiered fee structure** → Tiered calculation rule
- **Commission percentages** → Commission calculation rule  
- **Asset-based percentages** → Asset calculation rule
- **Payment schedules** → Payment timing rule
- **Penalty calculations** → Penalty structure rule

### Financial Terms Array Population
Ensure no financial arrays are empty when they should contain data:
- **fees array**: Should contain ALL fee structures, commissions, service charges
- **expenses array**: Should contain ALL reimbursable categories (split appropriately)
- **base_compensation**: Should contain salaries, main payments, purchase amounts
- **pricing_rules**: Should contain rules for every calculation mentioned

### Red Flags - Re-examine Document If:
- **fees array has only 1 item** but contract mentions multiple fee types
- **pricing_rules has fewer rules** than fee calculations in financial_terms
- **payment_timing fields are empty** in any FeeTerm or BaseCompensation
- **expenses array is empty** but contract mentions reimbursements
- **total_pages seems too low** for a complex multi-page agreement

## OUTPUT REQUIREMENTS

Respond with a single, valid JSON object conforming exactly to the ContractExtraction schema. Include no additional text, explanations, or comments outside the JSON structure. Ensure all required fields are populated and all monetary values preserve the original contract language exactly as written.

For each financial element you extract, think step by step:
1. **What is the business purpose** of this payment or arrangement?
2. **Which schema category** best represents this financial arrangement?
3. **What are the exact calculation methods** and conditions?
4. **What are the specific payment timing requirements** for this arrangement?
5. **Does this require a pricing rule** for implementation? (Answer: YES for any calculation)
6. **Are there multiple components** that need to be split into separate objects?
7. **Are there overlapping aspects** that need dual representation?
8. **What is my confidence level** for this extraction?

**MANDATORY FINAL CHECK**: Before submitting, ask yourself:
- Have I extracted EVERY financial amount, percentage, and calculation in this contract?
- Does every fee and compensation have complete payment_timing details?
- Do I have pricing rules for every calculation, even simple percentages?
- Have I split complex arrangements into granular components?
- Is my page count accurate?
- Would a finance team be able to implement this contract based on my extraction?

Remember: Your goal is to create a complete, accurate, and implementable financial representation of the contract that captures every financial obligation and provides actionable business logic for systems implementation. Err on the side of including too much detail rather than missing important elements.