#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  McpError,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';
import { glob } from 'glob';

const execAsync = promisify(exec);

// Helper to detect if ProofCheck is available
async function getProofCheckCommand(): Promise<string> {
  try {
    await execAsync('which proofcheck');
    return 'proofcheck';
  } catch {
    // Try Python module approach
    try {
      await execAsync('python3 --version');
      return 'python3 -m proofcheck.src';
    } catch {
      throw new Error('ProofCheck not found. Please install it first.');
    }
  }
}

// Helper to run ProofCheck commands
async function runProofCheck(args: string[]): Promise<string> {
  const cmd = await getProofCheckCommand();
  const fullCommand = `${cmd} ${args.join(' ')}`;
  
  try {
    const { stdout, stderr } = await execAsync(fullCommand, {
      timeout: 60000, // 1 minute timeout
    });
    return stdout || stderr;
  } catch (error: any) {
    throw new Error(`ProofCheck error: ${error.message}`);
  }
}

// Create the MCP server
const server = new Server(
  {
    name: 'proofcheck-mcp',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
      prompts: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'translate_latex',
      description: 'Translate LaTeX mathematical content to Lean 4 syntax',
      inputSchema: {
        type: 'object',
        properties: {
          latex_content: {
            type: 'string',
            description: 'LaTeX content to translate',
          },
          output_file: {
            type: 'string',
            description: 'Optional output file path for the Lean code',
          },
        },
        required: ['latex_content'],
      },
    },
    {
      name: 'create_lean_project',
      description: 'Create a new Lean 4 project with Lake',
      inputSchema: {
        type: 'object',
        properties: {
          project_name: {
            type: 'string',
            description: 'Name of the new Lean project',
          },
        },
        required: ['project_name'],
      },
    },
    {
      name: 'check_lean_file',
      description: 'Check a Lean file for correctness by building the project',
      inputSchema: {
        type: 'object',
        properties: {
          file_path: {
            type: 'string',
            description: 'Path to the Lean file to check',
          },
        },
        required: ['file_path'],
      },
    },
    {
      name: 'search_mathlib',
      description: 'Search Lean Mathlib for theorems and definitions',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query for Mathlib',
          },
        },
        required: ['query'],
      },
    },
    {
      name: 'list_lean_files',
      description: 'List all Lean files in a directory',
      inputSchema: {
        type: 'object',
        properties: {
          directory: {
            type: 'string',
            description: 'Directory to search for Lean files',
            default: '.',
          },
        },
      },
    },
  ],
}));

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'translate_latex': {
      const { latex_content, output_file } = args as any;
      
      // Write LaTeX to temp file
      const tempFile = `/tmp/latex_${Date.now()}.tex`;
      await fs.writeFile(tempFile, latex_content);
      
      try {
        // Run translation
        const result = await runProofCheck(['translate', tempFile]);
        
        // Read the generated Lean file
        const leanFile = tempFile.replace('.tex', '.lean');
        const leanContent = await fs.readFile(leanFile, 'utf-8');
        
        // Save to output file if specified
        if (output_file) {
          await fs.writeFile(output_file, leanContent);
        }
        
        // Clean up temp files
        await fs.unlink(tempFile).catch(() => {});
        await fs.unlink(leanFile).catch(() => {});
        
        return {
          content: [
            {
              type: 'text',
              text: `Translation successful!\n\nLean code:\n\`\`\`lean\n${leanContent}\n\`\`\``,
            },
          ],
        };
      } catch (error: any) {
        // Clean up on error
        await fs.unlink(tempFile).catch(() => {});
        throw new McpError(ErrorCode.InternalError, `Translation failed: ${error.message}`);
      }
    }

    case 'create_lean_project': {
      const { project_name } = args as any;
      
      if (!project_name || project_name.includes('/')) {
        throw new McpError(ErrorCode.InvalidParams, 'Invalid project name');
      }
      
      const result = await runProofCheck(['new', project_name]);
      
      return {
        content: [
          {
            type: 'text',
            text: `Created Lean project '${project_name}'.\n\nNext steps:\n1. cd ${project_name}\n2. Edit ${project_name}/Basic.lean\n3. Run 'lake build' to compile`,
          },
        ],
      };
    }

    case 'check_lean_file': {
      const { file_path } = args as any;
      
      // Verify file exists
      try {
        await fs.access(file_path);
      } catch {
        throw new McpError(ErrorCode.InvalidParams, `File not found: ${file_path}`);
      }
      
      const result = await runProofCheck(['check', file_path]);
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    }

    case 'search_mathlib': {
      const { query } = args as any;
      
      if (!query) {
        throw new McpError(ErrorCode.InvalidParams, 'Query is required');
      }
      
      const result = await runProofCheck(['search', query]);
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    }

    case 'list_lean_files': {
      const { directory = '.' } = args as any;
      
      try {
        const files = await glob(`${directory}/**/*.lean`, {
          ignore: ['**/lake-packages/**', '**/.lake/**'],
        });
        
        if (files.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: 'No Lean files found in the specified directory.',
              },
            ],
          };
        }
        
        return {
          content: [
            {
              type: 'text',
              text: `Found ${files.length} Lean files:\n${files.join('\n')}`,
            },
          ],
        };
      } catch (error: any) {
        throw new McpError(ErrorCode.InternalError, `Failed to list files: ${error.message}`);
      }
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }
});

