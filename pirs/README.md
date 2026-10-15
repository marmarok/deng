# Pirs: Kurdish language benchmarks for LLMs

Tasks for [Kaggle Benchmarks](https://www.kaggle.com/benchmarks) that measure how well large language models read and write Northern Kurdish (Latin script). We use them to choose the "brain" of a Kurdish voice assistant.

- `kurdish_translation_task.py`: English → Kurdish and Kurdish → English translation, scored with chrF.
- `fleurs-dev-100.csv`: sentence pairs sampled (seed 7, one per English sentence) from the validation split of [aranemini/northern-kurdish-fleurs](https://huggingface.co/datasets/aranemini/northern-kurdish-fleurs), derived from Google FLEURS, licensed CC BY 4.0.
