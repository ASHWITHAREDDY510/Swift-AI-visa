from sentence_transformers import SentenceTransformer
import os

print("🔄 Downloading embedding model (200MB)...")
print("   This may take 5-10 minutes")
print()

try:
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder="C:/Users/kaswi/.cache/huggingface/hub"
    )
    
    # Test it works
    test_embedding = model.encode("Hello SwiftVisa!")
    print(f"✅ Model downloaded successfully!")
    print(f"✅ Test encoding works! Vector shape: {test_embedding.shape}")
    print(f"📁 Cache location: C:/Users/kaswi/.cache/huggingface/hub")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("💡 Try these fixes:")
    print("   1. Run PowerShell as Administrator")
    print("   2. Check disk space (need ~500MB free)")
    print("   3. Temporarily disable antivirus/firewall")
    print("   4. Try: pip install --upgrade sentence-transformers")
