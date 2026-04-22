from pathlib import Path
from sc_parse import JSON_Parser

if __name__ == '__main__':
    project_root = Path(__file__).parent.parent.parent
    input_path = project_root / "original_data" / "CMeEE-V2" / "CMeEE-V2_created_test.json"
    output_path = project_root / "processed_corpus" / "Simplified_Chinese" / "cmeee_disease_only_test.json"
    JSON_Parser.process(
        input_path=input_path,
        output_path=output_path
    )