# Troubleshooting Guide - Chirality Framework
**Status Last Updated**: August 24, 2025 at 11:19h
**Note**: Always ask user for current date/time when updating status - AI doesn't have real-time access
References to "CF14" are for the Chirality Framework version 14.

## Common Issues and Solutions

### Installation Problems

#### Python Dependencies
**Problem**: `pip install -e .` fails with dependency conflicts
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions**:
```bash
# Create fresh virtual environment
python -m venv cf14-env
source cf14-env/bin/activate  # Linux/Mac
# or cf14-env\Scripts\activate  # Windows

# Update pip and setuptools
pip install --upgrade pip setuptools

# Install with specific versions
pip install openai==1.3.0 neo4j==5.14.0

# Alternative: Use conda environment
conda create -n cf14 python=3.9
conda activate cf14
pip install -e .
```

#### Missing System Dependencies
**Problem**: Neo4j connection fails
```
neo4j.exceptions.ServiceUnavailable: Could not resolve address
```

**Solutions**:
```bash
# Install Docker Desktop
# Start Neo4j container
docker run --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.18-community

# Or use Neo4j Aura cloud service
# Update NEO4J_URI in .env to cloud instance
```

### Configuration Issues

#### Environment Variables
**Problem**: OpenAI API calls fail with authentication error
```
openai.error.AuthenticationError: Invalid API key
```

**Solutions**:
```bash
# Check environment variable
echo $OPENAI_API_KEY

# Set in current session
export OPENAI_API_KEY="sk-proj-your-key-here"

# Add to .env file
echo "OPENAI_API_KEY=sk-proj-your-key-here" >> .env

# Verify API key format (should start with sk-proj- or sk-)
```

#### Neo4j Connection
**Problem**: Database connection timeout
```
neo4j.exceptions.ClientError: Unable to retrieve routing information
```

**Solutions**:
```bash
# Check Neo4j status
docker ps | grep neo4j

# Restart Neo4j container
docker restart neo4j

# Test connection manually
pip install neo4j
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
driver.verify_connectivity()
"

# Check firewall and network settings
telnet localhost 7687
```

### Semantic Operation Errors

#### Semantic Resolution Failures
**Problem**: The LLM returns responses that are nonsensical, inconsistent, or not in the correct JSON format.
```
ResolverError: OpenAI API returned non-semantic response or invalid JSON.
```

**Solutions**:
The entire system is designed for observability to handle these cases.

1.  **Use the `--verbose` flag.** This is the most powerful debugging tool. It shows you the exact output of each stage of the 3-stage pipeline, so you can pinpoint where the error is occurring (e.g., did the error happen during the initial semantic resolution, or during the final ontological lensing?).
    ```bash
    # Run a single cell computation with stage-by-stage output
    python -m chirality.cli compute-cell C --i 0 --j 0 --verbose
    ```

2.  **Test with the Echo Resolver.** The `echo` resolver bypasses the LLM entirely and returns deterministic, predictable results. This helps you verify that the pipeline mechanics and context passing are working correctly, isolating the problem to the LLM call itself.
    ```bash
    # Use the mock resolver to check the pipeline logic
    python -m chirality.cli compute-cell C --i 0 --j 0 --resolver echo
    ```

3.  **Check the `SYSTEM_PROMPT`.** The core instructions for the LLM are in `chirality/core/prompts.py`. Ensure the `SYSTEM_PROMPT` constant correctly defines the output contract and the rules for the semantic operations.

### CLI Issues

#### Command Not Found
**Problem**: `chirality` command not available.
```
bash: chirality: command not found
```

**Solutions**:
1.  **Use the module form.** This is the most reliable way to run the CLI.
    ```bash
    python3 -m chirality.cli --help
    ```
2.  **Ensure development installation.** The package must be installed in editable mode for the CLI commands to be available.
    ```bash
    # Reinstall in editable mode from the project root
    pip install -e .
    ```

### Debugging the Semantic Calculator

#### How to Trace an Operation
**Problem**: You need a complete, machine-readable log of a cell's computation.

**Solution**: Use the `--trace` flag. This will generate a detailed JSONL file in the `traces/` directory, containing a line for each stage of the pipeline with its inputs and outputs.
```bash
# This creates a file like traces/<thread_id>/C-20250828-123456.jsonl
python -m chirality.cli compute-cell C --i 0 --j 0 --trace
```

#### How to Inspect a Specific Stage
**Problem**: You want to see the input and output of just one part of the 3-stage pipeline.

**Solution**: Use the `--verbose` flag with the `compute-cell` command. It prints the results of each stage sequentially, allowing you to inspect the data as it is transformed.
```bash
# See the output of Stage 1, Stage 2, and Stage 3
python -m chirality.cli compute-cell C --i 0 --j 0 --verbose
```

#### How to Test a Change
**Problem**: You've modified the logic in `operations.py` or `cell_resolver.py` and want to verify its correctness without running a full pipeline.

**Solution**: Run the unit tests. The test suite uses a `MockCellResolver` to test the logic offline, providing fast and deterministic results.
```bash
# Run the entire test suite from the project root
pytest
```

## Getting Help


### Check Existing Issues
1. Search project issues on GitHub
2. Check TROUBLESHOOTING.md (this document) for known problems
3. Review CHANGELOG.md for recent changes
4. Review CONTINUOUS_IMPROVEMENT_PLAN.md for proposals to fix known problems

### Reporting Problems
Include:
- Chirality Framework version (`python -c "import chirality; print(chirality.__version__)"`)
- Python version (`python --version`)
- Operating system
- Complete error messages
- Steps to reproduce
- Relevant configuration (without API keys)

### Community Resources
- Project documentation
- GitHub discussions
- Example implementations
- Test cases for reference

---

*Troubleshooting guide for CF14.3.0.0 - Updated August 24, 2025*