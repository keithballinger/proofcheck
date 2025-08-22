# ProofCheck MCP Server

An MCP (Model Context Protocol) server that exposes ProofCheck's Lean proof assistant tools to AI assistants.

## Features

### Tools
- **translate_latex** - Convert LaTeX mathematical content to Lean 4
- **create_lean_project** - Create new Lean projects with Lake
- **check_lean_file** - Verify Lean proofs
- **search_mathlib** - Search for theorems in Mathlib
- **list_lean_files** - Find Lean files in a directory

### Resources
- **lean://examples** - Example Lean proofs and definitions
- **lean://templates** - Templates for common proof patterns

### Prompts
- **formalize_statement** - Help formalize mathematical statements
- **prove_theorem** - Guide through theorem proving
- **debug_proof** - Debug failing Lean proofs

## Installation

### Prerequisites
1. Install ProofCheck:
```bash
cd ../proofcheck
pip install -e .
```

2. Install Node.js dependencies:
```bash
cd mcp
npm install
npm run build
```

## Configuration

### For Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "proofcheck": {
      "command": "node",
      "args": ["/path/to/science_buddy/mcp/build/index.js"],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### For Other MCP Clients

The server communicates via stdio. Run it with:

```bash
node build/index.js
```

## Usage Examples

### With Claude Desktop

Once configured, you can ask Claude:

1. **Translate LaTeX to Lean:**
   "Can you translate this LaTeX theorem to Lean: \forall n \in \mathbb{N}, n + 0 = n"

2. **Create a new project:**
   "Create a new Lean project called 'my_proofs'"

3. **Search Mathlib:**
   "Search Mathlib for theorems about prime numbers"

4. **Check a proof:**
   "Check if my Lean file at path/to/proof.lean is correct"

5. **Use prompts:**
   "Help me formalize the statement that every even number greater than 2 can be expressed as the sum of two primes"

### Programmatic Usage

```typescript
// Example of using the MCP server programmatically
import { Client } from '@modelcontextprotocol/sdk/client/index.js';

const client = new Client({
  name: 'my-client',
  version: '1.0.0',
});

// Connect to the server
await client.connect(transport);

// Use a tool
const result = await client.callTool({
  name: 'search_mathlib',
  arguments: { query: 'prime number' }
});

// Read a resource
const examples = await client.readResource({
  uri: 'lean://examples'
});

// Get a prompt
const prompt = await client.getPrompt({
  name: 'formalize_statement',
  arguments: { statement: 'The square root of 2 is irrational' }
});
```

## Development

### Building
```bash
npm run build
```

### Watch mode
```bash
npm run dev
```

### Testing with MCP Inspector
```bash
npx @modelcontextprotocol/inspector node build/index.js
```

## Troubleshooting

### ProofCheck not found
Make sure ProofCheck is installed and in your PATH:
```bash
which proofcheck
# or
python3 -m proofcheck.src --help
```

### Permission denied
Make sure the built file is executable:
```bash
chmod +x build/index.js
```

### Claude Desktop not finding the server
1. Check the config file path is correct
2. Restart Claude Desktop after config changes
3. Check Claude Desktop logs for errors

## Architecture

The MCP server acts as a bridge between AI assistants and ProofCheck:

```
AI Assistant <-> MCP Protocol <-> ProofCheck MCP Server <-> ProofCheck CLI <-> Lean 4
```

It translates MCP tool calls into ProofCheck CLI commands and formats the results for the AI assistant.

## Contributing

To add new tools:
1. Add the tool definition in `ListToolsRequestSchema` handler
2. Implement the tool logic in `CallToolRequestSchema` handler
3. Update this README with usage examples

## License

MIT