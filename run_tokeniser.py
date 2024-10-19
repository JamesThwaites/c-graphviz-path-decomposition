from read_dotgraph_tokenise import tokenise_dot_file
from pathlib import Path
import sys

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {__file__.split('/')[-1]}.py <graphs_folder> <output_folder>\n"
              f"e.g. {__file__.split('/')[-1]}.py graphs tokenised")
        return
    
    if not Path(sys.argv[1]).is_dir():
        print(f"{sys.argv[1]} is not a valid directory!")
        return
    
    if not Path(sys.argv[2]).is_dir():
        print(f"Making directory {sys.argv[2]}...")
        Path(sys.argv[2]).mkdir()

    for file in Path(sys.argv[1]).glob(f"*.cfg.dot"):
        results = tokenise_dot_file(file)
        for cluster_name, result in results.items():
            cluster_name = cluster_name.replace("cluster_", "")
            file_name = (file.name
                         .replace("a-", "")
                         .replace(".c.015t", "")
                         .replace(".cfg.dot", f"-{cluster_name}.txt")
            )
            if result.startswith("Unsupported"):
                file_name = "_" + file_name

            elif result.startswith("Unexpected"):
                file_name = "__" + file_name
                
            Path(f"{sys.argv[2]}/{file_name}").write_text(result)

if __name__ == "__main__":
    main()