import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load chunked documents
df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'document_chunks.csv'))

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)
embeddings = np.array(embeddings).astype('float32')

# Create FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index and metadata
data_dir = os.path.join(os.path.dirname(__file__), '../vector_db')
faiss.write_index(index, os.path.join(data_dir, 'faiss_index.bin'))
df.to_csv(os.path.join(data_dir, 'metadata.csv'), index=False)

print(f"Stored {len(df)} embeddings in FAISS index at {data_dir}.")
