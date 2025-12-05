"""
Generate Python gRPC code from proto files
Run this after modifying voice.proto
"""
import subprocess
import sys
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent
proto_dir = project_root / "protos"
output_dir = project_root / "src" / "grpc_generated"

# Create output directory
output_dir.mkdir(exist_ok=True)

# Generate Python code
proto_file = proto_dir / "voice.proto"

print(f"Generating gRPC code from {proto_file}...")

try:
    # Generate _pb2.py and _pb2_grpc.py files
    subprocess.run([
        sys.executable, "-m", "grpc_tools.protoc",
        f"--proto_path={proto_dir}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(proto_file)
    ], check=True)
    
    print(f"✓ Generated files in {output_dir}:")
    print(f"  - voice_pb2.py (message classes)")
    print(f"  - voice_pb2_grpc.py (service stubs)")
    
    # Create __init__.py
    init_file = output_dir / "__init__.py"
    init_file.write_text('"""Generated gRPC code"""\n')
    
    print(f"✓ Created {init_file}")
    print("\n✓ gRPC code generation complete!")

except subprocess.CalledProcessError as e:
    print(f"✗ Error generating gRPC code: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}", file=sys.stderr)
    sys.exit(1)
