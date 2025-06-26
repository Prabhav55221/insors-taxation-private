#!/usr/bin/env python3
"""
GPT-4o Contract Financial Extraction Tool

Extracts financial terms and pricing information from PDF contracts
using OpenAI's GPT-4o with structured output.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import argparse
import json
import os
import base64
import tempfile
import shutil
from dotenv import load_dotenv
from typing import Optional, Dict, Any

from openai import OpenAI
from pydantic import ValidationError

# Import our schema
from models.pricing import ContractExtraction, create_openai_response_format

class ContractExtractor:
    """GPT-4o based contract financial extraction"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-2024-08-06"
        
    def load_prompt(self, prompt_path: str) -> str:
        """Load prompt from markdown file"""
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        except Exception as e:
            raise Exception(f"Error loading prompt from {prompt_path}: {e}")
    
    def encode_pdf(self, pdf_path: str) -> str:
        """Encode PDF file to base64 for API"""
        try:
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            return base64.b64encode(pdf_data).decode('utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            raise Exception(f"Error reading PDF file {pdf_path}: {e}")
    
    def extract_from_pdf(self, 
                    pdf_path: str, 
                    system_prompt_path: str = "prompts/system_prompt.md",
                    user_prompt_path: str = "prompts/user_prompt.md",
                    max_retries: int = 3) -> ContractExtraction:
        """
        Extract financial information from PDF contract
        """
        
        print(f"Analyzing contract: {pdf_path}")
        
        # Load prompts
        print("Loading prompts...")
        system_prompt = self.load_prompt(system_prompt_path)
        user_prompt = self.load_prompt(user_prompt_path)
        
        # Upload PDF file first
        print("Uploading PDF...")
        
        # Case Sensitive PDF Path
        # Create a temporary file with lowercase .pdf extension
        temp_path = None
        try:
            
            if not pdf_path.lower().endswith('.pdf'):
                raise Exception(f"File must have .pdf extension: {pdf_path}")
            
            # If the original file has uppercase .PDF, create temp file with lowercase .pdf
            if pdf_path.endswith('.PDF'):
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, "contract.pdf")
                shutil.copy2(pdf_path, temp_path)
                upload_path = temp_path
            else:
                upload_path = pdf_path
            
            with open(upload_path, 'rb') as f:
                file_response = self.client.files.create(
                    file=f,
                    purpose='assistants'
                )
            
        finally:
            
            # Clean up temp file if created
            if temp_path and os.path.exists(temp_path):
                shutil.rmtree(os.path.dirname(temp_path))
        
        file_id = file_response.id
        
        # Prepare API call
        response_format = create_openai_response_format()
        
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
        
        # Call GPT-4o with retries
        for attempt in range(max_retries):
            try:
                print(f"Calling GPT-4o (attempt {attempt + 1}/{max_retries})...")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format=response_format,
                    temperature=0.1,
                    max_tokens=8192
                )
                
                # Parse response
                content = response.choices[0].message.content
                
                if not content:
                    raise Exception("Empty response from GPT-4o")
                
                # Validate against schema
                extraction_data = json.loads(content)
                extraction = ContractExtraction(**extraction_data)
                
                print("Extraction completed successfully!")
                
                # Clean up uploaded file
                try:
                    self.client.files.delete(file_id)
                except:
                    pass  # Ignore cleanup errors
                    
                return extraction
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to parse GPT-4o response as JSON after {max_retries} attempts")
                    
            except ValidationError as e:
                print(f"Schema validation error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"GPT-4o response doesn't match schema after {max_retries} attempts")
                    
            except Exception as e:
                print(f"API error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    # Clean up uploaded file on final failure
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
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
                
            print(f"Results saved to: {output_path}")
            
        except Exception as e:
            raise Exception(f"Error saving results to {output_path}: {e}")
    
    def print_summary(self, extraction: ContractExtraction) -> None:
        """Print extraction summary to console"""
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        
        # Contract basics
        metadata = extraction.contract_metadata
        print(f"Document: {metadata.document_title}")
        print(f"Type: {metadata.contract_type}")
        print(f"Period: {metadata.effective_date} → {metadata.end_date}")
        print(f"Parties: {len(metadata.parties)} entities")
        
        # Financial overview
        financial = extraction.financial_terms
        print(f"\n FINANCIAL COMPONENTS:")
        print(f"   • Base Compensation: {len(financial.base_compensation)} items")
        print(f"   • Royalties: {len(financial.royalties)} items")
        print(f"   • Fees: {len(financial.fees)} items")
        print(f"   • Equity: {len(financial.equity_compensation)} items")
        print(f"   • Expenses: {len(financial.expenses)} items")
        
        # Pricing rules
        print(f"   • Pricing Rules: {len(extraction.pricing_rules.rules)} rules")
        
        # Quality metrics
        meta = extraction.extraction_metadata
        print(f"\n QUALITY METRICS:")
        print(f"   • Overall Confidence: {meta.overall_confidence:.1%}")
        print(f"   • Redacted Fields: {meta.redacted_fields_count}")
        print(f"   • Warnings: {len(meta.processing_warnings)}")
        
        if meta.extraction_notes:
            print(f"   • Notes: {meta.extraction_notes}")


def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Extract financial terms from PDF contracts using GPT-4o",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic extraction
  python extract_contract.py contract.pdf
  
  # Save to specific output file  
  python extract_contract.py contract.pdf -o results.json
  
  # Use custom prompts
  python extract_contract.py contract.pdf --system-prompt my_system.md --user-prompt my_user.md
  
  # Quiet mode (no summary)
  python extract_contract.py contract.pdf --quiet
        """
    )
    
    # Required arguments
    parser.add_argument(
        'pdf_path',
        type=str,
        help='Path to PDF contract file'
    )
    
    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='/Users/prabhavsingh/Documents/Insors/insors-pricing/PRICING/outputs',
        help='Output JSON file path (default: {pdf_name}_extraction.json)'
    )
    
    parser.add_argument(
        '--system-prompt',
        type=str,
        default='/Users/prabhavsingh/Documents/Insors/insors-pricing/PRICING/prompts/system_prompt.md',
        help='Path to system prompt file (default: prompts/system_prompt.md)'
    )
    
    parser.add_argument(
        '--user-prompt', 
        type=str,
        default='/Users/prabhavsingh/Documents/Insors/insors-pricing/PRICING/prompts/user_prompt.md',
        help='Path to user prompt file (default: prompts/user_prompt.md)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenAI API key (default: OPENAI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--retries',
        type=int,
        default=3,
        help='Number of retry attempts on failure (default: 3)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress summary output'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.pdf_path):
        print(f" Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    if not os.path.exists(args.system_prompt):
        print(f" Error: System prompt not found: {args.system_prompt}")
        sys.exit(1)
        
    if not os.path.exists(args.user_prompt):
        print(f" Error: User prompt not found: {args.user_prompt}")
        sys.exit(1)
    
    # Check API key
    load_dotenv()
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print(" Error: OpenAI API key required. Set OPENAI_API_KEY env var or use --api-key")
        sys.exit(1)
        
    # Determine output path
    if args.output:
        if os.path.isdir(args.output):
            pdf_name = Path(args.pdf_path).stem
            output_path = os.path.join(args.output, f"{pdf_name}_extraction.json")
        else:
            output_path = args.output
    else:
        pdf_name = Path(args.pdf_path).stem
        output_path = f"outputs/{pdf_name}_extraction.json"
    
    try:
        # Initialize extractor
        extractor = ContractExtractor(api_key=api_key)
        
        # Extract from PDF
        extraction = extractor.extract_from_pdf(
            pdf_path=args.pdf_path,
            system_prompt_path=args.system_prompt,
            user_prompt_path=args.user_prompt,
            max_retries=args.retries
        )
        
        # Save results
        extractor.save_results(extraction, output_path)
        
        # Display summary
        if not args.quiet:
            extractor.print_summary(extraction)
        
        print(f"\n Contract extraction completed successfully!")
        print(f" Results: {output_path}")
        
    except KeyboardInterrupt:
        print("\n Extraction cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n Extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()