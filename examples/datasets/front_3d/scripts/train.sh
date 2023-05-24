#!bash
pip install transformers
pip install datasets
pip install accelerate
pip install wandb
pip install git+https://github.com/huggingface/diffusers.git
apt install unzip
git clone https://github.com/huggingface/diffusers

export $hf_token= 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
export $wnb_token= c17faf7466a9921cb8fdb36b93d1d577615d7736

accelerate launch --mixed_precision="fp16" train_text_to_image_lora.py \
  --pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5" \
  --train_data_dir="/home/data" \
  --dataloader_num_workers=4 \
  --resolution=512 --center_crop --random_flip \
  --train_batch_size=16 \
  --gradient_accumulation_steps=4 \
  --max_train_steps=2000 \
  --learning_rate=1e-04 \
  --max_grad_norm=1 \
  --lr_scheduler="cosine" --lr_warmup_steps=0 \
  --output_dir="output" \
  --report_to=wandb \
  --checkpointing_steps=500 \
  --validation_prompt="a sagmentaion map of an orthographic view of a furnished bedroom." \
  --seed=1337