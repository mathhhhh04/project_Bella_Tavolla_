from huggingface_hub import hf_hub_download
import joblib

def load_model(repo_id: str, filename: str = "model.pkl", force_download: bool = False):
    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        force_download=force_download
    )
    return joblib.load(local_path)