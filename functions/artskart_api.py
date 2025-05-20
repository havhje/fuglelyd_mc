import requests
import logging
# from tqdm import tqdm # tqdm might not be needed here if main is removed

# Base URL for the Artskart Public API (NEW)
ARTSKART_PUBLIC_API_BASE_URL = "https://artskart.artsdatabanken.no/publicapi/api"

# Old NorTaxa API Base URL - will be phased out if new API is sufficient
# NORTAXA_API_BASE_URL = "https://nortaxa.artsdatabanken.no/api/v1/TaxonName"


# ----------------------------------------
# NEW FUNCTION: Fetches rich taxon information from Artskart Public API by scientific name
# ----------------------------------------
def fetch_artskart_taxon_info_by_name(scientific_name_str: str) -> dict | None:
    # Fetches taxon details from Artskart Public API using the scientific name.
    # Uses GET /api/taxon?term={scientific_name_str}
    api_url = f"{ARTSKART_PUBLIC_API_BASE_URL}/taxon"
    params = {"term": scientific_name_str}

    logging.debug(f"Fetching Artskart taxon info for: '{scientific_name_str}' from {api_url} with params {params}")
    try:
        response = requests.get(api_url, params=params, timeout=15)  # Increased timeout slightly
        response.raise_for_status()  # Raise an HTTPError for bad responses (4XX or 5XX)
        results = response.json()  # This is expected to be a list of taxon objects

        if not isinstance(results, list):
            logging.warning(
                f"Unexpected API response type for '{scientific_name_str}'. Expected list, got {type(results)}."
            )
            return None

        if not results:  # Empty list means no matches found
            logging.warning(
                f"No taxon found in Artskart for scientific name: '{scientific_name_str}'. API returned empty list."
            )
            return None

        # Iterate through results to find an exact match for the scientific name.
        # BirdNET might provide a name that could match multiple results (e.g., subspecies vs species).
        # We prioritize an exact match on 'ValidScientificName'.
        for taxon_info in results:
            if isinstance(taxon_info, dict) and taxon_info.get("ValidScientificName") == scientific_name_str:
                logging.debug(
                    f"Found exact match in Artskart for '{scientific_name_str}': ID {taxon_info.get('ValidScientificNameId')}"
                )
                return taxon_info  # Return the first exact match

        # If no exact match on ValidScientificName, check ScientificNames list for an exact accepted name
        for taxon_info in results:
            if isinstance(taxon_info, dict) and "ScientificNames" in taxon_info:
                for name_entry in taxon_info["ScientificNames"]:
                    if name_entry.get("ScientificName") == scientific_name_str and name_entry.get("Accepted") is True:
                        logging.debug(
                            f"Found exact accepted match in Artskart (in ScientificNames list) for '{scientific_name_str}': ID {taxon_info.get('ValidScientificNameId')}"
                        )
                        return taxon_info

        # If still no exact match, but we have results, take the first result as a best guess.
        # This might be risky if the first result isn't the correct one.
        # Consider adding more sophisticated matching logic or confidence scoring if needed.
        if results:  # Check again if results is not empty
            first_taxon_info = results[0]
            logging.warning(
                f"No exact scientific name match for '{scientific_name_str}' in Artskart results. "
                f"Using first result: '{first_taxon_info.get('ValidScientificName')}' (ID: {first_taxon_info.get('ValidScientificNameId')}). "
                f"Original search term was '{scientific_name_str}'."
            )
            return first_taxon_info

        logging.warning(
            f"No suitable match found for '{scientific_name_str}' even after checking first result heuristics."
        )
        return None

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:  # Should ideally not happen if term always returns list
            logging.warning(f"Taxon not found (404) for scientific name: '{scientific_name_str}' using Artskart API.")
        else:
            logging.error(f"Artskart API HTTP error for '{scientific_name_str}': {e}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Artskart API request failed for '{scientific_name_str}': {e}")
        return None
    except ValueError as e:  # Includes JSONDecodeError
        logging.error(f"Failed to decode JSON from Artskart API for '{scientific_name_str}': {e}")
        return None
