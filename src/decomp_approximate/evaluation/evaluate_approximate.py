import subprocess
import sys
from pathlib import Path

ALGORITHMS = [
    "src/decomp_approximate/algorithms/ard-o0.out", 
    "src/decomp_approximate/algorithms/ard-o1.out", 
    "src/decomp_approximate/algorithms/ard-o2.out", 
    "src/decomp_approximate/algorithms/ard-o3.out", 
    "src/decomp_approximate/algorithms/ard-o4.out", 
    "src/decomp_approximate/algorithms/ard-o5.out"
]

NUMBER_OF_RUNS = 100000

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {__file__.split('/')[-1]} <test_flows_directory> <output_directory>\n"
              f"e.g. {__file__.split('/')[-1]} unique_flows/ results_approximate/")
        return
    
    if not Path(sys.argv[1]).is_dir():
        print(f"{sys.argv[1]} is not a valid directory!")
        return
    
    if not Path(sys.argv[2]).is_dir():
        print(f"Making directory {sys.argv[2]}...")
        Path(sys.argv[2]).mkdir()

    for algorithm in ALGORITHMS:
        alg_file_name = algorithm.split('/')[-1]
        if not Path(f"{sys.argv[2]}/{alg_file_name}").is_dir():
            print(f"Making directory {sys.argv[2]}/{alg_file_name}...")
            Path(f"{sys.argv[2]}/{alg_file_name}").mkdir()

    for i, file in enumerate(Path(sys.argv[1]).glob(f"*.txt")):
        for algorithm in ALGORITHMS:
            alg_file_name = algorithm.split('/')[-1]
            result: subprocess.CompletedProcess = subprocess.run([f"./{algorithm}", str(NUMBER_OF_RUNS), "1"], text=True, input=file.read_text(), capture_output=True)
            if result.stderr:
                #print(result.stdout, result.stderr)
                print(f"{sys.argv[2]}/{alg_file_name}/{file.name}\n{result.stderr}\n")
            Path(f"{sys.argv[2]}/{alg_file_name}/{file.name}").write_text(result.stdout)
            print(f'\rDone: {i+1}', end='')
        

if __name__ == "__main__":
    main()