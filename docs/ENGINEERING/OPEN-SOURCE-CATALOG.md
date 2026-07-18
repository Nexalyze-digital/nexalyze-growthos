# Open Source Repository Catalog

Status: v0.2.5 foundation review

Source inspected: `D:\GitHub_Enterprise_Skills_Library\repositories`.

This catalog records relevant local repositories as references or possible dependencies. No code has been copied into GrowthOS.

## High-Priority References

| Repository | Primary Purpose | License | Technology | Possible GrowthOS Module | Integration Method | Priority | Adoption Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `vercel__next.js` | Next.js framework reference. | MIT | TypeScript, React | Frontend shell, all modules | Dependency already present and implementation reference | High | Adopted as app framework |
| `facebook__react` | React UI framework reference. | MIT | JavaScript, TypeScript | Frontend shell, all modules | Dependency already present and implementation reference | High | Adopted as UI framework |
| `tailwindlabs__tailwindcss` | Utility CSS framework. | MIT | TypeScript, CSS | Frontend UI system | Dependency already present | High | Adopted |
| `microsoft__playwright` | Browser automation and E2E testing. | Apache-2.0 | TypeScript | QA automation | Dependency candidate | High | Planned |
| `dequelabs__axe-core` | Accessibility engine. | MPL-2.0 | JavaScript | Accessibility QA | Dependency candidate | High | Planned |
| `GoogleChrome__lighthouse` | Web performance and quality audits. | Apache-2.0 | TypeScript, JavaScript | Performance validation | External tool/reference | High | Planned |
| `gitleaks__gitleaks` | Secret scanning. | MIT | Go | Security release gate | External tool | High | Planned |
| `aquasecurity__trivy` | Vulnerability and filesystem scanning. | Apache-2.0 | Go | Security release gate | External tool | High | Planned |
| `openai__openai-agents-python` | Agent SDK patterns. | MIT | Python | AI agents, Workflow Automation | Dependency candidate and implementation reference | High | Planned |
| `modelcontextprotocol__python-sdk` | MCP Python SDK. | MIT | Python | Agent tools, integrations | Dependency candidate and implementation reference | High | Planned |
| `modelcontextprotocol__typescript-sdk` | MCP TypeScript SDK. | MIT | TypeScript | Frontend or integration tools | Dependency candidate and implementation reference | High | Planned |

## AI And Workflow Platform References

| Repository | Primary Purpose | License | Technology | Possible GrowthOS Module | Integration Method | Priority | Adoption Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `langchain-ai__langchainjs` | LLM orchestration framework. | MIT | TypeScript | Research Hub, Workflow Automation | Implementation reference or dependency | Medium | Watchlist |
| `microsoft__autogen` | Multi-agent orchestration. | MIT | Python | Workflow Automation, Research Hub | Implementation reference | Medium | Watchlist |
| `FlowiseAI__Flowise` | Visual LLM workflow builder. | Apache-2.0 | TypeScript | Workflow Automation | External service/reference | Medium | Watchlist |
| `langgenius__dify` | LLM app platform. | Apache-2.0 | TypeScript, Python | AI operations, provider orchestration | External service/reference | Medium | Watchlist |
| `n8n-io__n8n` | Workflow automation platform. | Sustainable Use License | TypeScript | Workflow Automation | External service/reference only | Medium | Watchlist |
| `browser-use__browser-use` | Browser automation agents. | MIT | Python | Website Intelligence, Research Hub | Implementation reference | Medium | Watchlist |
| `microsoft__playwright-mcp` | Browser MCP server. | MIT | TypeScript | Website Intelligence | External tool/reference | Medium | Watchlist |
| `21st-dev__magic-mcp` | UI generation MCP patterns. | MIT | TypeScript | UI prototyping | Reference only | Low | Not adopted |

## SEO, Research, And Content Intelligence

