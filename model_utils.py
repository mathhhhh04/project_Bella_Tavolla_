import os
import joblib
from huggingface_hub import hf_hub_download

def load_model(
    repo_id: str,
    filename: str = "model.pkl",
    force_download: bool = False
):
    """
    [BLOCO 4] - Baixa o modelo do registry com cache inteligente automático.
    """
    token = os.environ.get("HF_TOKEN")
    
    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        force_download=force_download,
        token=token
    )
    return joblib.load(local_path)