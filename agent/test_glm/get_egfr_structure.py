#!/usr/bin/env python3
"""
Retrieve AlphaFold-predicted EGFR structure
"""

import requests
import json
from pathlib import Path

def get_egfr_structure():
    """Download AlphaFold EGFR structure and analyze confidence"""

    # Create output directory
    output_dir = Path("egfr_discovery_results")
    output_dir.mkdir(exist_ok=True)

    print("Retrieving AlphaFold EGFR structure...")

    # EGFR UniProt ID
    uniprot_id = "P00533"

    # Get prediction metadata
    api_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    response = requests.get(api_url)
    prediction_data = response.json()

    print(f"Found {len(prediction_data)} EGFR predictions")
    for pred in prediction_data:
        print(f"  AlphaFold ID: {pred['entryId']}")
        print(f"  Sequence length: {pred['sequenceLength']}")
        print(f"  Max pLDDT: {pred['maxPlddt']:.1f}")

    # Use the first prediction (usually the full-length protein)
    if prediction_data:
        alphafold_id = prediction_data[0]['entryId']
        print(f"\nUsing {alphafold_id} for analysis")

        # Download structure files
        version = "v4"

        # Model coordinates (mmCIF format)
        model_url = f"https://alphafold.ebi.ac.uk/files/{alphafold_id}-model_{version}.cif"
        model_response = requests.get(model_url)

        model_file = output_dir / f"{alphafold_id}_model.cif"
        with open(model_file, 'w') as f:
            f.write(model_response.text)
        print(f"Downloaded structure to: {model_file}")

        # Confidence scores
        conf_url = f"https://alphafold.ebi.ac.uk/files/{alphafold_id}-confidence_{version}.json"
        conf_response = requests.get(conf_url)
        conf_data = conf_response.json()

        conf_file = output_dir / f"{alphafold_id}_confidence.json"
        with open(conf_file, 'w') as f:
            json.dump(conf_data, f, indent=2)
        print(f"Downloaded confidence data to: {conf_file}")

        # Analyze confidence
        plddt_scores = conf_data['confidenceScore']
        avg_plddt = sum(plddt_scores) / len(plddt_scores)
        high_conf = sum(1 for s in plddt_scores if s > 90)
        very_high_conf = sum(1 for s in plddt_scores if s > 95)

        print(f"\nConfidence Analysis:")
        print(f"  Average pLDDT: {avg_plddt:.1f}")
        print(f"  High confidence residues (>90): {high_conf}/{len(plddt_scores)} ({high_conf/len(plddt_scores)*100:.1f}%)")
        print(f"  Very high confidence residues (>95): {very_high_conf}/{len(plddt_scores)} ({very_high_conf/len(plddt_scores)*100:.1f}%)")

        # Save summary
        summary = {
            'uniprot_id': uniprot_id,
            'alphafold_id': alphafold_id,
            'sequence_length': len(plddt_scores),
            'average_plddt': avg_plddt,
            'high_confidence_count': high_conf,
            'very_high_confidence_count': very_high_conf,
            'high_confidence_percentage': high_conf/len(plddt_scores)*100,
            'very_high_confidence_percentage': very_high_conf/len(plddt_scores)*100
        }

        summary_file = output_dir / "egfr_structure_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Structure summary saved to: {summary_file}")

        return summary_file
    else:
        print("No AlphaFold predictions found for EGFR")
        return None

if __name__ == "__main__":
    get_egfr_structure()