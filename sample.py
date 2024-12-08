import json
import re
import argparse
from collections import defaultdict
import os

file_path = "state_of_union_speeches.json"

def get_exceptions():
    return ["Zachary Taylor", "Franklin D. Roosevelt"]

def split_into_chunks(text, num_chunks):
    words = text.split()
    chunk_size = max(1, len(words) // num_chunks)
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks[:num_chunks] 

def get_first_n_sentences(text, chunk_size=200):
    sentences = re.split(r'(?<=[.!?]) +', text)
    proper_sentence_text = ''
    current_word_count = 0
    
    for sentence in sentences:
        sentence_word_count = len(sentence.split())
        if current_word_count + sentence_word_count <= chunk_size:
            proper_sentence_text += sentence + ' '
            current_word_count += sentence_word_count
        elif current_word_count == 0:
            chunk_size += 10
            continue
        
    return proper_sentence_text.strip().capitalize()

def main(chunk_size):
    output_dir = "samples"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"samples/speech_samples_{chunk_size}.json"
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    president_speech_map = defaultdict(list)

    for speech in data:
        if speech["president"] in get_exceptions():
            continue
        if int(speech["year"]) < 1900:
            continue
        president = speech["president"]
        year = speech["year"]
        text = speech["text"]
        url = speech["url"]
        president_speech_map[president].append({"year": year, "text": text, "url": url})

    samples = []
    total_word_count = 0
    
    for president, speeches in president_speech_map.items():
        for speech in speeches:
            text = speech["text"]
            num_chunks = (int) (52 / len(speeches)) + 1
            chunks = split_into_chunks(text, num_chunks)
            
            for chunk in chunks:
                sample_text = get_first_n_sentences(chunk, chunk_size=chunk_size)
                word_count = len(sample_text.split())
                total_word_count += word_count
                
                sample = {
                    "president": president,
                    "year": speech["year"],
                    "url": speech["url"],
                    "sample": sample_text,
                    "word_count": word_count
                }
                samples.append(sample)
    
    mean_word_count = total_word_count / len(samples) if samples else 0
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(samples, file, indent=2)

    print(f"Samples saved to {output_file}.")
    print(f"Total samples: {len(samples)}.")
    print(f"Mean words per sample: {mean_word_count:.2f}.")
    print(f"Minimum words per sample: {min([sample['word_count'] for sample in samples])}.")
    print(f"Maximum words per sample: {max([sample['word_count'] for sample in samples])}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process speeches and generate samples.")
    parser.add_argument('--chunk_size', type=int, default=200, help='The chunk size for splitting text into sentences.')
    args = parser.parse_args()
    main(args.chunk_size)
