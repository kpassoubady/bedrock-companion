import json
import glob
import os

base_dir = "/Users/kangs/code/github/bedrock-companion/day1/demos"
notebooks = glob.glob(f"{base_dir}/*/*.ipynb")

for nb_path in notebooks:
    with open(nb_path, "r") as f:
        data = json.load(f)
    
    nb_name = os.path.basename(nb_path)
    dir_name = os.path.basename(os.path.dirname(nb_path))
    
    colab_link = f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kpassoubady/bedrock-companion/blob/main/day1/demos/{dir_name}/{nb_name})\\n"
    
    first_cell = data["cells"][0]
    
    if first_cell["cell_type"] == "markdown":
        source = first_cell["source"]
        
        has_link = any("colab-badge.svg" in line for line in source)
        if not has_link:
            if len(source) >= 3 and source[1] == "\\n":
                source.insert(2, colab_link)
                source.insert(3, "\\n")
            else:
                source.append("\\n")
                source.append(colab_link)
            
            with open(nb_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Updated {nb_name}")
        else:
            print(f"Skipped {nb_name} (already has link)")

print("Done")
