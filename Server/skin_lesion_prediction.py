from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

model_id = "suinleelab/monet"
model = CLIPModel.from_pretrained(model_id).eval()
proc  = CLIPProcessor.from_pretrained(model_id)

img = Image.open("tinea_corporis.jpg").convert("RGB")
# Danh sách khái niệm/diagnosis bạn muốn kiểm tra
texts = [
  "melanoma: asymmetric dark lesion with irregular borders",
  "basal cell carcinoma: pearly papule with telangiectasia",
  "squamous cell carcinoma: hyperkeratotic scaly nodule",
  "tinea corporis: annular scaly plaque with central clearing (ringworm)",
  "psoriasis: erythematous scaly plaques on extensor surfaces",
  "eczema: pruritic eczematous patches with excoriations",
  "nevus: benign symmetric melanocytic nevus"
]

inputs = proc(text=texts, images=img, return_tensors="pt", padding=True)
with torch.no_grad():
    out = model(**inputs)
    # cosine similarities ~ CLIP: dùng logits_per_image
    sims = out.logits_per_image[0].softmax(dim=-1)

topk = torch.topk(sims, k=5)
for i in topk.indices:
    print(texts[i], float(sims[i]))
