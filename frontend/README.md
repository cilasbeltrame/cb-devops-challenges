# How to run

1. `npm install`
2. `npm run dev`
3. go to `http://localhost:5173/`

# Files explanation

- `public` folder has the `favicon` (little icon that appears on the chrome tab)
- components go in the `src/components` folder
- `App.tsx` has all the routes
- `index.css` is only for Tailwind (styles library) initialization
- `main.tsx` is the entrypoint
- `vite-env.d.ts`, `.eslintrc.cjs`, `postcss.config.js`, `tsconfig.json`, `tsconfig.node.json`, `vite.config.ts` are config files
- `tailwind.config.js` it's were styles configuration are set
- `index.html` it's the base html the website will use (font initialization and favicon set there)