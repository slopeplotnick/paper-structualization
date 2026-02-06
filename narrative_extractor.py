"""
Narrative Structure Extractor for Academic Papers
Uses GPT-5 to extract structured narrative from economics papers
"""

import os
import json
import glob
from pathlib import Path
from openai import OpenAI

from prompts import (
    CLASSIFY_PAPER_TYPE_PROMPT,
    EXTRACT_LAYER1_PROMPT,
    EXTRACT_LAYER2_PROMPTS,
    PAPER_TYPE_NAMES,
    LAYER1_FIELD_NAMES,
    LAYER2_FIELD_NAMES
)

# API Configuration
API_BASE_URL = "https://api.chatanywhere.tech/v1"
API_KEY = "sk-T6nHXyN9FaRD2hCGdEPUMXsVpo1PVPUe7u6bKg1288HOzh70"
MODEL = "gpt-5"

# Initialize OpenAI client
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)


def load_paper(file_path: str) -> str:
    """Load paper content from markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """Call the LLM API"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert academic paper analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API call error: {e}")
        raise


def classify_paper_type(content: str) -> str:
    """Classify paper into one of 6 types"""
    # Truncate content if too long
    max_content_length = 15000
    truncated_content = content[:max_content_length] if len(content) > max_content_length else content

    prompt = CLASSIFY_PAPER_TYPE_PROMPT.format(paper_content=truncated_content)
    result = call_llm(prompt, max_tokens=50)

    # Validate result
    valid_types = ["reduced_form", "structural", "pure_theory", "experimental", "econometric", "descriptive"]
    result = result.lower().strip()

    if result not in valid_types:
        # Try to find a match
        for t in valid_types:
            if t in result:
                return t
        # Default to descriptive if can't classify
        print(f"Warning: Could not classify paper type. Got: {result}. Defaulting to 'descriptive'")
        return "descriptive"

    return result


def extract_layer1(content: str) -> dict:
    """Extract Layer 1 (universal core) structure"""
    max_content_length = 15000
    truncated_content = content[:max_content_length] if len(content) > max_content_length else content

    prompt = EXTRACT_LAYER1_PROMPT.format(paper_content=truncated_content)
    result = call_llm(prompt, max_tokens=1500)

    # Parse JSON response
    try:
        # Clean up response if needed
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]

        return json.loads(result)
    except json.JSONDecodeError as e:
        print(f"Error parsing Layer 1 JSON: {e}")
        print(f"Raw response: {result}")
        return {
            "research_question": "Error parsing response",
            "mechanism": "Error parsing response",
            "headline_result": "Error parsing response",
            "policy_implications": "Error parsing response",
            "contribution": "Error parsing response",
            "hook_motivation": "Error parsing response",
            "context_setting": "Error parsing response"
        }


def extract_layer2(content: str, paper_type: str) -> dict:
    """Extract Layer 2 (methodology-specific) structure"""
    max_content_length = 15000
    truncated_content = content[:max_content_length] if len(content) > max_content_length else content

    prompt_template = EXTRACT_LAYER2_PROMPTS.get(paper_type)
    if not prompt_template:
        return {"error": f"Unknown paper type: {paper_type}"}

    prompt = prompt_template.format(paper_content=truncated_content)
    result = call_llm(prompt, max_tokens=1500)

    # Parse JSON response
    try:
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]

        return json.loads(result)
    except json.JSONDecodeError as e:
        print(f"Error parsing Layer 2 JSON: {e}")
        print(f"Raw response: {result}")
        return {"error": "Error parsing response"}


def generate_markdown(paper_id: str, paper_type: str, layer1: dict, layer2: dict) -> str:
    """Generate markdown output from extracted structure"""
    lines = []

    lines.append(f"# {paper_id} 叙事结构分析\n")
    lines.append(f"## 论文类型: {PAPER_TYPE_NAMES.get(paper_type, paper_type)}\n")

    # Layer 1
    lines.append("## Layer 1: 通用核心\n")
    for field, value in layer1.items():
        field_name = LAYER1_FIELD_NAMES.get(field, field)
        lines.append(f"### {field_name}")
        if isinstance(value, dict):
            for k, v in value.items():
                lines.append(f"- **{k}**: {v}")
        else:
            lines.append(f"{value}\n")

    # Layer 2
    type_name = PAPER_TYPE_NAMES.get(paper_type, paper_type)
    lines.append(f"\n## Layer 2: {type_name} 特定字段\n")

    field_names = LAYER2_FIELD_NAMES.get(paper_type, {})
    for field, value in layer2.items():
        field_name = field_names.get(field, field)
        lines.append(f"### {field_name}")
        if isinstance(value, dict):
            for k, v in value.items():
                lines.append(f"- **{k}**: {v}")
        elif isinstance(value, list):
            for item in value:
                lines.append(f"- {item}")
        else:
            lines.append(f"{value}\n")

    return "\n".join(lines)


