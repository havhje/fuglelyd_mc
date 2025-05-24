import pandas as pd
import os
from pathlib import Path
import argparse


def generate_sample_detections_csv(output_path, num_samples=50):
    """
    Generate a sample CSV file with bird detections for testing.
    
    Args:
        output_path: Path where the CSV file will be saved
        num_samples: Number of detection samples to generate
    """
    # Define sample data
    species_data = [
        # scientific_name, norwegian_name, redlist_status, probability of occurrence
        ('Corvus corax', 'Ravn', 'LC', 0.1),
        ('Parus major', 'Kjøttmeis', 'LC', 0.15),
        ('Erithacus rubecula', 'Rødstrupe', 'LC', 0.12),
        ('Larus canus', 'Fiskemåke', 'NT', 0.08),
        ('Falco peregrinus', 'Vandrefalk', 'VU', 0.05),
        ('Aquila chrysaetos', 'Kongeørn', 'NT', 0.06),
        ('Fratercula arctica', 'Lunde', 'VU', 0.04),
        ('Haliaeetus albicilla', 'Havørn', 'LC', 0.07),
        ('Buteo lagopus', 'Fjellvåk', 'LC', 0.09),
        ('Bubo scandiacus', 'Snøugle', 'CR', 0.02),
        ('Gavia stellata', 'Smålom', 'LC', 0.08),
        ('Gavia arctica', 'Storlom', 'VU', 0.04),
        ('Circus cyaneus', 'Myrhauk', 'EN', 0.03),
        ('Pandion haliaetus', 'Fiskeørn', 'NT', 0.05),
        ('Calidris maritima', 'Fjæreplytt', 'LC', 0.07)
    ]
    
    family_data = {
        'Corvus corax': ('Corvidae', 'Kråkefugler', 'Passeriformes', 'Spurvefugler'),
        'Parus major': ('Paridae', 'Meiser', 'Passeriformes', 'Spurvefugler'),
        'Erithacus rubecula': ('Muscicapidae', 'Fluesnappere', 'Passeriformes', 'Spurvefugler'),
        'Larus canus': ('Laridae', 'Måkefamilien', 'Charadriiformes', 'Vade-, måke- og alkefugler'),
        'Falco peregrinus': ('Falconidae', 'Falker', 'Falconiformes', 'Falkefugler'),
        'Aquila chrysaetos': ('Accipitridae', 'Haukefamilien', 'Accipitriformes', 'Haukefugler'),
        'Fratercula arctica': ('Alcidae', 'Alkefamilien', 'Charadriiformes', 'Vade-, måke- og alkefugler'),
        'Haliaeetus albicilla': ('Accipitridae', 'Haukefamilien', 'Accipitriformes', 'Haukefugler'),
        'Buteo lagopus': ('Accipitridae', 'Haukefamilien', 'Accipitriformes', 'Haukefugler'),
        'Bubo scandiacus': ('Strigidae', 'Ugler', 'Strigiformes', 'Ugler'),
        'Gavia stellata': ('Gaviidae', 'Lomfamilien', 'Gaviiformes', 'Lommer'),
        'Gavia arctica': ('Gaviidae', 'Lomfamilien', 'Gaviiformes', 'Lommer'),
        'Circus cyaneus': ('Accipitridae', 'Haukefamilien', 'Accipitriformes', 'Haukefugler'),
        'Pandion haliaetus': ('Pandionidae', 'Fiskeørnfamilien', 'Accipitriformes', 'Haukefugler'),
        'Calidris maritima': ('Scolopacidae', 'Snipefamilien', 'Charadriiformes', 'Vade-, måke- og alkefugler')
    }
    
    # Generate samples based on probability
    import random
    import numpy as np
    
    # Initialize lists for each column
    scientific_names = []
    confidences = []
    start_times = []
    end_times = []
    file_paths = []
    common_names = []
    
    # Generate random data
    for i in range(num_samples):
        # Select species based on probability
        species_idx = np.random.choice(len(species_data), p=[s[3] for s in species_data])
        species = species_data[species_idx]
        
        scientific_names.append(species[0])
        confidences.append(random.uniform(0.5, 0.99))
        start_time = random.uniform(0, 600)  # 0-10 minutes
        start_times.append(start_time)
        end_times.append(start_time + random.uniform(1, 5))  # 1-5 seconds duration
        file_paths.append(f"recording_{random.randint(1,5)}.wav")
        common_names.append(species[1])  # Use Norwegian name as common name
    
    # Create basic DataFrame
    df = pd.DataFrame({
        'scientific_name': scientific_names,
        'confidence': confidences,
        'start_time': start_times,
        'end_time': end_times,
        'audio_file': file_paths,
        'common_name': common_names
    })
    
    # Add Norwegian names and taxonomic info
    df['Species_NorwegianName'] = df['scientific_name'].apply(
        lambda x: next((s[1] for s in species_data if s[0] == x), None))
    
    df['Redlist_Status'] = df['scientific_name'].apply(
        lambda x: next((s[2] for s in species_data if s[0] == x), None))
    
    df['Family_ScientificName'] = df['scientific_name'].apply(
        lambda x: family_data.get(x, (None, None, None, None))[0])
    
    df['Family_NorwegianName'] = df['scientific_name'].apply(
        lambda x: family_data.get(x, (None, None, None, None))[1])
    
    df['Order_ScientificName'] = df['scientific_name'].apply(
        lambda x: family_data.get(x, (None, None, None, None))[2])
    
    df['Order_NorwegianName'] = df['scientific_name'].apply(
        lambda x: family_data.get(x, (None, None, None, None))[3])
    
    # Add ID columns
    df['validScientificNameId'] = range(10000, 10000 + len(df))
    df['Species_ScientificNameId'] = df['validScientificNameId']
    df['Family_ScientificNameId'] = None
    df['Order_ScientificNameId'] = None
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, sep=";", index=False)
    
    print(f"Generated sample detection data with {len(df)} records at: {output_path}")
    
    # Return stats for verification
    stats = {
        'total_samples': len(df),
        'species_counts': df['Species_NorwegianName'].value_counts().to_dict(),
        'redlist_counts': df['Redlist_Status'].value_counts().to_dict()
    }
    
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sample bird detection data for testing")
    parser.add_argument('--output', type=str, default='./test_data/sample_enriched_detections.csv',
                        help="Path to save the generated CSV file")
    parser.add_argument('--samples', type=int, default=50,
                        help="Number of detection samples to generate")
    
    args = parser.parse_args()
    
    # Generate the sample data
    stats = generate_sample_detections_csv(args.output, args.samples)
    
    # Print some stats
    print("\nSummary of generated data:")
    print(f"Total records: {stats['total_samples']}")
    
    print("\nSpecies breakdown:")
    for species, count in sorted(stats['species_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {species}: {count}")
    
    print("\nRedlist status breakdown:")
    for status, count in sorted(stats['redlist_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {status}: {count}")