| Repository | Primary Purpose | License | Technology | Possible GrowthOS Module | Integration Method | Priority | Adoption Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `google__schema-dts` | Schema.org TypeScript types. | Apache-2.0 | TypeScript | Website Intelligence, SEO/AEO/GEO | Dependency candidate | Medium | Planned |
| `garmeeh__next-seo` | SEO helpers for Next apps. | MIT | TypeScript | Public website surfaces | Implementation reference | Medium | Watchlist |
| `harlan-zw__unlighthouse` | Site crawling and Lighthouse automation. | MIT | TypeScript | Website Intelligence | External tool | Medium | Planned |
| `microsoft__markitdown` | Convert files to Markdown. | MIT | Python | Research Hub, Proposal Generator | Dependency candidate | Medium | Planned |
| `run-llama__llama_index` | Retrieval and indexing framework. | MIT | Python | Research Hub, Brand Brain | Implementation reference or dependency | Medium | Watchlist |
| `deepset-ai__haystack` | Retrieval and NLP pipelines. | Apache-2.0 | Python | Research Hub | Implementation reference | Medium | Watchlist |
| `schemaorg__schemaorg` | Schema.org vocabulary source. | Apache-2.0 | Data, docs | Website Intelligence | Reference | Low | Reference only |

## UI And Documentation References

| Repository | Primary Purpose | License | Technology | Possible GrowthOS Module | Integration Method | Priority | Adoption Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `radix-ui__primitives` | Accessible headless UI primitives. | MIT | TypeScript, React | Frontend UI system | Dependency candidate | Medium | Watchlist |
| `shadcn-ui__ui` | Component composition patterns. | MIT | TypeScript, React | Frontend UI system | Implementation reference | Medium | Reference only |
| `tailwindlabs__headlessui` | Accessible headless components. | MIT | TypeScript, React | Frontend UI system | Dependency candidate | Low | Watchlist |
| `storybookjs__storybook` | Component documentation and visual review. | MIT | TypeScript | UI system, QA | Dependency candidate | Low | Planned later |
| `facebook__docusaurus` | Documentation site framework. | MIT | TypeScript, React | Developer docs | External docs site candidate | Low | Watchlist |
| `mdx-js__mdx` | Markdown with JSX. | MIT | JavaScript | Documentation, reports | Dependency candidate | Low | Watchlist |

## Build And Code Quality References

| Repository | Primary Purpose | License | Technology | Possible GrowthOS Module | Integration Method | Priority | Adoption Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `microsoft__TypeScript` | TypeScript language. | Apache-2.0 | TypeScript | Frontend contracts | Dependency already present | High | Adopted |
| `eslint__eslint` | JavaScript/TypeScript linting. | MIT | JavaScript | Frontend quality | Dependency already present | High | Adopted |
| `prettier__prettier` | Code formatting. | MIT | JavaScript | Code quality | Dependency candidate | Medium | Planned |
| `conventional-changelog__commitlint` | Commit message validation. | MIT | JavaScript | Git workflow | Dependency candidate | Medium | Planned |
| `typicode__husky` | Git hooks. | MIT | JavaScript | Git workflow | Dependency candidate | Low | Watchlist |
| `vercel__turborepo` | Monorepo task orchestration. | MIT | TypeScript, Go | Monorepo build orchestration | Dependency candidate | Medium | Planned when packages grow |
| `nrwl__nx` | Monorepo workspace tooling. | MIT | TypeScript | Monorepo build orchestration | Reference only | Low | Watchlist |
| `evanw__esbuild` | JavaScript bundler. | MIT | Go | Build tooling | Transitive/reference | Low | Not adopted directly |
| `vitejs__vite` | Frontend tooling. | MIT | TypeScript | Tooling reference | Reference only | Low | Not adopted |

## Current Policy

- Use local repositories as references unless a dependency is explicitly approved.
- Prefer official packages from existing app frameworks before adding new libraries.
- Check license compatibility before adopting any package.
- Avoid code extraction unless the source license is compatible, attribution is documented, and the copied surface is small.
- Do not use non-permissive or source-available repositories as code sources.
