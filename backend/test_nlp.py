#!/usr/bin/env python3
"""Test script pentru a verifica dacă NLP-ul este disponibil și funcțional"""

import sys
import os

# Adaugă directorul app la path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Test NLP Availability")
print("=" * 60)

try:
    from app.nlp_utils import (
        SEMANTIC_SIMILARITY_AVAILABLE, 
        NLP_AVAILABLE,
        get_semantic_model,
        semantic_similarity
    )
    
    print(f"\n✓ Import reușit")
    print(f"  SEMANTIC_SIMILARITY_AVAILABLE: {SEMANTIC_SIMILARITY_AVAILABLE}")
    print(f"  NLP_AVAILABLE: {NLP_AVAILABLE}")
    
    if SEMANTIC_SIMILARITY_AVAILABLE:
        print("\n" + "=" * 60)
        print("Testare încărcare model...")
        print("=" * 60)
        
        try:
            model = get_semantic_model()
            if model is not None:
                print("✓ Model încărcat cu succes")
                
                print("\n" + "=" * 60)
                print("Testare similaritate semantică...")
                print("=" * 60)
                
                test_result = semantic_similarity("test", "test")
                print(f"✓ Similaritate semantică funcționează: {test_result}")
                
                test_result2 = semantic_similarity("ontologie", "reprezentare formală a cunoștințelor")
                print(f"✓ Similaritate semantică reală: {test_result2:.2f}")
                
                print("\n" + "=" * 60)
                print("✓ NLP ESTE FUNCȚIONAL!")
                print("=" * 60)
            else:
                print("✗ Modelul nu s-a putut încărca")
                print("  Verifică dacă sentence-transformers este instalat corect")
        except Exception as e:
            print(f"✗ Eroare la încărcarea modelului: {e}")
            import traceback
            traceback.print_exc()
    elif NLP_AVAILABLE:
        print("\n✓ FuzzyWuzzy disponibil (fallback)")
        print("  Semantic similarity nu este disponibil")
        print("  Instalează: pip install sentence-transformers scikit-learn")
    else:
        print("\n✗ NLP nu este disponibil")
        print("  Instalează: pip install sentence-transformers scikit-learn fuzzywuzzy python-Levenshtein")
        
except ImportError as e:
    print(f"\n✗ Eroare la import: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"\n✗ Eroare: {e}")
    import traceback
    traceback.print_exc()

