# mvp-nextjs

> Create a production-ready Next.js 15 MVP scaffold

## Quick Start

```bash
# Via Skill Controller
python skill_controller.py --execute mvp-nextjs --inputs '{"project_name": "my-app"}'

# Dry run (validation only)
python skill_controller.py --execute mvp-nextjs --inputs '{"project_name": "my-app"}' --dry-run
```

## What It Does

1. Creates Next.js 15 app with TypeScript and App Router
2. Configures Tailwind CSS 4
3. Initializes shadcn/ui with base components (button, card, input, label)
4. Creates PROJECT_CONTEXT.md for agent memory
5. Sets up .env.example
6. Initializes git with initial commit
7. Validates build passes

## Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_name` | string | Yes | - | Project name (kebab-case) |
| `target_dir` | string | No | C:/Proyectos | Parent directory |
| `include_supabase` | boolean | No | false | Add Supabase client |
| `include_auth` | boolean | No | false | Add auth boilerplate |

## Prerequisites

- **bun** - JavaScript runtime and package manager
- **git** - Version control

## Context7 Libraries

This skill automatically loads documentation for:
- `/vercel/next.js` - Next.js 15 docs
- `/tailwindlabs/tailwindcss` - Tailwind CSS 4 docs  
- `/shadcn-ui/ui` - shadcn/ui components

## Output Structure

```
{project_name}/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── ui/
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       └── label.tsx
│   └── lib/
│       └── utils.ts
├── public/
├── PROJECT_CONTEXT.md
├── .env.example
├── components.json
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Autonomy Level

**delegado** - Executes without confirmation except for the checkpoint before git init.

## Rollback

On failure, the entire project directory is removed automatically.

## Related Skills

- `feature-auth` - Add authentication after MVP created
- `deploy-vercel` - Deploy to Vercel

## Examples

### Basic MVP
```bash
python skill_controller.py --execute mvp-nextjs \
  --inputs '{"project_name": "landing-page"}'
```

### With Supabase
```bash
python skill_controller.py --execute mvp-nextjs \
  --inputs '{"project_name": "saas-app", "include_supabase": true, "include_auth": true}'
```

### Custom Directory
```bash
python skill_controller.py --execute mvp-nextjs \
  --inputs '{"project_name": "client-project", "target_dir": "D:/Clients/acme"}'
```