def save_outputs(result: dict, paper_id: str, output_dir: str):
    """Save JSON and Markdown outputs"""
    os.makedirs(output_dir, exist_ok=True)

    # Save JSON
    json_path = os.path.join(output_dir, f"{paper_id}_structure.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON: {json_path}")

    # Generate and save Markdown
    markdown_content = generate_markdown(
        paper_id,
        result.get("paper_type", "unknown"),
        result.get("layer1", {}),
        result.get("layer2", {})
    )
    md_path = os.path.join(output_dir, f"{paper_id}_structure.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    print(f"Saved Markdown: {md_path}")


def process_paper(paper_path: str, output_dir: str) -> dict:
    """Process a single paper"""
    paper_id = Path(paper_path).stem
    print(f"\n{'='*50}")
    print(f"Processing: {paper_id}")
    print(f"{'='*50}")

    # Load paper
    content = load_paper(paper_path)
    print(f"Loaded paper: {len(content)} characters")

    # Step 1: Classify paper type
    print("Step 1: Classifying paper type...")
    paper_type = classify_paper_type(content)
    print(f"  -> Paper type: {PAPER_TYPE_NAMES.get(paper_type, paper_type)}")

    # Step 2: Extract Layer 1
    print("Step 2: Extracting Layer 1 (universal core)...")
    layer1 = extract_layer1(content)
    print(f"  -> Extracted {len(layer1)} fields")

    # Step 3: Extract Layer 2
    print(f"Step 3: Extracting Layer 2 ({paper_type} specific)...")
    layer2 = extract_layer2(content, paper_type)
    print(f"  -> Extracted {len(layer2)} fields")

    # Combine results
    result = {
        "paper_id": paper_id,
        "paper_type": paper_type,
        "paper_type_name": PAPER_TYPE_NAMES.get(paper_type, paper_type),
        "layer1": layer1,
        "layer2": layer2
    }

    # Save outputs
    save_outputs(result, paper_id, output_dir)

    return result


def batch_process(input_dir: str, output_dir: str):
    """Batch process all papers in input directory"""
    # Find all .md files
    pattern = os.path.join(input_dir, "**", "*.md")
    paper_files = glob.glob(pattern, recursive=True)

    # Filter out non-paper files (keep only files that match paper ID pattern)
    paper_files = [f for f in paper_files if Path(f).stem.startswith("W")]

    print(f"Found {len(paper_files)} papers to process")

    results = []
    for paper_path in paper_files:
        try:
            result = process_paper(paper_path, output_dir)
            results.append(result)
        except Exception as e:
            print(f"Error processing {paper_path}: {e}")
            continue

    # Save summary
    summary_path = os.path.join(output_dir, "processing_summary.json")
    summary = {
        "total_papers": len(paper_files),
        "processed_successfully": len(results),
        "papers": [{"paper_id": r["paper_id"], "paper_type": r["paper_type"]} for r in results]
    }
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved processing summary: {summary_path}")

    return results


def main():
    """Main entry point"""
    # Get script directory
    script_dir = Path(__file__).parent

    # Set paths
    input_dir = script_dir / "test_data" / "S987654"
    output_dir = script_dir / "output"

    print("="*60)
    print("Narrative Structure Extractor")
    print("="*60)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Model: {MODEL}")
    print("="*60)

    # Process all papers
    results = batch_process(str(input_dir), str(output_dir))

    print("\n" + "="*60)
    print(f"Processing complete! Processed {len(results)} papers.")
    print(f"Results saved to: {output_dir}")
    print("="*60)


if __name__ == "__main__":
    main()