// Define available resources
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: 'lean://examples',
      name: 'Example Lean Files',
      description: 'Collection of example Lean proofs and definitions',
      mimeType: 'text/plain',
    },
    {
      uri: 'lean://templates',
      name: 'Lean Templates',
      description: 'Template files for common proof patterns',
      mimeType: 'text/plain',
    },
  ],
}));

// Handle resource reading
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === 'lean://examples') {
    const examples = `-- Example 1: Basic arithmetic
theorem add_zero (n : Nat) : n + 0 = n := by
  rfl

theorem zero_add (n : Nat) : 0 + n = n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [Nat.succ_eq_add_one, ih]

-- Example 2: List operations
def reverse {α : Type} : List α → List α
  | [] => []
  | x :: xs => reverse xs ++ [x]

theorem reverse_reverse {α : Type} (xs : List α) : 
  reverse (reverse xs) = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih => sorry -- Exercise for the reader`;

    return {
      contents: [
        {
          uri,
          mimeType: 'text/plain',
          text: examples,
        },
      ],
    };
  }

  if (uri === 'lean://templates') {
    const templates = `-- Template for induction proof
theorem my_theorem (n : Nat) : P n := by
  induction n with
  | zero => 
    -- Base case
    sorry
  | succ n ih =>
    -- Inductive step
    -- ih : P n
    -- Goal: P (n + 1)
    sorry

-- Template for equality proof
theorem equality_proof (x y : α) (h : x = y) : f x = f y := by
  rw [h]

-- Template for contradiction proof
theorem by_contradiction (p : Prop) : p := by
  by_contra h
  -- h : ¬p
  -- Goal: False
  sorry`;

    return {
      contents: [
        {
          uri,
          mimeType: 'text/plain',
          text: templates,
        },
      ],
    };
  }

  throw new McpError(ErrorCode.InvalidRequest, `Unknown resource: ${uri}`);
});

// Define available prompts
server.setRequestHandler(ListPromptsRequestSchema, async () => ({
  prompts: [
    {
      name: 'formalize_statement',
      description: 'Help formalize a mathematical statement in Lean',
      arguments: [
        {
          name: 'statement',
          description: 'The mathematical statement to formalize',
          required: true,
        },
      ],
    },
    {
      name: 'prove_theorem',
      description: 'Guide through proving a theorem step by step',
      arguments: [
        {
          name: 'theorem',
          description: 'The theorem to prove',
          required: true,
        },
        {
          name: 'approach',
          description: 'Preferred proof approach (induction, contradiction, etc.)',
          required: false,
        },
      ],
    },
    {
      name: 'debug_proof',
      description: 'Help debug a failing Lean proof',
      arguments: [
        {
          name: 'code',
          description: 'The Lean code with the failing proof',
          required: true,
        },
        {
          name: 'error',
          description: 'The error message from Lean',
          required: true,
        },
      ],
    },
  ],
}));

// Handle prompt generation
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'formalize_statement': {
      const { statement } = args as any;
      return {
        description: `Formalize: ${statement}`,
        messages: [
          {
            role: 'user',
            content: {
              type: 'text',
              text: `I need help formalizing this mathematical statement in Lean 4:

"${statement}"

Please:
1. Identify the key mathematical concepts involved
2. Suggest appropriate Lean types and definitions
3. Write the formal Lean statement
4. Explain any assumptions or simplifications made`,
            },
          },
        ],
      };
    }

    case 'prove_theorem': {
      const { theorem, approach } = args as any;
      const approachText = approach ? ` using ${approach}` : '';
      
      return {
        description: `Prove: ${theorem}`,
        messages: [
          {
            role: 'user',
            content: {
              type: 'text',
              text: `I need help proving this theorem in Lean 4${approachText}:

${theorem}

Please:
1. Analyze what needs to be proven
2. Identify useful lemmas from Mathlib
3. Outline the proof strategy
4. Provide the complete Lean proof with explanations
5. Suggest alternative approaches if applicable`,
            },
          },
        ],
      };
    }

    case 'debug_proof': {
      const { code, error } = args as any;
      
      return {
        description: 'Debug Lean proof',
        messages: [
          {
            role: 'user',
            content: {
              type: 'text',
              text: `My Lean proof is failing with an error. Please help me fix it.

Code:
\`\`\`lean
${code}
\`\`\`

Error:
\`\`\`
${error}
\`\`\`

Please:
1. Explain what the error means
2. Identify the issue in the code
3. Provide a corrected version
4. Explain the fix and why it works
5. Suggest how to avoid similar errors`,
            },
          },
        ],
      };
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown prompt: ${name}`);
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('ProofCheck MCP server started');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});