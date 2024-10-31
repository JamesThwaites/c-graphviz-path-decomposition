from read_dotgraph_tokenise import tokenise_dot_file
from pathlib import Path
import sys
from statistics import median

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {__file__.split('/')[-1]} <token_files_directory> [<output_directory>]\n"
              f"e.g. {__file__.split('/')[-1]} tokenised/ [unique_flows/]")
        return

    if not Path(sys.argv[1]).is_dir():
        print(f"{sys.argv[1]} is not a valid directory!")
        return
    
    if not Path(sys.argv[2]).is_dir():
        print(f"Making directory {sys.argv[2]}...")
        Path(sys.argv[2]).mkdir()


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

        if add and (data := ' '.join(data)) not in unique:
            unique.add(data)
            Path(f"{sys.argv[2]}/{file.name}").write_text(data)

    print(f"Unique flows: {len(unique)}")
    lens = [len(graph.split()) for graph in unique]
    print(f"Max size: {max(lens)}, Median: {median(lens)}")
    print(f"Average size: {sum(lens)/len(lens)}")
        

if __name__ == "__main__":
    main()