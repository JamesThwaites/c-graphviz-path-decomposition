from read_dotgraph_tokenise import tokenise_dot_file
from pathlib import Path
import sys
from statistics import median

def main():
    if not Path(sys.argv[1]).is_dir():
        print(f"{sys.argv[1]} is not a valid directory!")
        return

    unique: set[str] = set()
    for file in Path(sys.argv[1]).glob(f"*.txt"):
        add = True
        if file.name.startswith('_'):
            continue
        data = file.read_text().split()
        token_set = set()
        for token in data:
            if token.startswith('b') or token.startswith('c'):
                continue

            if token in token_set:
                print(file.name, token)
                add = False

            token_set.add(token)

        if add:
            unique.add(' '.join(data))

    print(f"Unique flows: {len(unique)}")
    lens = [len(graph.split()) for graph in unique]
    print(f"Max size: {max(lens)}, Median: {median(lens)}")
    print(f"Average size: {sum(lens)/len(lens)}")
        

if __name__ == "__main__":
    main()